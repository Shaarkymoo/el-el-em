import requests
import subprocess
import re
import ollama

# --- 1. Talk to Ollama ---
import ollama

import requests

def query_ollama(prompt, model="gpt-oss:20b", host="localhost"):
    """
    Query an Ollama server on the specified host.

    :param prompt: The user prompt string.
    :param model: Model name on the server.
    :param host: Hostname or IP address running Ollama API.
    :return: String reply from model.
    """
    url = f"http://{host}:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an assistant that can both CHAT and EXECUTE commands. "
                    "You are NOT running in a hidden terminal. Everything you output goes into the SAME chat window. "
                    "There is no separate execution window.\n\n"

                    "=== YOUR RESPONSE RULES ===\n"
                    "1. Conversational replies: plain sentences to the user.\n\n"
                    "2. Command execution:\n"
                    "   - When a command is needed, you MUST output a line exactly in this format:\n"
                    "     CALL:function_name(arguments)\n"
                    "   - This line MUST appear in the SAME chat stream as your conversational responses.\n"
                    "   - Do NOT hide commands. Do NOT assume they run silently somewhere else.\n\n"

                    "3. After a CALL, when the agent provides the result, read it and respond in plain text summary to the user.\n\n"
                    "4. Allowed commands: sha256sum, cat, binwalk.\n"
                    "   - Never modify arguments, paths, or strings. Use them exactly as provided.\n\n"

                    "=== EXAMPLES ===\n"
                    "User: 'Please hash /tmp/file.txt'\n"
                    "You: CALL:sha256sum(/tmp/file.txt)\n\n"
                    "Agent: The hash is xyz123123123\n"
                    "You: The sha256 hash of the file /tmp/file.txt is xyz123123123.\n\n"
                    "User: 'Can you show me what's inside secret.bin?'\n"
                    "You: CALL:cat(secret.bin)\n\n"
                    "Agent: 'hello wassup'\n"
                    "You: The content of the file secret.bin is a few words, 'hello wassup'\n\n"
                )
            },
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, json=payload)
    # Make sure to check for success & parse response as needed
    response.raise_for_status()
    result = response.json()
    return result["message"]["content"]


def query_ollama(prompt, model="gpt-oss:20b"):
    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that can both CHAT and EXECUTE commands. "
                    "You are NOT running in a hidden terminal. Everything you output goes into the SAME chat window. "
                    "There is no separate execution window.\n\n"

                    "=== YOUR RESPONSE RULES ===\n"
                    "1. Conversational replies: plain sentences to the user.\n\n"
                    "2. Command execution:\n"
                    "   - When a command is needed, you MUST output a line exactly in this format:\n"
                    "     CALL:function_name(arguments)\n"
                    "   - This line MUST appear in the SAME chat stream as your conversational responses.\n"
                    "   - Do NOT hide commands. Do NOT assume they run silently somewhere else.\n\n"

                    "3. After a CALL, when the agent provides the result, read it and respond in plain text summary to the user.\n\n"

                    "4. Allowed commands: sha256sum, cat, binwalk.\n"
                    "   - Never modify arguments, paths, or strings. Use them exactly as provided.\n\n"

                    "=== EXAMPLES ===\n"
                    "User: 'Please hash /tmp/file.txt'\n"
                    "You: CALL:sha256sum(/tmp/file.txt)\n\n"
                    "Agent: The hash is xyz123123123\n"
                    "You: The sha256 hash of the file /tmp/file.txt is xyz123123123.\n\n"
                    "User: 'Can you show me what's inside secret.bin?'\n"
                    "You: CALL:cat(secret.bin)\n\n"
                    "Agent: 'hello wassup'\n"
                    "You: The content of the file secret.bin is a few words, 'hello wassup'\n\n"
                )
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]


def hash_file(filepath: str) -> str:
    cmd = ["wsl", "sha256sum", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()
#can you tell me the sha256 hash of this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"   

def run_binwalk(filepath: str) -> str:
    cmd = ["wsl", "binwalk", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def cat(filepath: str) -> str:
    cmd = ["wsl", "cat", filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

TOOLS = {  
    "sha256sum": hash_file,
    "binwalk": run_binwalk,
    "cat" : cat
}

# --- 3. Agent that catches CALLs ---
def agent(user_input: str):
    # Ask the LLM what to do
    response = query_ollama(user_input)

    # Check for CALL pattern
    match = re.search(r'CALL:\s(\w+)\s(.+)', response)
    if match:
        print("Assistant:",response,"(command caught)")
        tool_name, arg = match.groups()
        arg = arg.strip('"').strip("'")  # clean quotes

        if tool_name in TOOLS:
            tool_result = TOOLS[tool_name](arg)
            #print(tool_result)
            # Feed the result back into the LLM for parsing/answering
            followup = f"Agent: The result of {tool_name}({arg}) was:\n{tool_result}\n\n"
            #print(followup)
            final_response = query_ollama(followup)
            return final_response
        else:
            return f"Unknown tool: {tool_name}"
    else:
        print("no command caught")
        return response

# --- 4. Chat loop in terminal ---
if __name__ == "__main__":
    print("🔗 LLM-OS Agent Chat (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        reply = agent(user_input)
        print("Assistant:", reply)


