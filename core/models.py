from dataclasses import dataclass, field

@dataclass
class Tier:
    label: str
    value: int

@dataclass
class TierList:
    id: str
    name: str
    importance: float
    par: str
    tiers: list[Tier]
    placements: dict[str, str] = field(default_factory=dict)
    is_official: bool = False

    def tier_value(self, label: str) -> int:
        par_int = next(t.value for t in self.tiers if t.label == self.par)
        return next(par_int - t.value for t in self.tiers if t.label == label)

    def is_par(self, label: str) -> bool:
        return self.tier_value(label) >= self.tier_value(self.par)