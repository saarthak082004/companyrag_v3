import uuid
import datetime
import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def store_chunks(index_name, company_name, source_file, chunks, embeddings):

    index = pc.Index(index_name)
    document_id = str(uuid.uuid4())

    vectors = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        chunk_id = f"{document_id}_chunk_{i}"

        metadata = {
            "company": company_name,
            "source": source_file,
            "document_id": document_id,
            "chunk_id": chunk_id,
            "text": chunk,
            "file_type": source_file.split(".")[-1],
            "uploaded_at": str(datetime.datetime.utcnow())
        }

        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": metadata
        })

    index.upsert(vectors=vectors)

    print(f"Stored {len(vectors)} chunks in {index_name}")