'''https://github.com/fogleman/TWL06'''

import base64
import collections
import itertools
import struct
import zlib

def check(word):
    return word in _DAWG

def iterator():
    return iter(_DAWG)

def children(prefix):
    return _DAWG.children(prefix)

def anagram(letters):
    for word in _DAWG.anagram(letters):
        yield word

END = '$'
WILD = '?'

class _Dawg(object):
    def __init__(self, data):
        data = base64.b64decode(data)
        data = zlib.decompress(data)
        self.data = data

    def _get_record(self, index):
        a = index * 4
        b = index * 4 + 4
        x = struct.unpack('<I', self.data[a:b])[0]
        more = bool(x & 0x80000000)
        letter = chr((x >> 24) & 0x7f)
        link = int(x & 0xffffff)
        return (more, letter, link)

    def _get_child(self, index, letter):
        while True:
            more, other, link = self._get_record(index)
            if other == letter:
                return link
            if not more:
                return None
            index += 1

    def _get_children(self, index):
        result = []
        while True:
            more, letter, link = self._get_record(index)
            result.append(letter)
            if not more:
                break
            index += 1
        return result

    def _anagram(self, bag, index=0, letters=None):
        letters = letters or []
        while True:
            more, letter, link = self._get_record(index)
            if letter == END:
                yield ''.join(letters)
            elif bag[letter]:
                bag[letter] -= 1
                letters.append(letter)
                for word in self._anagram(bag, link, letters):
                    yield word
                letters.pop(-1)
                bag[letter] += 1
            elif bag[WILD]:
                bag[WILD] -= 1
                letters.append(letter)
                for word in self._anagram(bag, link, letters):
                    yield word
                letters.pop(-1)
                bag[WILD] += 1
            if not more:
                break
            index += 1

    def __contains__(self, word):
        index = 0
        for letter in itertools.chain(word, END):
            index = self._get_child(index, letter)
            if index is None:
                return False
        return True

    def __iter__(self, index=0, letters=None):
        letters = letters or []
        while True:
            more, letter, link = self._get_record(index)
            if letter == END:
                yield ''.join(letters)
            else:
                letters.append(letter)
                for word in self.__iter__(link, letters):
                    yield word
                letters.pop(-1)
            if not more:
                break
            index += 1

    def children(self, prefix):
        index = 0
        for letter in prefix:
            index = self._get_child(index, letter)
            if index in (0, None):
                return []
        return self._get_children(index)

    def anagram(self, letters):
        bag = collections.defaultdict(int)
        for letter in letters:
            bag[letter] += 1
        for word in self._anagram(bag):
            yield word

file = open("encoded_dictionary.txt", "r")
_DAWG = _Dawg(file.read().strip())
file.close()