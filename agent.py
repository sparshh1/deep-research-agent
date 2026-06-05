import os
import json
import time
import google.generativeai as genai
from retriever import get_relevant_chunks
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel("gemini-flash-lite-latest")

def safe_llm_call(prompt):
    """Wraps the LLM call in a retry loop to handle 429 Rate Limits."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            
            time.sleep(4) 
            return llm.generate_content(prompt).text
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                print(f" rate limit hit sleeping for 60 secs before retrying")
                time.sleep(60)
            else:
                print(f" [LLM Error] {e}")
                return ""
    return ""

def run_research_agent(question, config):
    context = []
    
    search_queries = [question]
    if config.get('use_planner'):
        plan_prompt = f"Decompose this question into 3 sub-queries for research: {question}. Return ONLY a JSON list of strings."
        response_text = safe_llm_call(plan_prompt)
        try:
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            search_queries = json.loads(clean_text)
        except:
            pass 

    for round_num in range(3): 
        for q in search_queries:
            chunks = get_relevant_chunks(q, k=3)
            context.extend(chunks)
        
        if not config.get('use_reflector'):
            break 
            
        reflect_prompt = f"Question: {question}\nEvidence: {context}\nIs this enough? Reply 'YES' or 'NO, need info on [topic]'"
        decision = safe_llm_call(reflect_prompt)
        if "YES" in decision.upper():
            break

    synth_prompt = f"Answer '{question}' using ONLY this context: {context}. Cite as [arXiv:ID]."
    final_answer = safe_llm_call(synth_prompt)

    return final_answer