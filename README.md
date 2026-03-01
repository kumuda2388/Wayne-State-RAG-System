# Wayne State University Information RAG System

## Overview

This project implements a fully local Retrieval-Augmented Generation (RAG) system built on publicly available Wayne State University website content.

The system performs:

- Sitemap-based web crawling (XML sitemap + robots.txt validation)
- Canonical-safe content extraction
- Incremental change detection using SHA-256 hashing
- Sentence-based semantic chunking
- Embedding generation using Sentence Transformers
- Persistent vector storage using ChromaDB (HNSW ANN indexing)
- Local LLM inference using Phi-3 via Ollama
- FastAPI backend + Streamlit frontend integration

The entire pipeline runs locally without cloud vector databases or external LLM APIs.

---

# System Architecture

## End-to-End Pipeline

1. Parse XML sitemap  
2. Validate crawl permissions via robots.txt  
3. Fetch HTML pages  
4. Clean & extract textual content  
5. Compute SHA-256 content hash  
6. Perform sentence-based chunking  
7. Generate embeddings (384-dim vectors)  
8. Store embeddings in ChromaDB  
9. Embed user query  
10. Retrieve top-k relevant chunks  
11. Construct context prompt  
12. Generate grounded response using Phi-3  
13. Return answer to CLI or Web UI  

---

# Design Decisions

## 1. Sitemap-Based Crawling

Instead of depth-based crawling, this system relies on:

- XML Sitemap
- robots.txt validation

### Why?

- Prevents canonical URL duplication
- Avoids recursive link traversal issues
- Respects restricted paths
- Ensures authoritative coverage

Only HTML pages are processed.

---

## 2. Incremental Updates with Hashing

To avoid reprocessing unchanged pages:

- SHA-256 content hashes are computed
- Sitemap `lastmod` values are checked
- Pages are updated only if content changed

This enables reliable version tracking and efficient incremental indexing.

---

## 3. Chunking Strategy

- Sentence-based chunking
- Maximum chunk size: 1000 characters
- Preserves semantic coherence
- Optimized for retrieval efficiency
- Avoids over-fragmentation

---

## 4. Embedding Model

Model: `all-MiniLM-L6-v2`

- 384-dimensional vectors
- Lightweight and memory efficient
- High-quality semantic similarity
- Suitable for local execution

---

## 5. Vector Database

ChromaDB (local persistent mode)

- Approximate Nearest Neighbor (ANN)
- HNSW indexing
- Persistent local storage
- Fast semantic similarity retrieval

No cloud vector DB is used.

---

## 6. Local LLM Inference

LLM: Phi-3 via Ollama

Reasons:
- Lightweight
- Runs on 8GB MacBook Air
- Fully local
- No API costs

---

# Query Execution Flow (After Frontend & Backend Integration)

1. User submits query via CLI or Web UI  
2. Query embedding generated using same Sentence Transformer  
3. ChromaDB retrieves top 3 semantically similar chunks  
4. Retrieved chunks combined into structured context prompt  
5. Prompt sent to Phi-3 through Ollama  
6. Model generates grounded response  
7. Response returned to user  

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone <your-repository-url>
cd <project-folder>
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install sentence-transformers chromadb
pip install fastapi uvicorn
pip install streamlit
```

---

## 4. Install Ollama (Local LLM)

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull Phi-3 model:

```bash
ollama pull phi3
```

---

# Running the Pipeline

## Step 1: Crawl Website

```bash
python scripts/crawler.py
```

- Parses sitemap
- Validates robots.txt
- Computes SHA-256 hashes
- Updates only modified pages

---

## Step 2: Chunk Pages

```bash
python scripts/chunk_pages.py
```

- Sentence-based chunking
- 1000 character limit per chunk

---

## Step 3: Generate Embeddings

```bash
python scripts/embed_chunks.py
```

- Generates embeddings using all-MiniLM-L6-v2
- Stores vectors in ChromaDB

---

## Step 4: Run CLI Query

```bash
python scripts/ask.py
```

---

# Running the Web Application

## Option 1: FastAPI Backend

```bash
uvicorn scripts.api:app --reload
```

Swagger documentation available at:

```
http://127.0.0.1:8000/docs
```

---

## Option 2: Streamlit Frontend

```bash
streamlit run scripts/frontend.py
```

---

# Tech Stack

- Python
- Sentence Transformers
- ChromaDB (HNSW ANN)
- Ollama
- Phi-3 LLM
- FastAPI
- Streamlit

---

# Key Features

- Fully local RAG pipeline
- Canonical-safe sitemap crawling
- Incremental change detection with SHA-256
- Persistent local vector database
- Efficient semantic retrieval
- Local LLM inference
- Backend + frontend integration
- Modular script-based architecture

---

# Future Improvements

- Single-command unified pipeline execution
- Persistent conversational memory
- Hybrid search (BM25 + vector)
- Query expansion
- Retrieval evaluation metrics (Recall@k, MRR)
- Automatic re-chunking optimization
- Docker containerization
- Scheduled incremental crawling
- Agent-based retrieval optimization

---

# Project Status

Fully functional local RAG system with integrated backend and frontend.  
Designed for extensibility into autonomous, agent-based retrieval optimization systems.
