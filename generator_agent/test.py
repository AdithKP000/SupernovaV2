from generator import generate_answer

def test_generator():
    query = "What is Reciprocal Rank Fusion?"
    original_intent = "informational"
    reformulated_query = "Reciprocal Rank Fusion algorithm definition explanation"
    
    # Dummy context mimicking the output of hybrid_search.py
    dummy_context = [
        {
            "title": "Understanding RRF",
            "url": "https://example.com/rrf",
            "snippet": "Reciprocal Rank Fusion (RRF) is an algorithm that evaluates the search scores of multiple previously ranked results to produce a unified result set with improved accuracy."
        },
        {
            "title": "Hybrid Search Strategies",
            "url": "https://example.com/hybrid",
            "snippet": "When combining sparse algorithms like BM25 with dense vector search, RRF is often employed to merge the two distinct ranking lists into a single consolidated ranking."
        }
    ]
    
    print("--- Testing Generator Agent ---\n")
    print(f"Query: {query}")
    print("Generating Answer...\n")
    
    answer = generate_answer(
        query=query, 
        retrieved_contexts=dummy_context, 
        original_intent=original_intent, 
        reformulated_query=reformulated_query
    )
    
    print("--- Generated Answer ---")
    print(answer)

if __name__ == "__main__":
    test_generator()
