"""
eval_metrics.py  —  Real Evaluation Metrics for the RAG Critic Agent
=====================================================================

Three complementary approaches are implemented here:

1. Token-level F1 / Precision / Recall  (SQuAD-style, zero extra deps)
   - Tokenises the generated answer and the reference answer into word bags
   - Computes overlap precision, recall, and their harmonic mean (F1)
   - Best for: quick, dependency-free ground-truth comparison

2. Semantic Similarity  (requires sentence-transformers — already in requirements.txt)
   - Encodes both answers with 'all-MiniLM-L6-v2' and computes cosine similarity
   - Returns a 0-1 score; values > 0.80 are generally considered a strong match
   - Best for: paraphrase-robust comparison where wording differs but meaning matches

3. LLM Multi-Dimensional Scoring  (uses the same Groq client)
   - Asks the LLM to score Faithfulness, Relevance, and Completeness on 0-10
   - Best for: when there is no ground-truth reference answer available

Usage
-----
from eval_metrics import compute_real_metrics

# With a ground-truth reference answer (all three methods run):
metrics = compute_real_metrics(
    query          = "What is RRF?",
    generated      = "Reciprocal Rank Fusion merges ranked lists...",
    reference      = "RRF is an algorithm that combines BM25 and vector search...",
    groq_client    = client,
    groq_model     = "openai/gpt-oss-120b",
)

# Without a ground-truth reference (only LLM scoring runs):
metrics = compute_real_metrics(
    query       = "What is RRF?",
    generated   = "Reciprocal Rank Fusion merges ranked lists...",
    groq_client = client,
    groq_model  = "openai/gpt-oss-120b",
)

print(metrics)
# {
#   "token_precision": 0.72, "token_recall": 0.68, "token_f1": 0.70,
#   "semantic_similarity": 0.87,
#   "llm_faithfulness": 0.9, "llm_relevance": 0.8, "llm_completeness": 0.85,
#   "llm_composite": 0.85,
#   "overall_score": 0.806,
# }
"""

from __future__ import annotations

import json
import re
import string
from collections import Counter
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Token-level F1  (SQuAD-style)
# ─────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.split()


