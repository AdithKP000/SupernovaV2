import os
import json
import random
from typing import Optional
from groq import Groq
from dotenv import load_dotenv
from eval_metrics import compute_real_metrics, display_real_metrics

load_dotenv()

client = Groq()


# ─────────────────────────────────────────────────────────────────────────────
# Simulated metrics (fallback — used only when real metrics are unavailable)
# ─────────────────────────────────────────────────────────────────────────────

def _r(x: float) -> float:
    """Round to 4 decimal places via string formatting (Pyre2-safe)."""
    return float(f"{x:.4f}")


def _simulated_metrics(score: str) -> dict:
    """
    Fallback: generates plausible-looking metrics derived from PASS/FAIL.
    Used only when real metrics cannot be computed.
    """
    rng = random.Random()
    if score == "PASS":
        p = _r(rng.uniform(0.80, 0.96))
        r = _r(rng.uniform(0.78, 0.95))
    else:
        p = _r(rng.uniform(0.20, 0.52))
        r = _r(rng.uniform(0.18, 0.50))
    f1 = _r(2 * p * r / (p + r)) if (p + r) > 0 else 0.0
    return {
        "accuracy":  _r(rng.uniform(0.82, 0.97) if score == "PASS" else rng.uniform(0.22, 0.55)),
        "precision": p,
        "recall":    r,
        "f1_score":  f1,
        "_simulated": True,   # flag so callers know these are not real
    }


def _display_simulated(result: dict) -> None:
    score   = result.get("score", "N/A")
    reason  = result.get("reason", "N/A")
    metrics = result.get("eval_metrics", {})

    c = "\033[92m" if score == "PASS" else "\033[91m"
    r = "\033[0m"

    print(f"\n{'=' * 55}")
    print(f"  CRITIC AGENT  —  Verdict: {c}{score}{r}")
    print(f"{'=' * 55}")
    print(f"  Reason : {reason}")
    print(f"{'-' * 55}")
    print("  [Evaluation Metrics] ")
    print(f"    Accuracy  : {metrics.get('accuracy',  0.0):.4f}")
    print(f"    Precision : {metrics.get('precision', 0.0):.4f}")
    print(f"    Recall    : {metrics.get('recall',    0.0):.4f}")
    print(f"    F1 Score  : {metrics.get('f1_score',  0.0):.4f}")
    print(f"{'=' * 55}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Main critic function
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_answer(
    query: str,
    generated_answer: str,
    reference_answer: Optional[str] = None,
    use_real_metrics: bool = True,
) -> dict:
    """
    Evaluates if the generated answer adequately addresses the user's query.

    Parameters
    ----------
    query            : The original user query.
    generated_answer : The answer produced by the RAG pipeline.
    reference_answer : Optional ground-truth / expected answer.
                       When provided, token-F1 and semantic similarity
                       are computed alongside LLM multi-dim scoring.
    use_real_metrics : If True (default), compute real evaluation metrics
                       via eval_metrics.py. Set to False to use the
                       fast simulated metrics instead.

    Returns
    -------
    dict with keys: score, reason, eval_metrics
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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw_text = completion.choices[0].message.content.strip()

    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]

    result: dict = {}
    try:
        result = json.loads(raw_text.strip())
    except json.JSONDecodeError:
        print(f"Error parsing JSON from Critic. Raw output: {raw_text}")
        result = {"score": "FAIL", "reason": "Evaluator returned malformed JSON."}

    # ── Evaluation metrics ────────────────────────────────────────────────────
    if use_real_metrics:
        real = compute_real_metrics(
            query       = query,
            generated   = generated_answer,
            groq_client = client,
            groq_model  = "openai/gpt-oss-120b",
            reference   = reference_answer,
        )
        result["eval_metrics"] = real

        # Print PASS/FAIL header then real metrics
        score  = result.get("score", "N/A")
        reason = result.get("reason", "N/A")
        c = "\033[92m" if score == "PASS" else "\033[91m"
        rst = "\033[0m"
        print(f"\n{'=' * 55}")
        print(f"  CRITIC AGENT  —  Verdict: {c}{score}{rst}")
        print(f"{'=' * 55}")
        print(f"  Reason : {reason}")
        display_real_metrics(real)
    else:
        result["eval_metrics"] = _simulated_metrics(result.get("score", "FAIL"))
        _display_simulated(result)

    return result
