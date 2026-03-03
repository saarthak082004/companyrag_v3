import os
import re
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from langchain_text_splitters import TokenTextSplitter

# -------------------------
# CONFIG
# -------------------------
COMPANY_NAME = "Public Counsel"
DOC_PATH = "../data/public_counsel/public_counsel_handbook.docx"
CHUNK_SIZE = 250
CHUNK_OVERLAP = 50

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv()
pinecone_key = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PUBLIC_COUNSEL_INDEX_NAME")

# -------------------------
# LOAD EMBEDDING MODEL
# -------------------------
print("Loading embedding model...")
embed_model = SentenceTransformer("all-mpnet-base-v2")

# -------------------------
# LOAD PDF
# -------------------------
def load_pdf(path):
    print("Reading PDF...")
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text

# -------------------------
# LOAD DOCX
# -------------------------
def load_docx(path):
    print("Reading DOCX...")
    doc = Document(path)
    text = ""
    for para in doc.paragraphs:
        if para.text.strip():
            text += para.text + " "
    return text

# -------------------------
# LOAD DOCUMENT (auto-detect format)
# -------------------------
def load_document(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf(path)
    elif ext == ".docx":
        return load_docx(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only .pdf and .docx are supported.")

# -------------------------
# CLEAN TEXT
# -------------------------
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# -------------------------
# SPLIT INTO CHUNKS
# -------------------------
def split_text(text):
    splitter = TokenTextSplitter(
        encoding_name="cl100k_base",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)

# -------------------------
# MAIN INGESTION
# -------------------------
def main():

    raw_text = load_document(DOC_PATH)
    cleaned_text = clean_text(raw_text)
    print(f"Total tokens (characters) in cleaned text: {len(cleaned_text)}")

    chunks = split_text(cleaned_text)
    print(f"Total chunks created: {len(chunks)}")

    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    for i, chunk in enumerate(chunks):
        token_count = len(enc.encode(chunk))
        print(f"  Chunk {i}: {token_count} tokens, {len(chunk)} chars")

    pc = Pinecone(api_key=pinecone_key)
    index = pc.Index(INDEX_NAME)

    vectors = []

    for i, chunk in enumerate(chunks):
        embedding = embed_model.encode(chunk).tolist()

        vectors.append({
            "id": f"public-{i}",
            "values": embedding,
            "metadata": {
                "text": chunk,
                "company": COMPANY_NAME
            }
        })

    index.upsert(vectors)
    print("Public Counsel ingestion complete.")

if __name__ == "__main__":
    main()