from critic import evaluate_answer

def test_critic():
    query = "What is Reciprocal Rank Fusion, and how does it combine BM25 and Vector Search?"
    
    good_answer = "Reciprocal Rank Fusion (RRF) is an algorithm that merges ranked documents from multiple search strategies, such as BM25 (sparse keyword search) and Vector Search (dense embeddings), into a single result set. It evaluates the ranks to improve overall accuracy."
    
    bad_answer = "I'm sorry, I could not find information about adding BM25 and Vector Search together in the provided context."
    
    print("--- Testing Critic Agent (GOOD ANSWER) ---\n")
    print(evaluate_answer(query, good_answer))
    
    print("\n--- Testing Critic Agent (BAD ANSWER) ---\n")
    print(evaluate_answer(query, bad_answer))

if __name__ == "__main__":
    test_critic()
