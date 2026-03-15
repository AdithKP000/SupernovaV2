import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

def evaluate_answer(query: str, generated_answer: str) -> dict:
    """
    Evaluates if the generated answer adequately addresses the user's query.
    Returns a dictionary with 'score' (PASS/FAIL) and 'reason'.
    """
    
    prompt = f"""
    You are a strict Evaluator Agent for a RAG (Retrieval-Augmented Generation) pipeline.
    Your task is to grade the Generated Answer based on whether it fully and accurately answers the User Query.
    
    --- Input ---
    User Query: {query}
    Generated Answer: {generated_answer}
    
    --- Grading Rules ---
    1. Reply with "PASS" ONLY if the answer directly and adequately answers the user's query.
    2. Reply with "FAIL" if the answer says "I need more information", is completely irrelevant, or misses the core intent of the query.
    3. You must provide a brief "reason" explaining your score. If it's a FAIL, explain exactly what is missing so the search engine can try again.
    
    --- Output Format ---
    You must return ONLY a raw JSON object with no markdown formatting or extra text.
    {{
        "score": "PASS" | "FAIL",
        "reason": "Your brief explanation here."
    }}
    """

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        response_format={"type": "json_object"} # Groq supports json mode!
    )
    
    raw_text = completion.choices[0].message.content.strip()
    
    # Strip markdown block if the LLM hallucinated it despite instructions
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
        
    try:
        result = json.loads(raw_text.strip())
        return result
    except json.JSONDecodeError:
        print(f"Error parsing JSON from Critic. Raw output: {raw_text}")
        # Default to FAIL to be safe if parsing fails
        return {"score": "FAIL", "reason": "Evaluator returned malformed JSON."}
