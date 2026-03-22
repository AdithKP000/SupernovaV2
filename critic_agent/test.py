from critic import evaluate_answer

def test_with_reference():
    """
    Tests the critic with a ground-truth reference answer.
    Runs all three real metrics:
      - Token-level F1 / Precision / Recall  (SQuAD-style)
      - Semantic Similarity                  (sentence-transformers cosine sim)
      - LLM Multi-Dim Scoring                (Faithfulness / Relevance / Completeness)
    """
    query = "What is Reciprocal Rank Fusion, and how does it combine BM25 and Vector Search?"

    # ── Ground-truth reference answer ──────────────────────────────────────────
    reference = (
        "Reciprocal Rank Fusion (RRF) is a score fusion algorithm that combines "
        "the results from multiple ranked lists—such as BM25 (sparse keyword-based "
        "retrieval) and Vector Search (dense embedding-based retrieval)—into a single "
        "unified ranking. For each document, RRF computes 1 / (k + rank) across all "
        "lists and sums the scores, where k is a small constant (typically 60). "
        "Documents appearing highly in multiple lists receive a higher fused score."
    )

    good_answer = (
        "Reciprocal Rank Fusion (RRF) is an algorithm that merges ranked documents "
        "from multiple search strategies, such as BM25 (sparse keyword search) and "
        "Vector Search (dense embeddings), into a single result set. It evaluates "
        "the ranks to improve overall accuracy."
    )

    bad_answer = (
        "I'm sorry, I could not find information about adding BM25 and Vector Search "
        "together in the provided context."
    )

    print("\n" + "=" * 60)
    print("  TEST 1: Good Answer (with ground-truth reference)")
    print("=" * 60)
    result = evaluate_answer(
        query            = query,
        generated_answer = good_answer,
        reference_answer = reference,   # ← enables token-F1 + semantic similarity
        use_real_metrics = True,
    )
    print("Raw result dict:", {k: v for k, v in result.items() if k != "eval_metrics"})

    print("\n" + "=" * 60)
    print("  TEST 2: Bad Answer (with ground-truth reference)")
    print("=" * 60)
    result = evaluate_answer(
        query            = query,
        generated_answer = bad_answer,
        reference_answer = reference,
        use_real_metrics = True,
    )
    print("Raw result dict:", {k: v for k, v in result.items() if k != "eval_metrics"})

    print("\n" + "=" * 60)
    print("  TEST 3: Good Answer (no reference — LLM scoring only)")
    print("=" * 60)
    result = evaluate_answer(
        query            = query,
        generated_answer = good_answer,
        # no reference_answer → only LLM multi-dim scoring runs
        use_real_metrics = True,
    )
    print("Raw result dict:", {k: v for k, v in result.items() if k != "eval_metrics"})


if __name__ == "__main__":
    test_with_reference()
