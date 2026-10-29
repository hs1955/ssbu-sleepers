from storage import list_tierlists, load_tierlist
import numpy as np
from ckmeans import breaks   # pip install ckmeans

def gen_final_scores() -> dict[str, float]:
    tierlists = list_tierlists()
    if len(tierlists) == 0:
        print("Create some tierlists first")
        return {}

    final_scores = load_tierlist(tierlists[0]).char_scores()
    max_importance = 1
    for tl_name in tierlists[1:]:
        tl = load_tierlist(tl_name)
        max_importance = max(tl.importance, max_importance)
        tl_scores = tl.char_scores()
        for c_id, score in tl_scores.items():
            final_scores[c_id] += score * tl.importance

    # Normalize Score
    for c_id, _ in tl_scores.items():
        final_scores[c_id] /= max_importance

    return final_scores

TIER_LABELS = ["E", "D", "C", "B", "A", "S"]   # worst -> best

def gen_final_tierlist(
    scores: dict[str, float],
    k: int = 6,
    labels: list[str] | None = None,
) -> dict[str, str]:
    """Map char_id -> tier label. Assumes k == len(labels)."""
    labels = labels or TIER_LABELS
    assert len(labels) == k, f"need {k} labels, got {len(labels)}"

    ids = list(scores)
    values = np.array([scores[i] for i in ids], dtype=float)

    # k-1 cut points; digitize returns 1..k
    cut_points = breaks(values, k)
    idx = np.digitize(values, cut_points, right=False) - 1  # 0..k-1
    return {cid: labels[i] for cid, i in zip(ids, idx)}

def _main():
    pass

if __name__ == "__main__":
    _main()
