from random import choice

class TileBag:
    def __init__(self) -> None:
        self.tiles = list("EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTTLLLLSSSSUUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ")

    def get(self) -> str:
        tile = choice(self.tiles)
        self.tiles.remove(tile)
        return tile