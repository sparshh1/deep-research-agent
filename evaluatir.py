import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
judge_model = genai.GenerativeModel("gemini-flash-lite-latest")

def score_predictions():
    configs = ["no_reflector", "no_verifier"]
    
    for config in configs:
        filepath = f"predictions/{config}.jsonl"
        if not os.path.exists(filepath):
            continue
            
        print(f"\nScoring: {config}")
        total_accuracy = 0
        total_faithfulness = 0
        count = 0
        
        with open(filepath, 'r') as f:
            for line in f:
                data = json.loads(line)
                question = data['question_id'] 
                answer = data['answer']
                
            
                prompt = f"""
                Evaluate this research answer on a scale of 1 to 5 for:
                1. Accuracy (Is it a coherent, well-structured research answer?)
                2. Faithfulness (Does it properly use and format inline [arXiv:ID] citations?)
                
                Answer to evaluate: {answer}
                
                Return ONLY a JSON dictionary: {{"accuracy": <score>, "faithfulness": <score>}}
                """
                
                try:
                    score_txt = judge_model.generate_content(prompt).text
                    score_txt = score_txt.replace('```json\n', '').replace('\n```', '')
                    scores = json.loads(score_txt)
                    
                    total_accuracy += scores.get('accuracy', 0)
                    total_faithfulness += scores.get('faithfulness', 0)
                    count += 1
                except Exception as e:
                    print(f"Error scoring {question}: {e}")
                
                time.sleep(6) 
                
        if count > 0:
            print(f"avg accuracy: {total_accuracy/count:.2f} and avg Faithfulness: {total_faithfulness/count:.2f}")

if __name__ == "__main__":
    score_predictions()