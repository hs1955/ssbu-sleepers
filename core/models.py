from dataclasses import dataclass, field
from storage import load_fighters, Fighter

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
    placements: dict[str, int] = field(default_factory=dict)
    is_official: bool = False

    def tier_value(self, label: str) -> int:
        for tier in self.tiers:
            if tier.label == label:
                return tier.value
        return -1

    def char_scores(self):
        max_tier_value = self.tiers[-1].value
        return {c_id : (self.tier_value(tier) / max_tier_value) for c_id, tier in self.placements}

    def is_par(self, label: str) -> bool:
        return self.tier_value(label) >= self.tier_value(self.par)

def set_tier_values(tl: TierList):
    last_tier = tl.tiers[0]
    for tier in tl.tiers[1:]:
        print(f"How much stronger is tier: '{tier.label}' from '{last_tier.label}'?")
        print("+1 - A Little Stronger\n+2 - Noticeably Stronger\n+3 - Definitely Stronger\n+4 - Insanely Stronger")
        val = ""
        while not (val.isdigit() and 1 <= int(val) <= 4):
            val = input()
        tier.value = last_tier.value + int(val)
        last_tier = tier

def input_fighters(tl: TierList, chars: dict[str, Fighter]):
    for c_id, fighter in chars.items():
        print(" ".join(f"{tier.label}-{i+1}" for i, tier in enumerate(tl.tiers)))
        print(f"{fighter.name}")
        val = ""
        while not (val.isdigit() and 1 <= int(val) <= len(tl.tiers)):
            val = input()
        tl.placements[c_id] = tl.tiers[int(val)-1].value

def _main():
    tl = TierList("0", "test", 1.0, "A", [
        Tier("F", 0),
        Tier("B", 4),
        Tier("A", 7),
        Tier("S", 9),
    ], {})
    # set_tier_values(tl)
    print(tl)
    all_chars = load_fighters().chars
    subset_all_chars = {c: all_chars[c] for c in ("1", "2", "3", "5", "6")}
    input_fighters(tl, subset_all_chars)
    print(tl.placements)

if __name__ == "__main__":
    _main()
