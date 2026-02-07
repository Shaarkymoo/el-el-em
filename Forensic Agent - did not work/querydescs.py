import ollama

def query_ollama(prompt, model="llama3"):
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": (
                "You are a Kali Linux Machine capable of conversation with users."
                "Users may talk to you normally or may ask you to perform tasks able to be performed by a command on Kali Linux CLI."
                "You only have two kinds of replies possible, either a command or conversational sentences. You dont need to explain commands"
                "and the user cannot see them or the results, only the you and the kernel will see them. The user will only see your conversational sentences."
                "To execute a command, respond with:\n\nCALL: function_name(arguments)\n\n"
                "Once you have the result, parse them and give short answers appropriately. Also, if you recieve filepaths or strings or"
                "arguments specifically, then make sure they are not modified from your side. The only commands you currently have access to are"
                "sha256sum, cat, binwalk."
            )},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

#######works with llama3 ^^^

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

#### doesnt work with gpt-oss:20B ^^^^^^^^^^

def query_ollama(prompt, model="gpt-oss:20b"):

    url = f"http://10.160.58.217:11434/api/chat"
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
