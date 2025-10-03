import math


def compute_combined_score(
    score: float,
    vec1: list[float],
    vec2: list[float],
    weight_score: float = 0.5,
    weight_cosine: float = 0.5,
    min_val: float = 0.7,
    max_val: float = 1.0
) -> float:
    """
    Combines a raw score with normalized cosine similarity between two embedding vectors.

    Parameters:
        score (float): Initial score.
        vec1 (list[float]): Embedding vector for control.
        vec2 (list[float]): Embedding vector for taxonomy item.
        weight_score (float): Weight for the initial score.
        weight_cosine (float): Weight for cosine similarity.
        min_val (float): Minimum threshold for cosine normalization.
        max_val (float): Maximum threshold for cosine normalization.

    Returns:
        float: Final combined score.
    """
    if score < 0.25:
        return 0.0

    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    norm_product = math.sqrt(sum(v ** 2 for v in vec1)) * math.sqrt(sum(v ** 2 for v in vec2))
    cosine = dot_product / norm_product if norm_product != 0 else 0.0
    norm_cosine = 0.0 if cosine < min_val else (cosine - min_val) / (max_val - min_val)

    return (score * weight_score) + (norm_cosine * weight_cosine)