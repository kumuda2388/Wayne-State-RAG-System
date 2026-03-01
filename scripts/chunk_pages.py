import json
import os
import hashlib
from datetime import datetime, timezone

PAGES_FILE = "data/clean/pages.jsonl"
CHUNKS_FILE = "data/chunks/chunks.jsonl"


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_text(text: str, url: str, page_version: int, max_chars: int = 1000):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks = []
    current_chunk = ""
    chunk_index = 0

    for para in paragraphs:
        if len(current_chunk) + len(para) > max_chars and current_chunk:
            chunk_hash = compute_hash(current_chunk)

            chunks.append({
                "chunk_id": f"{url}::v{page_version}::chunk_{chunk_index}",
                "url": url,
                "page_version": page_version,
                "chunk_index": chunk_index,
                "chunk_hash": chunk_hash,
                "text": current_chunk.strip(),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

            chunk_index += 1
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += " "
            current_chunk += para

    if current_chunk.strip():
        chunk_hash = compute_hash(current_chunk)

        chunks.append({
            "chunk_id": f"{url}::v{page_version}::chunk_{chunk_index}",
            "url": url,
            "page_version": page_version,
            "chunk_index": chunk_index,
            "chunk_hash": chunk_hash,
            "text": current_chunk.strip(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })

    return chunks


def main():
    os.makedirs(os.path.dirname(CHUNKS_FILE), exist_ok=True)

    with open(CHUNKS_FILE, "w", encoding="utf-8") as out:
        with open(PAGES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                page = json.loads(line)

                url = page["url"]
                text = page["text"]
                page_version = page.get("version", 1)

                chunks = chunk_text(text, url, page_version)

                for chunk in chunks:
                    out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("Chunking complete.")
    print(f"Chunks written to: {CHUNKS_FILE}")


if __name__ == "__main__":
    main()