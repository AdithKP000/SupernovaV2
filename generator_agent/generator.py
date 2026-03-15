import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

def generate_answer(query: str, retrieved_contexts: list, original_intent: str = None, reformulated_query: str = None) -> str:
    """
    Synthesizes an answer using the retrieved contexts.
    Can Optionally take in the intent and reformulated query to better guide the LLM's synthesis.
    """
    
    # Format the context into a clean string for the LLM
    formatted_context = ""
    for idx, item in enumerate(retrieved_contexts):
        formatted_context += f"\n--- Source {idx+1} ---\n"
        formatted_context += f"Title: {item.get('title', 'N/A')}\n"
        formatted_context += f"URL: {item.get('url', 'N/A')}\n"
        formatted_context += f"Snippet: {item.get('snippet', 'N/A')}\n"

    # We provide the LLM with the intent and reformulated query so it knows *why* these documents were retrieved
    prompt = f"""
    You are an expert AI assistant powering a search engine. 
    Your task is to answer the user's original query using ONLY the provided search results.
    
    --- User Context ---
    Original Query: {query}
    Detected Intent: {original_intent if original_intent else 'Unknown'}
    Reformulated Query used for search: {reformulated_query if reformulated_query else 'None'}
    
    --- Search Results ---
    {formatted_context}
    
    --- Instructions ---
    1. Answer the Original Query thoroughly based on the Search Results. 
    2. Cite your sources using the Title or URL provided in the context (e.g., "According to [Title]...").
    3. If the answer cannot be found in the provided Search Results, clearly state: "I need more information to answer this query." DO NOT hallucinate external knowledge.
    4. Keep the formatting clean and readable using Markdown.
    """

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7, 
    )

    return completion.choices[0].message.content.strip()
