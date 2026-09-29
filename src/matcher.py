"""Hybrid matching engine: combines SQL relational filtering with AI semantic vector matching."""
import math
import re
from typing import List

_SENTENCE_MODEL = None
_MODEL_TRIED = False


def _get_sentence_model():
    """Lazy load SentenceTransformer model if available."""
    global _SENTENCE_MODEL, _MODEL_TRIED
    if _MODEL_TRIED:
        return _SENTENCE_MODEL
    _MODEL_TRIED = True
    try:
        from sentence_transformers import SentenceTransformer
        _SENTENCE_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        _SENTENCE_MODEL = None
    return _SENTENCE_MODEL


def _tokenize(text: str) -> List[str]:
    """Simple tokenizer for fallback vector computation."""
    return re.findall(r"\b[a-zA-Z0-9_#\+\.]+\b", text.lower())


def _tfidf_cosine_similarity(text1: str, text2: str) -> float:
    """Fast, dependency-light TF-IDF cosine similarity fallback."""
    tokens1 = _tokenize(text1)
    tokens2 = _tokenize(text2)
    if not tokens1 or not tokens2:
        return 0.0

    tf1, tf2 = {}, {}
    for t in tokens1:
        tf1[t] = tf1.get(t, 0) + 1
    for t in tokens2:
        tf2[t] = tf2.get(t, 0) + 1

    all_terms = set(tf1.keys()).union(set(tf2.keys()))
    dot = 0.0
    norm1 = 0.0
    norm2 = 0.0

    for term in all_terms:
        w1 = tf1.get(term, 0)
        w2 = tf2.get(term, 0)
        dot += w1 * w2
        norm1 += w1 * w1
        norm2 += w2 * w2

    if norm1 == 0 or norm2 == 0:
        return 0.0

    sim = dot / (math.sqrt(norm1) * math.sqrt(norm2))
    return max(0.0, min(1.0, sim))


def compute_semantic_similarity(resume_text: str, job_description: str) -> float:
    """
    Computes semantic similarity percentage between resume text and job description (0 to 100).
    Uses Sentence-Transformers (all-MiniLM-L6-v2) if installed/cached,
    otherwise falls back smoothly to vector cosine similarity.
    """
    if not resume_text or not job_description:
        return 0.0

    model = _get_sentence_model()
    if model is not None:
        try:
            from sentence_transformers import util
            emb1 = model.encode(resume_text, convert_to_tensor=True)
            emb2 = model.encode(job_description, convert_to_tensor=True)
            sim = float(util.cos_sim(emb1, emb2)[0][0])
            return round(max(0.0, min(1.0, sim)) * 100, 2)
        except Exception:
            pass

    # High-fidelity fallback
    sim = _tfidf_cosine_similarity(resume_text, job_description)
    return round(sim * 100, 2)


def calculate_skill_match_pct(candidate_skills: List[str], job_skills: List[str]) -> float:
    """
    Computes percentage of job's required skills possessed by the candidate (0 to 100).
    Mirrors the Oracle PL/SQL function fn_skill_match_pct.
    """
    if not job_skills:
        return 0.0
    c_set = {s.strip().lower() for s in candidate_skills}
    j_set = {s.strip().lower() for s in job_skills}
    matched = c_set.intersection(j_set)
    return round((len(matched) / len(j_set)) * 100, 2)


def calculate_hybrid_score(skill_match_pct: float, semantic_score: float) -> float:
    """
    Calculates final composite candidate match score:
    60% semantic embedding similarity + 40% SQL keyword/skill match.
    Mirrors the Oracle PL/SQL procedure sp_apply_job.
    """
    final = 0.6 * semantic_score + 0.4 * skill_match_pct
    return round(final, 2)
