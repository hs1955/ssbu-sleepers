# tui/app.py
"""SSBU tier list TUI — minimal keyboard-driven skeleton."""

import json
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, Static
from textual_image.widget import Image as TextualImage

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA = PROJECT_ROOT / "data"
IMAGES = PROJECT_ROOT / "images"
TIERLISTS = PROJECT_ROOT / "tierlists"

TIERS = ["S", "A", "B", "C", "D", "E", "F"]

TIER_KEYS = {
    "1": "S",
    "2": "A",
    "3": "B",
    "4": "C",
    "5": "D",
    "6": "E",
    "7": "F",
}

class TierRow(Horizontal):
    """One tier: a label plus the thumbnails currently assigned to it."""

    def __init__(self, tier: str, chars: list[dict], **kwargs) -> None:
        super().__init__(**kwargs)
        self.tier = tier
        self.chars = chars

    def compose(self) -> ComposeResult:
        yield Label(self.tier, classes="tier-label")
        for char in self.chars:
            yield TextualImage(IMAGES / char["image"], classes="thumb")

class SSBUTierApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("ctrl+z", "suspend_process"),
        *[Binding(k, f"assign('{v}')", v) for k, v in TIER_KEYS.items()],
        Binding("left", "prev", "◀"),
        Binding("right", "next", "▶"),
        Binding("u", "undo", "undo"),
        Binding("ctrl+s", "save", "save"),
        Binding("q", "quit", "quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.characters = self._load_characters()
        self.index = 0
        self.placements: dict[int, str] = {}
        self.history: list[int] = []

    @staticmethod
    def _load_characters() -> list[dict]:
        return json.loads((DATA / "fighters.json").read_text())["fighters"]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            yield Vertical(id="tiers")
            with Vertical(id="preview"):
                yield Static("", id="preview-name")
                yield TextualImage(id="preview-image")
        yield Footer()

    async def on_mount(self) -> None:
        await self._rebuild_tiers()
        self._update_preview()

    # ---------- rendering ----------

    async def _rebuild_tiers(self) -> None:
        tiers = self.query_one("#tiers", Vertical)
        await tiers.remove_children()

        rows = []
        for tier in TIERS:
            chars = [
                c for c in self.characters
                if self.placements.get(c["id"]) == tier
            ]
            rows.append(TierRow(tier, chars, classes="tier-row"))

        await tiers.mount_all(rows)

    def _update_preview(self) -> None:
        char = self.characters[self.index]
        self.query_one("#preview-name", Static).update(
            f"{char['name']}\n{self.index + 1}/{len(self.characters)}"
        )
        self.query_one("#preview-image", TextualImage).image = IMAGES / char["image"]

    # ---------- actions ----------
    async def action_assign(self, tier: str) -> None:
        char_id = self.characters[self.index]["id"]
        self.history.append(char_id)
        self.placements[char_id] = tier
        await self._rebuild_tiers()
        self.action_next()

    async def action_undo(self) -> None:
        if not self.history:
            return
        char_id = self.history.pop()
        self.placements.pop(char_id, None)
        await self._rebuild_tiers()

    def action_prev(self) -> None:
        self.index = (self.index - 1) % len(self.characters)
        self._update_preview()

    def action_next(self) -> None:
        self.index = (self.index + 1) % len(self.characters)
        self._update_preview()

    def action_save(self) -> None:
        TIERLISTS.mkdir(exist_ok=True)
        out = TIERLISTS / "my_list.json"
        out.write_text(json.dumps({
            "id": "my_list",
            "name": "My List",
            "weight": 1.0,
            "tiers": TIERS,
            "placements": {str(cid): t for cid, t in self.placements.items()},
        }, indent=2))
        self.notify(f"Saved {len(self.placements)} placements → {out.name}")


if __name__ == "__main__":
    SSBUTierApp().run()