from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq()

def refourmulate_querry(query,intent):

    prompt = f"""
You are a search query reformulation agent.

Rewrite the query for better retrieval in a hybrid search engine.

Intent: {intent}

Rules:
- If NAVIGATIONAL → rewrite as official website search
- If TECHNICAL → expand with relevant technical keywords
- If COMPARISON → expand both entities
- If RESEARCH → make it detailed
- If INFORMATIONAL → clarify meaning

Query: {query}

Return only the rewritten query.
"""

    # --- Ollama (commented out) ---
    # response = ollama.chat(
    #     model="mistral",
    #     messages=[{"role":"user","content":prompt}]
    # )
    # return response['message']['content'].strip()

    # We don't need streaming here since the agent orchestrator expects a string return
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b", # Changing to the OSS model requested by the user
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3, # low temp for deterministic reformulation
    )

    return completion.choices[0].message.content.strip()