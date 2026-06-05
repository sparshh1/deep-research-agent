import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path='data/chroma_db')
collection = client.get_collection(name="research_papers")
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_relevant_chunks(query, k=5):
    """
    Search the vector index for the top k most relevant text segments.
    Each result includes the text and the source arXiv ID for citations.
    """
    query_vector = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k
    )
    
    formatted_results = []
    for i in range(len(results['documents'][0])):
        formatted_results.append({
            "text": results['documents'][0][i],
            "arxiv_id": results['metadatas'][0][i]['arxiv_id']
        })
    return formatted_results