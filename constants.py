from collections import defaultdict
from enum import Enum

IP = "" # "192.168.0.90"
PORT = 1200
ADDRESS = (IP, PORT)

class InvalidReason(Enum):
    NotInStraightLine = "All tiles must be placed on the same row or column!"
    SeparateWords = "All tiles must be connected to the same word!"
    Disconnected = "The word formed must be connected to pre-existing words!"
    NonexistentWord = "The word '%s' doesn't exist!"

# (letter_multiplier, word_multiplier)
class Bonus(Enum):
    DL = (2, 1)
    TL = (3, 1)
    DW = (1, 2)
    TW = (1, 3)
    NONE = (1, 1)

BONUS_LOCATIONS = defaultdict(lambda: Bonus.NONE, {
    (4, 1): Bonus.DL,
    (12, 1): Bonus.DL,
    (7, 3): Bonus.DL,
    (9, 3): Bonus.DL,
    (1, 4): Bonus.DL,
    (8, 4): Bonus.DL,
    (15, 4): Bonus.DL,
    (3, 7): Bonus.DL,
    (7, 7): Bonus.DL,
    (9, 7): Bonus.DL,
    (13, 7): Bonus.DL,
    (4, 8): Bonus.DL,
    (12, 8): Bonus.DL,
    (3, 9): Bonus.DL,
    (7, 9): Bonus.DL,
    (9, 9): Bonus.DL,
    (13, 9): Bonus.DL,
    (1, 12): Bonus.DL,
    (8, 12): Bonus.DL,
    (15, 12): Bonus.DL,
    (7, 13): Bonus.DL,
    (9, 13): Bonus.DL,
    (4, 15): Bonus.DL,
    (12, 15): Bonus.DL,

    (6, 2): Bonus.TL,
    (10, 2): Bonus.TL,
    (2, 6): Bonus.TL,
    (6, 6): Bonus.TL,
    (10, 6): Bonus.TL,
    (14, 6): Bonus.TL,
    (2, 10): Bonus.TL,
    (6, 10): Bonus.TL,
    (10, 10): Bonus.TL,
    (14, 10): Bonus.TL,
    (6, 14): Bonus.TL,
    (10, 14): Bonus.TL,

    (2, 2): Bonus.DW,
    (3, 3): Bonus.DW,
    (4, 4): Bonus.DW,
    (5, 5): Bonus.DW,
    (14, 2): Bonus.DW,
    (13, 3): Bonus.DW,
    (12, 4): Bonus.DW,
    (11, 5): Bonus.DW,
    (14, 14): Bonus.DW,
    (13, 13): Bonus.DW,
    (12, 12): Bonus.DW,
    (11, 11): Bonus.DW,
    (2, 14): Bonus.DW,
    (3, 13): Bonus.DW,
    (4, 12): Bonus.DW,
    (5, 11): Bonus.DW,
    (8, 8): Bonus.DW,

    (1, 1): Bonus.TW,
    (15, 1): Bonus.TW,
    (15, 15): Bonus.TW,
    (1, 15): Bonus.TW,
    (8, 1): Bonus.TW,
    (15, 8): Bonus.TW,
    (8, 15): Bonus.TW,
    (1, 8): Bonus.TW,
})

LETTER_POINTS = {
    "A": 1, "E": 1, "I": 1, "O": 1, "U": 1, "L": 1, "N": 1, "S": 1, "T": 1, "R": 1,
    "D": 2, "G": 2,
    "B": 3, "C": 3, "M": 3, "P": 3,
    "F": 4, "H": 4, "V": 4, "W": 4, "Y": 4,
    "K": 5,
    "J": 8, "X": 8,
    "Q": 10, "Z": 10,
}