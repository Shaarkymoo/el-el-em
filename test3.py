import subprocess
import ollama
import json
from nmap_driver import nmap_scan
import os
from volat_driver import volatility_scan
from typing import List, Optional

knowledge_base_files = ["D:/Projects/el-el-em/knowledge_base/Volatility Man Page.md","D:/Projects/el-el-em/knowledge_base/Volatility Man Page.md"]
workflow_chart_path = "D:/Projects/el-el-em/knowledge_base/workflow chart.md"

def get_workflow_charts(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return str(f.read())
    else:
        print(f"⚠️ Warning: Workflow chart file not found: {file}")
        return 

def get_knowledge(filelist):
    knowledge = ""
    for filepath in filelist:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                knowledge += f.read() + "\n\n"
        else:
            print(f"⚠️ Warning: Knowledge file not found: {filepath}")
    return str(knowledge)

knowledge = get_knowledge(knowledge_base_files)
#print(knowledge[:100])  # Print the first 1000 characters of the knowledge base for verification

# --- 1. Conversation history (persistent during runtime) ---
conversation = [
    {"role": "system", "content": (
        """
        You are a Digital Forensics Analyst Assistant.
        Your purpose is to help a security analyst investigate digital evidence such as memory dumps, disk images, files, and logs. 
        The security analyst does not have CLI knowledge and relies on you to translate their plain English requests into the correct tool usage, then analyze and summarize the results for them.
        Reading the conversation is an agent which will recognise commands as long as you write them in the correct format.
        You run locally and have the CLI knowledge needed for different forensics related CLI tools.
        Your job is to understand the user's requests in plain English and translate them into the correct tool usage, then analyze and summarize the results of the tool execution for the user.

        Behavior rules:
        1. Primary Modes
        - Conversational Mode: When the user is chatting normally, respond in natural, concise, professional English.
        - Tool Call Mode: When you are asked to run or execute a system tool or command, DO NOT respond conversationally. Instead, output a single JSON object describing which tool to call and with which arguments.

        2. Tool Call Format
        - Always output JSON exactly like this when you need a tool:
            {"tool":"<tool_name>","args":["<arg1>","<arg2>", ...]}
        - No extra text, no markdown, no explanations — just the JSON.
        - <tool_name> corresponds to the known tools given in the knowledge base only. You may refer to the knowledge base as well as the workflow chart for which tools are available and their usage.
        - Arguments must be passed as a JSON array of strings exactly as received from the user. Do not modify paths or filenames. 
        - Do not add or remove arguments like flags or plugins unless specifically instructed by the user. Use only that which is necessary for the tool to run within the users request.
        - If no arguments are needed, use an empty array: {"tool":"<tool_name>","args":[]}

        3. After Tool Execution
        - Once the system returns the output of the tool, you will receive a follow-up message describing the tools result.
        - At that point, respond to the user naturally, summarizing the results in clear English. You do not need to explain the commands.
        - You may also format your answer in JSON dictionaries or key-value lists if that makes it clearer, but do not expose internal commands.

        4. Consistency & Safety
        - Do not hallucinate tools or paths; only use tools you know.
        - Do not modify file paths or command arguments provided by the user.
        - If a requested action cannot be performed, explain why in natural language.

        5. Your style
        - Be concise but informative.
        - Be accurate and factual.
        - Provide structured outputs (tables, JSON summaries, or bullet points) when summarizing complex results.

        By following these rules you act as a reliable digital forensics co-pilot.

        WORKFLOW CHARTS:
        """
        +   #+ get_workflow_charts(workflow_chart_path) +

        """

        \n \nKNOWLEDGE BASE: \n\n
        
        """ + get_knowledge(knowledge_base_files)
    )}
]

# --- 2. Query LLM with running history ---
def query_ollama(prompt, model="llama3.1:8b"):
    # Add user message to history
    conversation.append({"role": "user", "content": prompt})

    # Query LLM with full history
    response = ollama.chat(
        model=model,
        messages=conversation
    )

    # Add assistant message to history
    message = response['message']['content']
    conversation.append({"role": "assistant", "content": message})

    return message

# --- 3. Tools ---
def hash_file(filepath: str, *args: str) -> str:
    """
    Run sha256sum on a file, with optional extra CLI flags/arguments.
    Example:
        hash_file("/mnt/c/file.txt")
        hash_file("/mnt/c/file.txt", "-b")
    """
    cmd = ["wsl", "sha256sum"] + list(args) + [filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()
#can you tell me the sha256 hash of this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"   

def run_binwalk(filepath: str, *args: str) -> str:
    """
    Run binwalk on a file, with optional arguments.
    Example:
        run_binwalk("firmware.bin")
        run_binwalk("firmware.bin", "-e", "--run-as=root")
    """
    cmd = ["wsl", "binwalk"] + list(args) + [filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()
#can you run binwalk on this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"   

def cat(filepath: str, *args: str) -> str:
    """
    Run cat on a file, with optional arguments.
    Example:
        cat("/mnt/c/file.txt")
        cat("/mnt/c/file.txt", "-n")  # line numbers
    """
    cmd = ["wsl", "cat"] + list(args) + [filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()
#can you read this file "/mnt/c/Users/Shaarav/Desktop/Test.txt"

def nmap_wrapper(target: str, *options):
    # join multiple args back to a single options string if present
    options_str = " ".join(options) if options else None
    cmd, output = nmap_scan(target, options=options_str, use_wsl=True)
    return f"Command run: {' '.join(cmd)}\n\n{output}"
#can you run nmap on this target "scanme.nmap.org" with options "syn scan, ports:22,80"
#Can you run nmap on this target "scanme.nmap.org" with options "connect scan, ports 1-200, moderate speed"
#Can you run nmap on this target "scanme.nmap.org" with options "connect scan, top 100 ports, moderate speed"
#Can you run nmap on this target "scanme.nmap.org" with options "connect scan, port 80"

def volatility_wrapper(memory_file: str, *options) -> str:
    options_str = " ".join(options) if options else None
    cmd, output = volatility_scan(memory_file, options=options_str, use_wsl=True)
    return f"Command run: {' '.join(cmd)}\n\n{output}"
#can you run volatility on this memory dump "memory.dmp"

def johnTheRipper(filepath: str, *args: str) -> str:
    cmd = ["wsl", "john"] + list(args) + [filepath]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return (result.stdout + result.stderr).strip()

TOOLS = {  
    "sha256sum": hash_file,
    "binwalk": run_binwalk,
    "cat" : cat,
    "nmap": nmap_wrapper,
    "john": johnTheRipper,
    "volatility": volatility_wrapper,
}

# --- 4. Agent logic ---
def agent(user_input: str):
    response = query_ollama(user_input)

    try:
        # Try parsing JSON from model output
        data = json.loads(response.strip())
        if isinstance(data, dict) and "tool" in data and "args" in data:
            tool_name = data["tool"]
            args = data["args"]
            print("Tool call detected:", tool_name, args,"\n\n")

            if tool_name in TOOLS:
                # Run the tool
                tool_result = TOOLS[tool_name](*args)

                # Feed result back to LLM for natural reply
                followup = (
                    f"The output of {tool_name} {' '.join(args)} is:\n{tool_result}\n"
                    "Summarize this clearly for the user."
                )
                print("Follow-up to LLM:", followup,"\n\n")

                final_response = query_ollama(followup)
                return final_response
            else:
                return f"⚠️ Unknown tool requested: {tool_name}"
        else:
            return response  # Not a valid tool call, just reply
    except json.JSONDecodeError:
        return response

# --- 5. Chat loop ---
if __name__ == "__main__":
    print("🔗 LLM-OS Agent Chat (type 'exit' to quit)")
    print()
    while True:
        user_input = input("You: ")
        print()
        if user_input.lower() in ["exit", "quit"]:
            break
        reply = agent(user_input)
        print("Assistant:", reply)
        print()