def token_level_metrics(generated: str, reference: str) -> dict[str, float]:
    """
    Compute token-level Precision, Recall, and F1 between generated and reference.
    Mirrors the SQuAD evaluation script logic.
    Returns values in [0, 1].
    """
    gen_tokens = Counter(_tokenize(generated))
    ref_tokens = Counter(_tokenize(reference))

    # Token overlap
    common = sum((gen_tokens & ref_tokens).values())
    total_gen = sum(gen_tokens.values())
    total_ref = sum(ref_tokens.values())

    if total_gen == 0 or total_ref == 0:
        return {"token_precision": 0.0, "token_recall": 0.0, "token_f1": 0.0}

    precision = common / total_gen
    recall    = common / total_ref
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print(f"[eval_metrics] Token Precision: {precision:.4f}")
    print(f"[eval_metrics] Token Recall: {recall:.4f}")
    print(f"[eval_metrics] Token F1: {f1:.4f}")
   
    return {
        "token_precision": round(precision, 4),
        "token_recall":    round(recall,    4),
        "token_f1":        round(f1,        4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Semantic Similarity  (sentence-transformers)
# ─────────────────────────────────────────────────────────────────────────────

_encoder = None  # lazy-loaded so import doesn't block startup


def _get_encoder():
    """Lazy-load the sentence-transformer model (cached after first call)."""
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _encoder = SentenceTransformer("all-MiniLM-L6-v2")
    return _encoder


def semantic_similarity(generated: str, reference: str) -> float:
    """
    Cosine similarity between the sentence embeddings of generated and reference.
    Uses 'all-MiniLM-L6-v2' (fast, 22M params, good general-purpose model).
    Returns a float in [0, 1]  (1 = identical meaning, 0 = unrelated).
    """
    encoder = _get_encoder()
    embeddings = encoder.encode([generated, reference], normalize_embeddings=True)
    # Cosine similarity of unit-normalised vectors = dot product
    score = float(embeddings[0] @ embeddings[1])
    # Clamp to [0, 1] in case of tiny floating-point negatives
    return round(max(0.0, min(1.0, score)), 4)


# ─────────────────────────────────────────────────────────────────────────────
# 3.  LLM Multi-Dimensional Scoring
# ─────────────────────────────────────────────────────────────────────────────

_LLM_SCORE_PROMPT = """
You are an evaluator for a RAG (Retrieval-Augmented Generation) pipeline.
Score the Generated Answer on the three dimensions below.
Each dimension should be scored from 0 to 10 (integers only).

User Query     : {query}
Generated Answer: {generated}
{reference_section}
--- Scoring Dimensions ---
1. Faithfulness  : Does the answer stick to facts and avoid hallucinations? (0 = fully hallucinated, 10 = completely grounded)
2. Relevance     : Does the answer directly address the user's query? (0 = completely off-topic, 10 = perfectly on-topic)
3. Completeness  : Does the answer cover all key aspects of the query? (0 = nothing addressed, 10 = fully complete)

Return ONLY a raw JSON object with no markdown:
{{
    "faithfulness": <0-10>,
    "relevance": <0-10>,
    "completeness": <0-10>
}}
"""


def llm_multidim_score(
    query: str,
    generated: str,
    groq_client,
    groq_model: str,
    reference: Optional[str] = None,
) -> dict[str, float]:
    """
    Ask the LLM to rate the generated answer on Faithfulness, Relevance, and Completeness.
    Normalises each dimension's 0-10 integer score to 0-1.
    If a reference is provided, the LLM uses it to check for factual grounding.
    Returns a dict with individual scores.
    """
    ref_section = f"Reference Context: {reference}\n" if reference else ""
    prompt = _LLM_SCORE_PROMPT.format(query=query, generated=generated, reference_section=ref_section)

    try:
        completion = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip("`").strip()

        scores = json.loads(raw)
        faithfulness  = max(0, min(10, int(scores.get("faithfulness",  0)))) / 10
        relevance     = max(0, min(10, int(scores.get("relevance",     0)))) / 10
        completeness  = max(0, min(10, int(scores.get("completeness",  0)))) / 10
        composite     = round((faithfulness + relevance + completeness) / 3, 4)

        return {
            "llm_faithfulness":  round(faithfulness,  4),
            "llm_relevance":     round(relevance,      4),
            "llm_completeness":  round(completeness,   4),
            "llm_composite":     composite,
        }

    except Exception as exc:
        print(f"[eval_metrics] LLM scoring failed: {exc}")
        return {
            "llm_faithfulness":  0.0,
            "llm_relevance":     0.0,
            "llm_completeness":  0.0,
            "llm_composite":     0.0,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def compute_real_metrics(
    query: str,
    generated: str,
    groq_client,
    groq_model: str,
    reference: Optional[str] = None,
) -> dict[str, float]:
    """
    Compute real evaluation metrics for a (query, generated_answer) pair.

    Parameters
    ----------
    query        : The original user query.
    generated    : The answer produced by the RAG pipeline.
    groq_client  : An initialised Groq client instance.
    groq_model   : Model name to use for LLM scoring.
    reference    : Optional ground-truth / expected answer.
                   If provided, token-F1 and semantic similarity are also computed.

    Returns
    -------
    A flat dict of metric names → float values in [0, 1].
    Always includes LLM multi-dim scores.
    Includes token & semantic scores only when reference is given.
    Includes an 'overall_score' which averages all available scores.
    """
    result: dict[str, float] = {}

    # ── Method 1 & 2: ground-truth-based metrics ─────────────────────────────
    if reference:
        tok = token_level_metrics(generated, reference)
        result.update(tok)

        try:
            result["semantic_similarity"] = semantic_similarity(generated, reference)
        except Exception as exc:
            print(f"[eval_metrics] Semantic similarity failed: {exc}")
            result["semantic_similarity"] = 0.0
    else:
        # Fallback: generating plausible precision/recall for logging and info
        print("Unable to print")

    # ── Method 3: LLM multi-dimensional scoring ───────────────────────────────
    llm = llm_multidim_score(query, generated, groq_client, groq_model, reference)
    result.update(llm)

    # ── Overall score: average of all available scores ────────────────────────
    score_keys = [
        "token_f1", "semantic_similarity",
        "llm_faithfulness", "llm_relevance", "llm_completeness",
    ]
    available_scores = [result[k] for k in score_keys if k in result]
    result["overall_score"] = round(
        sum(available_scores) / len(available_scores), 4
    ) if available_scores else 0.0

    return result


def display_real_metrics(metrics: dict[str, float]) -> None:
    """
    Pretty-prints the real evaluation metrics to the console.
    Designed to slot in where display_eval_metrics() was used.
    """
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    RESET  = "\033[0m"

    def _colour(v: float) -> str:
        if v >= 0.75: return GREEN
        if v >= 0.50: return YELLOW
        return RED

    def _bar(v: float, width: int = 20) -> str:
        filled = int(v * width)
        return "[" + "█" * filled + "░" * (width - filled) + f"] {v:.4f}"

    print(f"\n{CYAN}{'─' * 55}{RESET}")
    print(f"{CYAN}  [Real Evaluation Metrics]{RESET}")
    print(f"{CYAN}{'─' * 55}{RESET}")

    # Token metrics (only present when reference was given)
    if "token_precision" in metrics:
        print("  ── Token-Level (SQuAD-style) ──────────────────────")
        for key in ("token_precision", "token_recall", "token_f1"):
            v = metrics[key]
            label = key.replace("token_", "").capitalize().ljust(10)
            print(f"    {label}: {_colour(v)}{_bar(v)}{RESET}")

    # Semantic similarity
    if "semantic_similarity" in metrics:
        v = metrics["semantic_similarity"]
        print("  ── Semantic Similarity (sentence-transformers) ─────")
        print(f"    CosSim    : {_colour(v)}{_bar(v)}{RESET}")

    # LLM scores
    print("  ── LLM Multi-Dim Scoring ───────────────────────────")
    for key, label in [
        ("llm_faithfulness",  "Faithfulness"),
        ("llm_relevance",     "Relevance"),
        ("llm_completeness",  "Completeness"),
        ("llm_composite",     "Composite"),
    ]:
        v = metrics.get(key, 0.0)
        print(f"    {label.ljust(13)}: {_colour(v)}{_bar(v)}{RESET}")

    # Overall
    overall = metrics.get("overall_score", 0.0)
    print(f"  {'─' * 53}")
    print(f"  {'Overall Score'.ljust(13)}  : {_colour(overall)}{_bar(overall)}{RESET}")
    print(f"{CYAN}{'─' * 55}{RESET}\n")
