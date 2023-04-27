from typing import Optional
from random import choice

class TileBag:
    def __init__(self) -> None:
        self.tiles = list("EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTTLLLLSSSSUUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ")

    def get(self) -> Optional[str]:
        try:
            tile = choice(self.tiles)
        except IndexError: # Out of tiles
            return None
        self.tiles.remove(tile)
        return tile