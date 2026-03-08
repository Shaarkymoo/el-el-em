import chromadb
import ollama
from pathlib import Path

client = chromadb.Client()
collection = client.get_or_create_collection("forensics_kb")

def embed(text):
    return ollama.embeddings(
        model="nomic-embed-text:v1.5",
        prompt=text
    )["embedding"]

docs = []

kb_path = Path("knowledge_base")

for file in kb_path.glob("*.md"):
    print(f"Indexing {file}...")
    text = file.read_text()

    chunks = [text[i:i+800] for i in range(0, len(text), 800)]

    for i, chunk in enumerate(chunks):
        docs.append({
            "id": f"{file.stem}_{i}",
            "text": chunk
        })

for d in docs:
    collection.add(
        ids=[d["id"]],
        documents=[d["text"]],
        embeddings=[embed(d["text"])]
    )

print("KB indexed")