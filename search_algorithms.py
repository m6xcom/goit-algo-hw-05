"""Substring search algorithms: Boyer-Moore, Knuth-Morris-Pratt, Rabin-Karp.

Every function returns the index of the first occurrence of ``pattern``
in ``text``, or -1 when the pattern is absent. An empty pattern matches at 0,
the same as ``str.find``.
"""


def build_shift_table(pattern: str) -> dict[str, int]:
    """Bad-character table: shift distance for each character of the pattern."""
    table = {}
    length = len(pattern)
    # The last character is skipped: its shift stays at the pattern length.
    for index, char in enumerate(pattern[:-1]):
        table[char] = length - index - 1
    table.setdefault(pattern[-1], length)
    return table


def boyer_moore_search(text: str, pattern: str) -> int:
    """Boyer-Moore-Horspool search with the bad-character heuristic."""
    if not pattern:
        return 0
    shift_table = build_shift_table(pattern)
    pattern_length = len(pattern)
    i = 0
    while i <= len(text) - pattern_length:
        j = pattern_length - 1
        # Compare from the end of the pattern to the start.
        while j >= 0 and text[i + j] == pattern[j]:
            j -= 1
        if j < 0:
            return i
        i += shift_table.get(text[i + pattern_length - 1], pattern_length)
    return -1


def compute_lps(pattern: str) -> list[int]:
    """Longest proper prefix that is also a suffix, for each prefix of pattern."""
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps


def kmp_search(text: str, pattern: str) -> int:
    """Knuth-Morris-Pratt search."""
    if not pattern:
        return 0
    lps = compute_lps(pattern)
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                return i - j
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1
    return -1


def rabin_karp_search(text: str, pattern: str) -> int:
    """Rabin-Karp search with a polynomial rolling hash."""
    if not pattern:
        return 0
    pattern_length = len(pattern)
    text_length = len(text)
    if pattern_length > text_length:
        return -1

    base = 256
    modulus = 1_000_000_007
    # Weight of the highest-order character, used to remove it from the hash.
    high_order = pow(base, pattern_length - 1, modulus)

    pattern_hash = 0
    window_hash = 0
    for k in range(pattern_length):
        pattern_hash = (pattern_hash * base + ord(pattern[k])) % modulus
        window_hash = (window_hash * base + ord(text[k])) % modulus

    for i in range(text_length - pattern_length + 1):
        # Equal hashes can be a collision, so confirm with a direct comparison.
        if window_hash == pattern_hash and text[i:i + pattern_length] == pattern:
            return i
        if i < text_length - pattern_length:
            window_hash = (window_hash - ord(text[i]) * high_order) % modulus
            window_hash = (window_hash * base + ord(text[i + pattern_length])) % modulus
    return -1


ALGORITHMS = {
    "Боєр-Мур": boyer_moore_search,
    "КМП": kmp_search,
    "Рабін-Карп": rabin_karp_search,
}
