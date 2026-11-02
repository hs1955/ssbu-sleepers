from html.parser import HTMLParser
from enum import Enum
from dataclasses import dataclass

FighterName = str # Used as an ID for the fighter data in tierlists
@dataclass(slots=True)
class Fighter:
    name: FighterName
    img: str

TierName = str
@dataclass(slots=True)
class Tier:
    name: TierName
    description: str
    min_score: float

@dataclass(slots=True)
class TierList:
    name: str
    description: str
    _tiers: list[Tier] = []
    @property
    def tiers(self) -> list[Tier]:
        return sorted(self._tiers, key=lambda t: t.min_score, reverse=True)
    scores: dict[FighterName, float] = {}

    def get_fighter_tier(self, name: FighterName):
        for tier in self.tiers:
            if self.scores[name] > tier.min_score:
                return tier
        return self.tiers[-1]

    def get_sorted_scores(self) -> dict[FighterName, float]:
        return {k: v for k, v in sorted(self.scores.items(), key=lambda item: item[1], reverse=True)}

    def get_tier_list(self, sorted_scores: dict[FighterName, float]) -> \
                                            dict[TierName, dict[FighterName, tuple[int, float]]]:
        tierlist = {tier.name: {} for tier in self.tiers}
        sorted_scores_iter = enumerate(sorted_scores.items(), 1)
        for tier in self.tiers:
            while (entry := next(sorted_scores_iter, None)) is not None
                rank, (name, score) = entry
                if score < tier.min_score:
                    break
                tierlist[tier.name][name] = (rank, score)

        return tierlist

class ParserStates(Enum):
    TITLE, DESCRIPTION, TIER, RANKS, IMGS, SCORES = range(1, 7)
PS = ParserStates

PARSER_NEXT_STATE = {
    PS.TITLE:  PS.DESCRIPTION,     # TITLE and DESC are parsed only once!
    PS.DESCRIPTION:  PS.TIER,
    PS.TIER:   PS.RANKS,
    PS.RANKS:  PS.IMGS,
    PS.IMGS:   PS.SCORES,
    PS.SCORES: PS.TIER,     # Cycle back to TIER
}

class FighterRanksParser(HTMLParser):
    fighters: dict[FighterName, Fighter] = {}
    tierlist = TierList("", "", [], {})

    _parser_state = ParserStates.TITLE
    _tier_sizes: list[int] = []             # Tier sizes are known before the actual tiers
    _colspan = 0
    _active_tiers: list[Tier] = []          # More than 1 tier can appear on a row
    _fighters_to_add: list[FighterName] = []
    _last_score = 0.0
    # Apparently end tags with whitespace after it have data. Ignore this
    _end_tag = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._end_tag = False
        match tag:
            case "tbody":
                print("Parsing Starting")
            case "img":
                name = ""
                img = ""
                for attr, val in attrs:
                    if attr == "alt":
                        name = "" if val is None else val
                    elif attr == "src":
                        img = "" if val is None else val
                self.fighters[name] = Fighter(name, img)
                self._fighters_to_add.append(name)
            case "th" | "td":
                for attr, val in attrs:
                    if attr == "colspan" and val is not None:
                        self._colspan = int(val)

    def handle_endtag(self, tag: str) -> None:
        self._end_tag = True
        match tag:
            case "tbody":
                print("Parsing Complete")
            case "tr":
                self._parser_state = PARSER_NEXT_STATE[self._parser_state]

    def handle_data(self, data: str) -> None:
        if self._end_tag or (data.isspace() and self._parser_state != PS.SCORES):
            return
        raw_data = data.strip()
        match self._parser_state:
            case PS.TITLE:
                self.tierlist.name = raw_data
                # Title and Description are on the same row, but parsed in different calls
                self._parser_state = PS.DESCRIPTION
            case PS.DESCRIPTION:
                self.tierlist.description = raw_data
            case PS.TIER:
                tier = Tier(raw_data, raw_data, 0) # min_score unknown
                self._active_tiers.append(tier)
                self._tier_sizes.append(self._colspan)
            case PS.SCORES:
                if len(self._active_tiers) == 0:
                    return
                is_float = raw_data.replace('.','',1).isdigit()
                if is_float:
                    self._last_score = float(raw_data)
                    for _ in range(self._colspan):  # Some scores apply to the fighter and their echo
                        name = self._fighters_to_add.pop(0)
                        self.tierlist.scores[name] = self._last_score

                    self._tier_sizes[0] -= self._colspan # self._tier_sizes[0] == Fighters Left to Add
                    if self._tier_sizes[0] == 0: # Tier is complete
                        self._tier_sizes.pop(0)
                        tier = self._active_tiers.pop(0)
                        tier.min_score = self._last_score
                        self.tierlist.tiers.append(tier)

import os
def main():
    # Parse HTML File
    parser = FighterRanksParser()
    op = os.path

    path = op.abspath(op.join(op.dirname(__file__), "../init-data/official.html"))
    with open(path, "r", encoding="utf-8") as file:
        html = "".join(file.readlines())
    parser.feed(html)
    sorted_scores = parser.tierlist.get_sorted_scores()
    print(parser.tierlist.get_tier_list(sorted_scores))

if __name__ == "__main__":
    main()
