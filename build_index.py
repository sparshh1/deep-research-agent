import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

PARSED_DIR = 'data/parsed_text'
CHROMA_PATH = 'data/chroma_db'

print("Loading embedding model")
model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="research_papers")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1600,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

def build_index():
    files = [f for f in os.listdir(PARSED_DIR) if f.endswith('.txt')]
    print(f"Indexing {len(files)} files...")
    
    for filename in files:
        arxiv_id = filename.replace('.txt', '')
        with open(os.path.join(PARSED_DIR, filename), 'r') as f:
            text = f.read()
        
        chunks = splitter.split_text(text)
        
    
        for i, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                ids=[f"{arxiv_id}_{i}"],
                metadatas=[{"arxiv_id": arxiv_id}]
            )
    print("Indexing complete")

if __name__ == "__main__":
    if not os.path.exists(PARSED_DIR):
        print(f"Error: {PARSED_DIR} not found.")
    else:
        build_index()