'''
A convenient, self-contained, 515 KB Scrabble dictionary module, ideal
for use in word games.

Functionality:

- Check if a word is in the dictionary.
- Enumerate all words in the dictionary.
- Determine what letters may appear after a given prefix.
- Determine what words can be formed by anagramming a set of letters.

Sample usage:

>>> import twl
>>> twl.check('dog')
True
>>> twl.check('dgo')
False
>>> words = set(twl.iterator())
>>> len(words)
178691
>>> twl.children('dude')
['$', 'd', 'e', 's']
>>> list(twl.anagram('top'))
['op', 'opt', 'pot', 'to', 'top']

Provides a simple API using the TWL06 (official Scrabble tournament) 
dictionary. Contains American English words that are between 2 and 15 
characters long, inclusive. The dictionary contains 178691 words.

Implemented using a DAWG (Directed Acyclic Word Graph) packed in a 
binary lookup table for a very small memory footprint, not only on 
disk but also once loaded into RAM. In fact, this is the primary
benefit of this method over others - it is optimized for low memory
usage (not speed).

The data is stored in the Python module as a base-64 encoded, 
zlib-compressed string.

Each record of the DAWG table is packed into a 32-bit integer.

MLLLLLLL IIIIIIII IIIIIIII IIIIIIII

M - More Flag
L - ASCII Letter (lowercase or '$')
I - Index (Pointer)

The helper method _get_record(index) will extract these three elements 
into a Python tuple such as (True, 'a', 26). 

All searches start at index 0 in the lookup table. Records are scanned 
sequentially as long as the More flag is set. These records represent all 
of the children of the current node in the DAWG. For example, the first
26 records are:

0 (True, 'a', 26)
1 (True, 'b', 25784)
2 (True, 'c', 11666)
3 (True, 'd', 39216)
4 (True, 'e', 33704)
5 (True, 'f', 50988)
6 (True, 'g', 46575)
7 (True, 'h', 60884)
8 (True, 'i', 56044)
9 (True, 'j', 67454)
10 (True, 'k', 65987)
11 (True, 'l', 76093)
12 (True, 'm', 68502)
13 (True, 'n', 83951)
14 (True, 'o', 79807)
15 (True, 'p', 89048)
16 (True, 'q', 88465)
17 (True, 'r', 113967)
18 (True, 's', 100429)
19 (True, 't', 125171)
20 (True, 'u', 119997)
21 (True, 'v', 134127)
22 (True, 'w', 131549)
23 (True, 'x', 136449)
24 (True, 'y', 136058)
25 (False, 'z', 136584)

The root node contains 26 children because there are words that start 
with all 26 letters. Other nodes will have fewer children. For example,
if we jump to the node for the prefix 'b', we see:

25784 (True, 'a', 25795)
25785 (True, 'd', 28639)
25786 (True, 'e', 27322)
25787 (True, 'h', 29858)
25788 (True, 'i', 28641)
25789 (True, 'l', 29876)
25790 (True, 'o', 30623)
25791 (True, 'r', 31730)
25792 (True, 'u', 32759)
25793 (True, 'w', 33653)
25794 (False, 'y', 33654)

So the prefix 'b' may be followed only by these letters:

a, d, e, h, i, l, o, r, u, w, y

The helper method _get_child(index, letter) will return a new index
(or None if not found) when traversing an edge to a new node. For
example, _get_child(0, 'b') returns 25784.

The search is performed iteratively until the sentinel value, $, is
found. If this value is found, the string is a word in the dictionary.
If at any point during the search the appropriate child is not found,
the search fails - the string is not a word.

See also:

http://code.activestate.com/recipes/577835-self-contained-twl06-dictionary-module-500-kb/
http://en.wikipedia.org/wiki/Official_Tournament_and_Club_Word_List
http://www.isc.ro/lists/twl06.zip
'''

import base64
import collections
import itertools
import struct
import zlib

def check(word):
    '''
    Returns True if `word` exists in the TWL06 dictionary.
    Returns False otherwise.
    
    >>> twl.check('word')
    True
    >>> twl.check('asdf')
    False
    '''
    return word in _DAWG

def iterator():
    '''
    Returns an iterator that will yield all words stored in the 
    dictionary in alphabetical order.
    
    Useful if you want to use this module simply as a method of
    loading words into another type of data structure. (After 
    all, this Python module is significantly smaller than the
    original word list file - 500KB vs 1900KB.)
    
    >>> words = set(twl.iterator())
    >>> words = list(twl.iterator())
    '''
    return iter(_DAWG)

def children(prefix):
    '''
    Returns a list of letters that may appear after `prefix`.
    '''
    return _DAWG.children(prefix)

def anagram(letters):
    '''
    Yields words that can be formed with some or all of the 
    given `letters`. `letters` may include '?' characters as
    a wildcard.
    '''
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