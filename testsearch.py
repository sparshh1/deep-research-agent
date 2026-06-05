from retriever import get_relevant_chunks

results = get_relevant_chunks("what are the core components of a ReAct agent?", k=2)
for i, res in enumerate(results):
    print(f"Result {i+1} (Source: {res['arxiv_id']}):")
    print(res['text'][:200] + "...")
    print("-" * 30)