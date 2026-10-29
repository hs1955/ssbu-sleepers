import os, json, pydantic
from dataclasses import asdict
from core.models import TierList, Tier

# ../tierlists relative to this file
TIERLISTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tierlists")
)

class Fighter(pydantic.BaseModel):
    name: str
    image: str

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
        placements=dict(data.get("placements", {})),
        is_official=data.get("is_official", False),
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
    print("\nsaved tierlists:", list_tierlists())

if __name__ == "__main__":
    _main()