from typing import Optional

class Board:
    def __init__(self) -> None:
        self.data = [[None] * 15 for _ in range(15)]

    def __getitem__(self, key: tuple[int, int]) -> Optional[str]:
        return self.board[int(key[1]) - 1][int(key[0]) - 1]

    def __setitem__(self, key: tuple[int, int], value: Optional[str]) -> None:
        self.board[int(key[1]) - 1][int(key[0]) - 1] = value