"""Compare Boyer-Moore, KMP and Rabin-Karp on two articles with timeit.

Run: python benchmark.py
"""

import sys
import timeit
from pathlib import Path

from search_algorithms import ALGORITHMS

BASE_DIR = Path(__file__).parent
NUMBER = 10   # calls per measurement
REPEAT = 5    # measurements; the best one is reported

# For each article: one substring that exists in the text, one that does not.
ARTICLES = {
    "Стаття 1": {
        "file": "стаття 1.txt",
        "existing": "Правильно підібраний алгоритм пошуку",
        "fake": "квантовий алгоритм сортування",
    },
    "Стаття 2": {
        "file": "стаття 2.txt",
        "existing": "БДР можуть успішно застосовуватися",
        "fake": "квантовий алгоритм сортування",
    },
}


def read_text(path: Path) -> str:
    """Read a text file; the course files may be UTF-8 or Windows-1251."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unknown encoding: {path}")


def measure(func, text: str, pattern: str) -> float:
    """Best time of one call, in seconds."""
    timer = timeit.Timer(lambda: func(text, pattern))
    return min(timer.repeat(repeat=REPEAT, number=NUMBER)) / NUMBER


def main() -> None:
    # Cyrillic output must not depend on the Windows console code page.
    sys.stdout.reconfigure(encoding="utf-8")
    # results[article][kind][algorithm] = seconds
    results: dict[str, dict[str, dict[str, float]]] = {}

    for article, config in ARTICLES.items():
        text = read_text(BASE_DIR / config["file"])
        results[article] = {}
        for kind in ("existing", "fake"):
            pattern = config[kind]
            expected = text.find(pattern)
            if (expected >= 0) != (kind == "existing"):
                raise ValueError(f"{article}: wrong {kind} substring {pattern!r}")
            results[article][kind] = {}
            for name, func in ALGORITHMS.items():
                found = func(text, pattern)
                if found != expected:
                    raise AssertionError(f"{name} returned {found}, expected {expected}")
                results[article][kind][name] = measure(func, text, pattern)

        print(f"\n{article}: {config['file']} ({len(text)} символів)")
        position = text.find(config["existing"])
        print(f"  існуючий підрядок: {config['existing']!r} (позиція {position})")
        print(f"  вигаданий підрядок: {config['fake']!r}")
        print(f"  {'Алгоритм':<12}{'існуючий, мс':>16}{'вигаданий, мс':>16}{'сума, мс':>12}")
        for name in ALGORITHMS:
            existing = results[article]["existing"][name] * 1000
            fake = results[article]["fake"][name] * 1000
            print(f"  {name:<12}{existing:>16.4f}{fake:>16.4f}{existing + fake:>12.4f}")
        totals = {name: sum(results[article][k][name] for k in ("existing", "fake"))
                  for name in ALGORITHMS}
        print(f"  Найшвидший: {min(totals, key=totals.get)}")

    overall = {name: sum(results[a][k][name] for a in results for k in ("existing", "fake"))
               for name in ALGORITHMS}
    print("\nВ цілому (сума всіх чотирьох вимірів):")
    for name, seconds in sorted(overall.items(), key=lambda item: item[1]):
        print(f"  {name:<12}{seconds * 1000:>12.4f} мс")
    print(f"  Найшвидший: {min(overall, key=overall.get)}")


if __name__ == "__main__":
    main()
