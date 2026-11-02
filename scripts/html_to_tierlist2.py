from dataclasses import dataclass, field

@dataclass
class FighterData:
    img: str

@dataclass
class TierData:
    min_score: float
    description: str = ""

@dataclass
class TierList:
    name: str
    desc: str = ""
    tiers: dict[str, TierData] = field(default_factory=dict)
    scores: dict[str, float] = field(default_factory=dict)

    def get_sorted_tiers(self) -> list[tuple[str, TierData]]:
        return sorted(self.tiers.items(), key=lambda t: t[1].min_score, reverse=True)