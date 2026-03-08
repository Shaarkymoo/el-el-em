import subprocess

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


##https://github.com/CyberAlbSecOP/Awesome_GPT_Super_Prompting/tree/main

# https://github.com/yueliu1999/Awesome-Jailbreak-on-LLMs

# https://github.com/Techiral/awesome-llm-jailbreaks

# https://github.com/tuxsharxsec/Jailbreaks

# https://github.com/BirdsAreFlyingCameras/GPT-5_Jailbreak_PoC

# nmap, 