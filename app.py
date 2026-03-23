import sys
import os

# Add the local modules to path so we can import them from the root
sys.path.append(os.path.join(os.path.dirname(__file__), 'intent_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'querry_reformulation'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tech_crawler'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'generator_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'critic_agent'))

# Import the individual agents
from ml_agent import detect_intent
from qra import refourmulate_querry
from hybrid_search import search, exact_url_match
from generator import generate_answer
from critic import evaluate_answer

def run_agentic_rag(user_query: str, max_iterations: int = 3, use_critic: bool = True, search_strategy: str = "hybrid"):
    print(f"\n==================================================")
    print(f"User Query: {user_query}")
    print(f"==================================================\n")

    # Step 1: Detect Intent (Only done once)
    print("🤖 Agent 1 [Intent]: Analyzing query...")
    intent = detect_intent(user_query)
    print(f"   -> Detected Intent: {intent.upper()}")
    
    # We maintain a specific variable for the feedback loop
    critic_feedback = ""
    iteration = 1
    
    while iteration <= max_iterations:
        print(f"\n--- Iteration {iteration} ---")
        
        # Step 2: Query Reformulation
        print("🤖 Agent 2 [Reformulator]: Rewriting query...", end="")
        if critic_feedback:
            print(" (Using feedback from Critic)")
            # Append critic feedback for targeted reformulation
            enhanced_query = f"{user_query}. WARNING: Previous failed because '{critic_feedback}'. Fix this."
            search_query = refourmulate_querry(enhanced_query, intent)
        else:
            print("")
            search_query = refourmulate_querry(user_query, intent)
            
        print(f"   -> Search Query: {search_query}")
        
        # Step 3: Search Execution
        print(f"🤖 Agent 3 [Search]: Executing {search_strategy} search...")
        # Ensure we suppress prints from the inner hybrid_search module to keep it clean
        
        raw_results = []
        if intent.lower() == "navigational":
            # Pass the raw user query to check for exact URL matches before relying on the reformulated query
            raw_results = exact_url_match(user_query, k=5)
            
        if not raw_results:
            raw_results = search(search_query, mode=search_strategy, k=5)
        
        # Filter the raw results to only include what we need
        context = []
        for r in raw_results:
            context.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "snippet": r.get("snippet")
            })
            
        print(f"   -> Retrieved {len(context)} documents.")
        
        # Step 4: Generation
        print("🤖 Agent 4 [Generator]: Synthesizing answer...")
        answer = generate_answer(
            query=user_query,
            retrieved_contexts=context,
            original_intent=intent,
            reformulated_query=search_query
        )
        print("   -> Answer Generated.")
        
        # Step 5: Evaluation (The Critic Loop)
        if not use_critic:
            return answer
            
        print("🤖 Agent 5 [Critic]: Evaluating answer quality...")
        
        # Construct reference answer from the retrieved scraped data (snippets)
        reference_text = "\n".join([c["snippet"] for c in context if c.get("snippet")])
        
        eval_result = evaluate_answer(user_query, answer, reference_answer=reference_text)
        
        score = eval_result.get("score", "FAIL")
        reason = eval_result.get("reason", "Unknown reason.")
        
        print(f"   -> Score: {score}")
        print(f"   -> Reason: {reason}")
        
        if score == "PASS":
            print("\n✅ Critic approved the response! Returning to user.")
            return answer
        else:
            print(f"\n❌ Critic REJECTED the response. Initiating iterative retrieval...")
            critic_feedback = reason
            iteration += 1

    print(f"\n⚠️ Reached max iterations ({max_iterations}). Returning the best answer we have.")
    return answer

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the Agentic RAG Pipeline")
    parser.add_argument("-q", "--query", "--querry", dest="query", type=str, help="The search query")
    parser.add_argument("--no-critic", action="store_true", help="Disable the critic evaluation loop")
    parser.add_argument("--strategy", type=str, choices=['hybrid', 'bm25', 'vector'], default='hybrid', help="Search strategy to use (default: hybrid)")
    
    args = parser.parse_args()
    
    # Interactive mode if no initial query provided
    if not args.query:
        print("\nWelcome to the Agentic RAG System!")
        print("Type 'exit' to quit.\n")
        while True:
            q = input("\nEnter your query: ")
            if q.lower() in ['exit', 'quit', 'q']:
                break
            
            s = input(f"Select Strategy (hybrid/bm25/vector) [default: {args.strategy}]: ").strip().lower()
            if not s:
                 s = args.strategy
            elif s not in ['hybrid', 'bm25', 'vector']:
                 print("Invalid strategy, using default.")
                 s = args.strategy
            
            final_response = run_agentic_rag(q, use_critic=not args.no_critic, search_strategy=s)
            print(f"\n\nFINAL RESPONSE:\n{final_response}\n")
            print("-" * 50)
            
    else:
        final_response = run_agentic_rag(args.query, use_critic=not args.no_critic, search_strategy=args.strategy)
        print(f"\n\nFINAL RESPONSE:\n{final_response}\n")
