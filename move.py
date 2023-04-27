from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from board import Board

from collections import defaultdict

from constants import InvalidReason, Bonus, BONUS_LOCATIONS, LETTER_POINTS
import twl as scrabble

class Move:
    def __init__(self, board: Board, tiles: dict[tuple[int, int], str]):
        self.board = board
        self.tiles = tiles

        self.words = set()
        self.score = 0
        self.invalid_reason = "Interesting..."
        self.invalid = not self.validate_placement() or not self.validate_words()

    def validate_placement(self) -> bool:
        horizontal = len(set([pos[1] for pos in self.tiles])) == 1 # All y coord equal
        vertical = len(set([pos[0] for pos in self.tiles])) == 1   # All x coord equal

        # Neither vertical nor horizontal: not in a straight line
        if not horizontal and not vertical:
            self.invalid_reason = InvalidReason.NotInStraightLine.value
            return False

        # Check if tiles are connected to the same horizontal/vertical word
        if horizontal:
            left = min(self.tiles, key=lambda pos: pos[0])[0]
            right = max(self.tiles, key=lambda pos: pos[0])[0]
            y = next(iter(self.tiles))[1]
            for x in range(left, right):
                if not self.board[(x, y)]:
                    self.invalid_reason = InvalidReason.SeparateWords.value
                    return False
        elif vertical:
            top = min(self.tiles, key=lambda pos: pos[1])[1]
            bottom = max(self.tiles, key=lambda pos: pos[1])[1]
            x = next(iter(self.tiles))[0]
            for y in range(top, bottom):
                if not self.board[(x, y)]:
                    self.invalid_reason = InvalidReason.SeparateWords.value
                    return False

        # Early return if it's the first move (on center tile)
        if (8, 8) in self.tiles:
            return True

        # Check if the word formed is disconnected from pre-existing words
        for pos in self.tiles:
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (pos[0] + offset[0], pos[1] + offset[1])
                if neighbor not in self.tiles and (self.board[neighbor] or (not 0 <= neighbor[0] < 15 and 0 <= neighbor[1] < 15)):
                    return True
        self.invalid_reason = InvalidReason.Disconnected.value
        return False

    def validate_words(self) -> bool:
        seen = set()

        # Check horizontal words
        for pos in self.tiles:
            word = ""
            mult = 1
            score = 0
            # Advance to left of tile
            left = pos[0]
            while left >= 0 and self.board[(left, pos[1])]:
                letter = self.board[(left, pos[1])]
                word = letter + word
                bonus = BONUS_LOCATIONS[(left, pos[1])]
                if (left, pos[1]) in self.tiles:
                    score += LETTER_POINTS[letter] * bonus.value[0]
                    mult *= bonus.value[1]
                else:
                    score += LETTER_POINTS[letter]
                left -= 1
            # Advance to right of tile
            right = pos[0] + 1
            while right < 15 and self.board[(right, pos[1])]:
                letter = self.board[(right, pos[1])]
                word += letter
                bonus = BONUS_LOCATIONS[(right, pos[1])]
                if (right, pos[1]) in self.tiles:
                    score += LETTER_POINTS[letter] * bonus.value[0]
                    mult *= bonus.value[1]
                else:
                    score += LETTER_POINTS[letter]
                right += 1
            # If one letter then skip
            if left + 1 == right - 1: continue
            self.words.add(word)
            if ((left, pos[1]), (right, pos[1])) in seen: continue
            self.score += score * mult
            seen.add(((left, pos[1]), (right, pos[1])))

        # Check vertical words
        for pos in self.tiles:
            word = ""
            mult = 1
            score = 0
            # Advance to top of tile
            top = pos[1]
            while top >= 0 and self.board[(pos[0], top)]:
                letter = self.board[(pos[0], top)]
                word = letter + word
                bonus = BONUS_LOCATIONS[(pos[0], top)]
                if (pos[0], top) in self.tiles:
                    score += LETTER_POINTS[letter] * bonus.value[0]
                    mult *= bonus.value[1]
                else:
                    score += LETTER_POINTS[letter]
                top -= 1
            # Advance to bottom of tile
            bottom = pos[1] + 1
            while bottom < 15 and self.board[(pos[0], bottom)]:
                letter = self.board[(pos[0], bottom)]
                word += letter
                bonus = BONUS_LOCATIONS[(pos[0], bottom)]
                if (pos[0], bottom) in self.tiles:
                    score += LETTER_POINTS[letter] * bonus.value[0]
                    mult *= bonus.value[1]
                else:
                    score += LETTER_POINTS[letter]
                bottom += 1
            # If one letter then skip
            if top + 1 == bottom - 1: continue
            self.words.add(word)
            if ((pos[0], top), (pos[0], bottom)) in seen: continue
            self.score += score * mult
            seen.add(((pos[0], top), (pos[0], bottom)))

        # Check for word validity
        for word in self.words:
            if not scrabble.check(word.lower()):
                self.invalid_reason = InvalidReason.NonexistentWord.value % word
                return False
        return True