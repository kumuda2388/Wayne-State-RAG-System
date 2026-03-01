import chromadb
from sentence_transformers import SentenceTransformer
import requests

# ---------------- PATHS & CONSTANTS ---------------- #

CHROMA_DIR = "data/vectordb/chroma"
COLLECTION_NAME = "wayne_chunks"
OLLAMA_URL = "http://localhost:11434/api/generate"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(COLLECTION_NAME)

print(f"Chroma contains {collection.count()} chunks.")


def ask_question(question: str) -> str:
    question_embedding = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
    )

    retrieved_chunks = results["documents"][0]
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""
You are an assistant answering questions about Wayne State University.

Use ONLY the context provided below.
If the answer is not in the context, say "I don't know."

Context:
---------
{context}
---------

Question:
{question}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


# Optional: Keep CLI mode working
if __name__ == "__main__":
    question = input("\nAsk a question about Wayne State University:\n> ")
    answer = ask_question(question)
    print("\nAnswer:\n")
    print(answer)