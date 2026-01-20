from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class BirthDate:
    year: int
    month: int
    day: int


BIRTHDATE = BirthDate(1997, 8, 22)
README_PATH = Path("README.md")


def calculate_age(*, today: date, birth: BirthDate) -> int:
    age = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        age -= 1
    return age


def update_level_in_readme(readme_text: str, *, new_level: int) -> tuple[str, bool]:
    pattern = re.compile(
        r"(^\s*(?:public\s+)?(?:readonly\s+)?level\s*=\s*)(\d+)(\s*;)",
        re.MULTILINE,
    )

    def replacer(match: re.Match[str]) -> str:
        return f"{match.group(1)}{new_level}{match.group(3)}"

    updated, count = pattern.subn(replacer, readme_text, count=1)
    return updated, count == 1 and updated != readme_text


def main() -> None:
    if not README_PATH.exists():
        raise SystemExit(f"Could not find {README_PATH} in repo root")

    today = date.today()  # GitHub Actions runner uses UTC
    age = calculate_age(today=today, birth=BIRTHDATE)

    original = README_PATH.read_text(encoding="utf-8")
    updated, changed = update_level_in_readme(original, new_level=age)

    if not changed:
        # If level already matches, or pattern not found, keep workflow idempotent.
        # Still fail hard if we couldn't find the level assignment at all.
        if re.search(
            r"^\s*(?:public\s+)?(?:readonly\s+)?level\s*=\s*\d+\s*;",
            original,
            re.MULTILINE,
        ) is None:
            raise SystemExit("Could not find a 'level = <number>;' assignment to update in README.md")
        return

    README_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
