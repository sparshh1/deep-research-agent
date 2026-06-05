import os
import json
import time

from agent import run_research_agent 

os.makedirs('predictions', exist_ok=True)

CONFIGS = {
    "full_agent":      {"use_planner": True,  "use_reflector": True,  "use_verifier": True},
    "baseline":        {"use_planner": False, "use_reflector": False, "use_verifier": False},
    "no_planner":      {"use_planner": False, "use_reflector": True,  "use_verifier": True},
    "no_reflector":    {"use_planner": True,  "use_reflector": False, "use_verifier": True},
    "no_verifier":     {"use_planner": True,  "use_reflector": True,  "use_verifier": False}

}
def load_eval_questions(filepath='eval/questions.jsonl'):
    questions = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions

def run_evaluation():
    questions = load_eval_questions()
    print(f"Loaded {len(questions)} evaluation questions.")
    
    for config_name, settings in CONFIGS.items():
        print(f"\n🚀 STARTING RUN: {config_name.upper()}")
        print(f"Settings: {settings}")
        
        results = []
        output_file = f'predictions/{config_name}.jsonl'
        
        if os.path.exists(output_file):
            print(f"Skipping {config_name} - output file already exists.")
            continue
            
        for i, q in enumerate(questions):
            print(f"  [{config_name}] Processing Q{i+1}/{len(questions)}: {q['id']}")
            
            start_time = time.time()
            try:
                answer = run_research_agent(q['question'], settings)
                
                import re
                cited_ids = re.findall(r'\[arXiv:([0-9]+\.[0-9]+v?[0-9]*)\]', answer)
                
            except Exception as e:
                print(f"    Error on Q{q['id']}: {e}")
                answer = f"ERROR: {str(e)}"
                cited_ids = []

            latency = time.time() - start_time
            
            results.append({
                "question_id": q['id'],
                "answer": answer,
                "cited_arxiv_ids": list(set(cited_ids)), 
                "latency_seconds": round(latency, 2)
            })
            
            time.sleep(4) 
            
        print(f"Finished {config_name}. Saving to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(json.dumps(r) + '\n')

if __name__ == "__main__":
    if not os.path.exists('eval/questions.jsonl'):
        print("ERROR: 'eval/questions.jsonl' not found. Please create the folder and file.")
    else:
        run_evaluation()
        print("\n🎉 ALL RUNS COMPLETE! Check the /predictions folder.")