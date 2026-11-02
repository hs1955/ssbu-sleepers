import os, json, pydantic
from dataclasses import asdict
from models import Fighter, TierList, Tier, input_fighters

# ../tierlists relative to this file
TIERLISTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tierlists")
)

class Fighters(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    chars: dict[str, Fighter]

def load_fighters() -> Fighters:
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/fighters.json")
    )
    with open(file_path, "r", encoding="utf-8") as file:
        return Fighters.model_validate_json(file.read())

def _tierlist_path(name: str) -> str:
    """Path to the JSON file for a tierlist named `name`."""
    os.makedirs(TIERLISTS_DIR, exist_ok=True)
    # Strip anything that could escape the directory or confuse the FS.
    safe = "".join(c for c in name if c.isalnum() or c in " -_").strip()
    if not safe:
        raise ValueError(f"invalid tierlist name: {name!r}")
    return os.path.join(TIERLISTS_DIR, f"{safe}.json")

def load_tierlist(name: str) -> TierList:
    with open(_tierlist_path(name), "r", encoding="utf-8") as f:
        data = json.load(f)

    return TierList(
        id=data["id"],
        name=data["name"],
        importance=data["importance"],
        par=data["par"],
        tiers=[Tier(**t) for t in data["tiers"]],
        placements=dict(data.get("placements", {}))
    )

def save_tierlist(tl: TierList) -> bool:
    try:
        with open(_tierlist_path(tl.name), "w", encoding="utf-8") as f:
            json.dump(asdict(tl), f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False

def list_tierlists() -> list[str]:
    """Names of all saved tierlists (filenames without .json)."""
    if not os.path.isdir(TIERLISTS_DIR):
        return []
    return sorted(
        f[:-5] for f in os.listdir(TIERLISTS_DIR) if f.endswith(".json")
    )

def _main():
    fighters = load_fighters()
    print("\n", fighters.chars)
    tl = TierList("1", "official", 1.0, "A-", [
        Tier("E", 0),
        Tier("D", 2),
        Tier("C-", 5),
        Tier("C+", 6),
        Tier("B-", 8),
        Tier("B+", 9),
        Tier("A-", 12),
        Tier("A",  13),
        Tier("A+", 14),
        Tier("S-", 16),
        Tier("S",  18),
        Tier("S+", 19),
    ], {
    # S+ (19)
    "79":  19,   # Steve
    "36":  19,   # Sonic
    "31":  19,   # Snake

    # S (18)
    "26":  18,   # Mr. Game & Watch
    "40":  18,   # R.O.B.
    "81":  18,   # Pyra & Mythra
    "139": 18,   # Kazuya

    # S- (16)
    "34":  16,   # Diddy Kong
    "78":  16,   # Min Min
    "7":   16,   # Fox
    "86":  16,   # Peach / Daisy
    "73":  16,   # Joker
    "5":   16,   # Yoshi
    "8":   16,   # Pikachu

    # A+ (14)
    "25":  14,   # Roy
    "38":  14,   # Olimar
    "58":  14,   # Cloud
    "9":   14,   # Luigi
    "60":  14,   # Bayonetta
    "85":  14,   # Samus / Dark Samus
    "49":  14,   # Palutena
    "1":   14,   # Mario

    # A (13)
    "59":  13,   # Corrin
    "30":  13,   # Wario
    "141": 13,   # Sora
    "20":  13,   # Falco
    "42":  13,   # Wolf
    "74":  13,   # Hero

    # A- (12)
    "57":  12,   # Ryu
    "54":  12,   # Shulk
    "82":  12,   # Mii Brawler
    "76":  12,   # Terry
    "29":  12,   # Zero Suit Samus
    "48":  12,   # Greninja
    "51":  12,   # Pac-Man
    "33":  12,   # Pokémon Trainer
    "41":  12,   # Toon Link
    "52":  12,   # Lucina

    # B+ (9)
    "22":  9,    # Young Link
    "89":  9,    # Pit / Dark Pit
    "11":  9,    # Captain Falcon
    "70":  9,    # Ken
    "46":  9,    # Rosalina & Luma

    # B- (8)
    "10":  8,    # Ness
    "16":  8,    # Sheik
    "27":  8,    # Meta Knight
    "44":  8,    # Mega Man
    "61":  8,    # Inkling
    "80":  8,    # Sephiroth
    "77":  8,    # Byleth
    "15":  8,    # Ice Climbers
    "19":  8,    # Pichu
    "2":   8,    # Donkey Kong

    # C+ (6)
    "39":  6,    # Lucario
    "75":  6,    # Banjo & Kazooie
    "45":  6,    # Wii Fit Trainer
    "66":  6,    # Chrom
    "35":  6,    # Lucas
    "84":  6,    # Mii Gunner
    "71":  6,    # Incineroar

    # C- (5)
    "3":   5,    # Link
    "63":  5,    # Ridley
    "14":  5,    # Bowser
    "56":  5,    # Duck Hunt
    "6":   5,    # Kirby
    "69":  5,    # Isabelle
    "53":  5,    # Robin
    "55":  5,    # Bowser Jr.
    "24":  5,    # Mewtwo
    "12":  5,    # Jigglypuff
    "21":  5,    # Marth

    # D (2)
    "83":  2,    # Mii Swordfighter
    "17":  2,    # Zelda
    "32":  2,    # Ike
    "72":  2,    # Piranha Plant
    "43":  2,    # Villager
    "37":  2,    # King Dedede
    "68":  2,    # King K. Rool
    "91":  2,    # Simon / Richter
    "18":  2,    # Dr. Mario

    # E (0)
    "47":  0,    # Little Mac
    "23":  0,    # Ganondorf
    })
    # input_fighters(tl, fighters.chars)
    save_tierlist(tl)
    print("\nsaved tierlists:", list_tierlists())

if __name__ == "__main__":
    _main()