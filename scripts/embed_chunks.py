import json
import os
from sentence_transformers import SentenceTransformer
import chromadb

# ---------------- PATHS & CONSTANTS ---------------- #

CHUNKS_FILE = "data/chunks/chunks.jsonl"
CHROMA_DIR = "data/vectordb/chroma"
COLLECTION_NAME = "wayne_chunks"

# ---------------- LOAD CHUNKS ---------------- #

chunk_map = {}

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        chunk = json.loads(line)
        chunk_map[chunk["chunk_id"]] = chunk

current_chunk_ids = set(chunk_map.keys())

print(f"Loaded {len(chunk_map)} chunks from chunks.jsonl")

# ---------------- LOAD EMBEDDING MODEL ---------------- #

model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- INIT PERSISTENT CHROMA ---------------- #

os.makedirs(CHROMA_DIR, exist_ok=True)

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

# ---------------- READ EXISTING CHROMA DATA ---------------- #

existing = collection.get(include=["metadatas"])

existing_ids = set(existing.get("ids") or [])

existing_hash_map = {}
if existing.get("metadatas"):
    for meta in existing["metadatas"]:
        if meta and "chunk_id" in meta:
            existing_hash_map[meta["chunk_id"]] = meta.get("chunk_hash")

print(f"Chroma currently contains {len(existing_ids)} chunks")

# ---------------- DIFF LOGIC ---------------- #

to_add = []
to_update = []

for chunk_id, chunk in chunk_map.items():
    if chunk_id not in existing_ids:
        to_add.append(chunk)
    elif existing_hash_map.get(chunk_id) != chunk["chunk_hash"]:
        to_update.append(chunk)

print(f"Chunks to add: {len(to_add)}")
print(f"Chunks to update: {len(to_update)}")

# ---------------- ADD NEW CHUNKS (BATCH) ---------------- #

if to_add:
    texts = [chunk["text"] for chunk in to_add]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    collection.add(
        ids=[chunk["chunk_id"] for chunk in to_add],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[{
            "chunk_id": chunk["chunk_id"],
            "url": chunk["url"],
            "chunk_index": chunk["chunk_index"],
            "chunk_hash": chunk["chunk_hash"],
            "page_version": chunk["page_version"]
        } for chunk in to_add]
    )

# ---------------- UPDATE CHANGED CHUNKS (BATCH) ---------------- #

if to_update:
    texts = [chunk["text"] for chunk in to_update]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    collection.update(
        ids=[chunk["chunk_id"] for chunk in to_update],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[{
            "chunk_id": chunk["chunk_id"],
            "url": chunk["url"],
            "chunk_index": chunk["chunk_index"],
            "chunk_hash": chunk["chunk_hash"],
            "page_version": chunk["page_version"]
        } for chunk in to_update]
    )

# ---------------- DELETE STALE CHUNKS ---------------- #

stale_ids = existing_ids - current_chunk_ids

if stale_ids:
    print(f"Deleting {len(stale_ids)} stale chunks")
    collection.delete(ids=list(stale_ids))

# ---------------- FINAL STATUS ---------------- #

print("Embedding sync complete.")
print(f"Total chunks in Chroma now: {collection.count()}")