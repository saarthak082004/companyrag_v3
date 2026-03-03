# 🚀 CompanyRAG v3
## Multi-Company Retrieval Augmented Generation (RAG) System

---

## 📌 Overview

CompanyRAG v3 is a production-style Retrieval Augmented Generation (RAG) system designed to support multiple company knowledge bases using semantic vector search.

The system enables:
- 📄 PDF & DOCX document ingestion
- ✂️ Token-based intelligent chunking
- 🧠 Embedding generation using MPNet (768-dimension)
- 🗄 Vector storage using Pinecone
- 🔍 Semantic retrieval with metadata traceability

---

## 🏗 Architecture
companyrag_v3/
│
├── ingestion/
│ ├── ingest_public.py
│ ├── ingest_synise.py
│ ├── pinecone_store.py
│ └── retrieval.py
│
├── data/
│ ├── public_counsel/
│ └── synise/
│
├── .env
├── requirements.txt
└── README.md


---

## ⚙️ Tech Stack

- Python 3.10
- SentenceTransformers (`all-mpnet-base-v2`)
- Pinecone Vector Database
- LangChain TokenTextSplitter
- Tiktoken (`cl100k_base` encoding)
- python-docx / pypdf
- Conda Environment

---

## 🧠 Embedding Model

- Model: `all-mpnet-base-v2`
- Dimension: 768
- Tokenizer: `cl100k_base`
- Chunk Size: 250 tokens
- Chunk Overlap: 50 tokens

---

## 📥 Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/companyrag_v3.git
cd companyrag_v3
2️⃣ Create Conda Environment
conda create -n companyrag_v3 python=3.10
conda activate companyrag_v3
3️⃣ Install Dependencies
pip install -r requirements.txt

If requirements.txt is missing:

pip install sentence-transformers pinecone-client python-docx pypdf python-dotenv langchain-text-splitters tiktoken
4️⃣ Setup Environment Variables

Create a .env file in project root:

PINECONE_API_KEY=your_pinecone_api_key_here
📤 Ingestion
Ingest Public Counsel
cd ingestion
python ingest_public.py
Ingest Synise
cd ingestion
python ingest_synise.py

Each chunk is stored with structured metadata:

{
  "company": "...",
  "source": "...",
  "document_id": "...",
  "chunk_id": "...",
  "file_type": "...",
  "uploaded_at": "...",
  "text": "..."
}
🔍 Retrieval

Run:

python retrieval.py

Then enter:

Company Name (Synise / Public Counsel)

Your question

The system:

Converts query to embedding

Searches relevant company index

Returns top semantic matches with metadata

🎯 Features

Multi-company architecture

Auto-detect PDF / DOCX format

Token-aware chunking

Rich metadata structure

Modular ingestion design

Production-style vector pipeline

🔐 Security

Environment variables stored in .env

.gitignore prevents sensitive files from being pushed

API keys never hardcoded

📌 Future Improvements

Single-index multi-company filtering

Hybrid search (BM25 + Vector)

Reranking layer

Streamlit web interface

Hallucination control mechanism

Citation-based answer generation

👨‍💻 Author

Saarthak
B.Tech – Computer Science
RAG System

📄 License

This project is for educational and research purposes.


---

# ✅ After Saving

Push it:

```bash
git add README.md
git commit -m "Added professional README"
git push
