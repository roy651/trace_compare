"""Comparison modes: each takes two field values and returns True when they count as similar."""

from collections.abc import Sequence

from rapidfuzz import fuzz

FUZZY_THRESHOLD = 85.0
SEMANTIC_THRESHOLD = 0.75
NUMERIC_THRESHOLD = 0.05

EMBEDDING_MODEL_NAME = "sentence-transformers/nli-distilroberta-base-v2"

_embedding_model = None


def deep_equal(x, y):
    """
    Compare two objects using custom rules:
    - numeric: exact equality
    - boolean: exact equality
    - string: equality after stripping spaces
    - list: order-independent equality (multiset semantics)
    - tuple: same length, elementwise in order
    - set / frozenset: order-independent, deep comparison of elements
    - dict: recursive deep equality on all keys/values
    - objects with attributes: compare their __dict__ recursively
    - other types: fallback to ==
    """
    if x is None or y is None:
        return x is y

    # Numbers, excluding bool
    if (
        isinstance(x, (int, float))
        and isinstance(y, (int, float))
        and not isinstance(x, bool)
        and not isinstance(y, bool)
    ):
        return x == y

    if isinstance(x, bool) and isinstance(y, bool):
        return x == y

    if isinstance(x, str) and isinstance(y, str):
        return x.strip() == y.strip()

    # List: order does not matter, multiset semantics
    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return False
        used = [False] * len(y)
        for u in x:
            for i, v in enumerate(y):
                if not used[i] and deep_equal(u, v):
                    used[i] = True
                    break
            else:
                return False
        return True

    # Tuple: same length, compared in order
    if isinstance(x, tuple) and isinstance(y, tuple):
        if len(x) != len(y):
            return False
        return all(deep_equal(u, v) for u, v in zip(x, y))

    # Set / frozenset: deep comparison without order
    if isinstance(x, (set, frozenset)) and isinstance(y, (set, frozenset)):
        if len(x) != len(y):
            return False

        y_list = list(y)
        used = [False] * len(y_list)

        for u in x:
            found = False
            for i, v in enumerate(y_list):
                if not used[i] and deep_equal(u, v):
                    used[i] = True
                    found = True
                    break
            if not found:
                return False

        return True

    if isinstance(x, dict) and isinstance(y, dict):
        if x.keys() != y.keys():
            return False
        return all(deep_equal(x[k], y[k]) for k in x)

    if type(x) is type(y) and hasattr(x, "__dict__") and hasattr(y, "__dict__"):
        return deep_equal(vars(x), vars(y))

    return x == y


def fuzzy_similar(x, y, threshold: float = FUZZY_THRESHOLD) -> bool:
    """
    Compare two strings, or two lists of strings, by fuzzy similarity.

    - Strings: token set ratio >= threshold.
    - Lists: each side is joined with spaces, then WRatio >= threshold.
    - Any other type combination: False.
    """
    if isinstance(x, str) and isinstance(y, str):
        score = fuzz.token_set_ratio(x, y)
        return score >= threshold

    if isinstance(x, list) and isinstance(y, list):
        left = " ".join(str(s) for s in x)
        right = " ".join(str(s) for s in y)

        score = fuzz.WRatio(left, right)
        return score >= threshold

    return False


def _get_embedding_model():
    """Load the sentence-transformers model on first use, so importing this module stays light."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "The semantic_similarity comparison mode needs the 'semantic' extra: "
                "pip install 'trace-compare[semantic]'"
            ) from None
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def semantic_similar(
    x: str | list[str],
    y: str | list[str],
    threshold: float = SEMANTIC_THRESHOLD,
) -> bool:
    """
    Compare two strings, or two lists of strings, by cosine similarity of sentence embeddings.

    - Strings: similarity >= threshold.
    - Lists: each side is joined with spaces, then compared as strings.
    - Any other type combination: False.
    """

    def _semantic_similarity(a: str, b: str) -> float:
        model = _get_embedding_model()
        from sentence_transformers import util

        embeddings = model.encode([a, b], convert_to_tensor=True)
        return util.cos_sim(embeddings[0], embeddings[1]).item()

    if isinstance(x, str) and isinstance(y, str):
        sim = _semantic_similarity(x, y)
        return sim >= threshold

    if isinstance(x, list) and isinstance(y, list):
        left = " ".join(str(s) for s in x)
        right = " ".join(str(s) for s in y)

        sim = _semantic_similarity(left, right)
        return sim >= threshold

    return False


def numeric_similar(x, y, threshold: float = NUMERIC_THRESHOLD, mode: str = "absolute") -> bool:
    """
    Compare two numbers, or two numeric sequences of the same length, within a tolerance.

    Scalars:
        mode = "absolute" -> |x - y| <= threshold
        mode = "relative" -> |x - y| / max(|x|, |y|) <= threshold

    Sequences (lists/tuples) of the same length:
        mode = "absolute" -> average(|xi - yi|) <= threshold
        mode = "relative" -> average( |xi - yi| / max(|xi|, |yi|) ) <= threshold

    Sequences of different lengths return False.
    """

    def _is_sequence(obj):
        return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes))

    if _is_sequence(x) and _is_sequence(y):
        if len(x) != len(y):
            return False

        n = len(x)
        if n == 0:
            return True

        if mode == "absolute":
            avg_diff = sum(abs(a - b) for a, b in zip(x, y)) / n
            return avg_diff <= threshold

        if mode == "relative":
            rel_diffs = []
            for a, b in zip(x, y):
                if a == 0 and b == 0:
                    rel_diffs.append(0.0)
                else:
                    denom = max(abs(a), abs(b))
                    rel_diffs.append(abs(a - b) / denom)
            avg_rel_diff = sum(rel_diffs) / n
            return avg_rel_diff <= threshold

        raise ValueError("mode must be 'absolute' or 'relative'")

    if mode == "absolute":
        return abs(x - y) <= threshold

    if mode == "relative":
        if x == 0 and y == 0:
            return True
        denom = max(abs(x), abs(y))
        return abs(x - y) / denom <= threshold

    raise ValueError("mode must be 'absolute' or 'relative'")


def same_type_and_length(x, y):
    """
    True when x and y have the same type and, if they support len(), the same length.
    Two values of the same type that both lack len() (ints, floats) also return True.
    """
    if type(x) is not type(y):
        return False

    try:
        return len(x) == len(y)
    except TypeError:
        try:
            len(x)
        except TypeError:
            try:
                len(y)
            except TypeError:
                return True

        return False


def both_or_none(x, y):
    """True when both values are present or both are missing."""
    return (x is None) == (y is None)


# Modes applied when both values are present. field_exists is handled separately
# because it is the one mode that must see a value missing on one side.
VALUE_COMPARISONS = {
    "exact_match": deep_equal,
    "fuzzy_match": fuzzy_similar,
    "semantic_similarity": semantic_similar,
    "approximate_numeric": numeric_similar,
    "list_length": same_type_and_length,
}
