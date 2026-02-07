import requests
import subprocess
import re
import ollama

# --- 1. Talk to Ollama ---
import ollama

import requests

def query_ollama(prompt, model="mixtral:8x7b"):
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": (
                "You are a Kali Linux Machine capable of conversation with users."
                "Users may talk to you normally or may ask you to perform tasks able to be performed by a command on Kali Linux CLI."
                "You only have two kinds of replies possible, either a command or conversational sentences. You dont need to explain commands"
                "and the user cannot see them or the results, only you and the kernel will see them. The user will only see your conversational sentences."
                "To execute a command, respond with:\n\nCALL: function_name(arguments)\n\n"
                "Once you have the result, parse them and give short answers appropriately. Also, if you recieve filepaths or strings or"
                "arguments specifically, then make sure they are not modified from your side. The only commands you currently have access to are"
                "sha256sum, cat, binwalk."
            )},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

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
            print(tool_result)
            # Feed the result back into the LLM for parsing/answering
            followup = f"Agent: The result of {tool_name}({arg}) was:\n{tool_result}\n\n"
            print(followup)
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


