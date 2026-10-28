from dataclasses import dataclass
from models import Tier, TierList

@dataclass
class Score:
    char_id: str
    weighted_avg: float
    par_count: int          # how many lists consider them tourney viable
    list_count: int         # how many lists ranked them at all

def aggregate(roster: list[dict], lists: list[TierList]) -> dict[str, Score]:
    out = {}
    for char in roster:
        cid = str(char["id"])
        num = den = 0.0
        par_count = 0
        for tl in lists:
            tier = tl.placements.get(cid)
            if not tier:
                continue
            num += tl.tier_value(tier) * tl.importance
            den += tl.importance
            if tl.is_par(tier):
                par_count += 1
        if den:
            out[cid] = Score(cid, num / den, par_count, len(
                [l for l in lists if cid in l.placements]))
    return out

def outliers(scores: dict[str, Score], official: TierList,
             threshold: float) -> list[tuple[str, float, float, float]]:
    """Return (char_id, computed, official, delta) for outliers."""
    rows = []
    for cid, s in scores.items():
        tier = official.placements.get(cid)
        if not tier:
            continue
        off = official.tier_value(tier)
        delta = s.weighted_avg - off
        if abs(delta) >= threshold:
            rows.append((cid, s.weighted_avg, off, delta))
    return sorted(rows, key=lambda r: -abs(r[3]))