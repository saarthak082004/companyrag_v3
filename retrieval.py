import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# -------------------------
# CONFIG
# -------------------------
TOP_K = 5

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")

# -------------------------
# CONNECT TO PINECONE
# -------------------------
print("Connecting to Pinecone...")
pc = Pinecone(api_key=api_key)

# -------------------------
# COMPANY → INDEX MAP
# -------------------------
INDEX_MAP = {
    "Synise": "synise-kb",
    "Public Counsel": "publiccounsel-kb"
}

# -------------------------
# LOAD EMBEDDING MODEL
# -------------------------
print("Loading embedding model (MPNet 768)...")
model = SentenceTransformer("all-mpnet-base-v2")

# -------------------------
# SELECT COMPANY
# -------------------------
company = input("\nEnter company (Synise / Public Counsel): ").strip()

if company not in INDEX_MAP:
    raise ValueError("Company not supported.")

index_name = INDEX_MAP[company]
index = pc.Index(index_name)

# -------------------------
# TAKE USER QUESTION
# -------------------------
query = input("\nAsk your question: ")

# -------------------------
# EMBEDDING
# -------------------------
print("Converting question to embedding...")
query_vector = model.encode(query).tolist()

# -------------------------
# SEARCH IN COMPANY INDEX
# -------------------------
print(f"Searching in {index_name}... (retrieval happening here)")

results = index.query(
    vector=query_vector,
    top_k=TOP_K,
    include_metadata=True
)

# -------------------------
# HANDLE NO RESULTS
# -------------------------
if not results.get("matches"):
    print("\nNo relevant information found.")
    exit()

# -------------------------
# PROCESS RESULTS
# -------------------------
contexts_by_source = {}

for match in results["matches"]:
    metadata = match.get("metadata", {})
    source = metadata.get("source", "Unknown Source")
    text = metadata.get("text", "")
    score = match.get("score", 0)

    if source not in contexts_by_source:
        contexts_by_source[source] = []

    contexts_by_source[source].append(
        f"(Score: {score:.4f})\n{text}"
    )

# -------------------------
# PRINT CLEAN OUTPUT
# -------------------------
print("\n================ RETRIEVED CONTEXT ================\n")

final_context = ""

for source, chunks in contexts_by_source.items():
    print(f"\n SOURCE: {source}\n")
    combined = "\n\n".join(chunks)
    print(combined)
    final_context += f"\n\nSOURCE: {source}\n{combined}"

print("\n================ USER QUESTION ================\n")
print(query)

print("\n================ COMBINED CONTEXT FOR LLM ================\n")
print(final_context)
