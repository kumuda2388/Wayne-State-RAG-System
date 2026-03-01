Wayne State University Information RAG System
Overview

This project implements a fully local Retrieval-Augmented Generation (RAG) system for Wayne State University website content.

The system:
Crawls official website content via XML sitemap
Performs structured content extraction and cleaning
Implements semantic chunking
Generates embeddings using Sentence Transformers
Stores vectors in a local ChromaDB instance
Uses Ollama with Phi-3 LLM for local response generation
Provides both CLI and FastAPI + Streamlit frontend interface

The entire pipeline runs locally, with no external vector DB or cloud LLM dependency.

Pipeline Flow

Crawl Website (Sitemap-based)
Clean & Extract Text
Compute Content Hashes (SHA-256)
Chunk Content
Generate Embeddings (Sentence Transformers)
Store in ChromaDB (HNSW ANN)
Query → Embed → Retrieve Top-k
Send Context to Phi-3 (via Ollama)
Generate Grounded Response

Design Decisions & Approach
1. Crawling Strategy

Instead of depth-based crawling, I used:
XML Sitemap parsing
robots.txt validation

Why?

Prevent canonical URL duplication
Avoid unnecessary link traversal
Respect restricted paths
Ensure structured, authoritative content coverage
Only HTML pages are fetched.

2. Incremental Change Detection

To avoid redundant processing:
SHA-256 content hashes are computed
Sitemap lastmod field is tracked
Only modified pages are reprocessed
This enables efficient version tracking and incremental updates.

3. Chunking Strategy

Implemented sentence-based chunking with:
Maximum chunk size: 1000 characters
Preserved semantic boundaries
Balanced retrieval accuracy vs chunk granularity
This prevents:
Over-fragmentation
Context dilution
Token inefficiency

4. Embedding Model

Model used:
all-MiniLM-L6-v2
384-dimensional embeddings
Fast and memory-efficient
Suitable for local execution

5. Vector Database

ChromaDB (offline local mode)
Persistent local storage
HNSW-based Approximate Nearest Neighbor search
Efficient semantic similarity retrieval
No cloud services are used.

6. Local LLM Inference
LLM: Phi-3 via Ollama

Reasons:

Lightweight
Runs on 8GB MacBook Air
Fully local inference
No API costs

Query workflow:
User question → embedding generated
Top-3 chunks retrieved from ChromaDB
Context constructed
Phi-3 generates grounded response


12/22:
Today, I worked on building the Wayne State University information RAG system. I implemented web scraping using the site’s XML sitemap in combination with robots.txt to ensure that only permitted pages are crawled and that restricted paths are respected. I intentionally avoided depth-based link crawling to prevent canonical URL issues and unnecessary duplication, relying instead on sitemap-defined canonical URLs. The pipeline fetches only HTML pages, cleans and extracts textual content, and computes SHA-256 content hashes for change detection. During each crawl, all pages listed in the sitemap are checked, and the metadata is updated only when the content hash or sitemap lastmod value indicates a change, enabling reliable version tracking and efficient incremental updates.

11/29:
Today, I focused on chunking and embedding the scraped data for the Wayne State University RAG system. I implemented sentence-based chunking with a maximum chunk size of 1,000 characters to preserve semantic coherence while ensuring efficient retrieval. Embeddings were generated using the all-MiniLM-L6-v2 Sentence Transformer model, which produces 384-dimensional vectors and is widely used for fast, high-quality semantic embeddings.
For vector storage and retrieval, I used the ChromaDB offline library, configured as a local vector database rather than a cloud service. The chromadb.Client was used as the database connection and manager, enabling persistent local storage of embeddings, metadata, indexed vectors, and source text. ChromaDB leverages Approximate Nearest Neighbor (ANN) search with a Hierarchical Navigable Small World (HNSW) graph to enable efficient and fine-grained semantic retrieval of relevant chunks during query time.

source venv/bin/activate to activate environment
python scripts/crawler.py to run crawler
python scripts/chunk_pages.py to run chunking script
pip install sentence-transformers chromadb
python scripts/embed_chunks.py to run embedding model to create vectors
python scripts/ask.py to run llm
streamlit run scripts/frontend.py
future scope: to create pipeline to run just one script and everything else is in place
and memory persistent etc also future scope

for fast API
pip install fastapi uvicorn
#uvicorn is the web server
uvicorn scripts.api:app --reload #to run api api is the filename app is object inside file and --reload auto restart on changes
http://127.0.0.1:8000/docs to see swagger 


curl -fsSL https://ollama.com/install.sh | sh - to download ollama to local system or can be downloaded directly

ollama pull ph13 - pulling this model to run llm locally and since i am working on mac air 8gb this might be the best option
 /bye to exit

 3/1/2026:I am running the entire RAG pipeline locally using Ollama with the Phi-3 LLM. The system takes a user query as input, generates an embedding for the question using the same Sentence Transformer model used during indexing, and performs vector similarity search in ChromaDB to retrieve the top three most relevant chunks. These retrieved chunks are then combined into a context prompt and sent to the Phi-3 model, which generates a grounded response that is displayed to the user.


now after integrating front end and back end:

