#!/usr/bin/env python3
"""
Quick test suite for regex library - 10 most common use cases
"""

import regex


def test_case(name: str, pattern: str, text: str, expected: bool) -> bool:
    """Test a single regex pattern"""
    result = bool(regex.match(pattern, text))
    status = "✓" if result == expected else "✗"
    print(f"{status} {name:30s} | Pattern: {pattern:20s} | Text: {text:20s} | Expected: {expected}")
    return result == expected


def main():
    print("=" * 100)
    print("Quick Regex Test Suite - 10 Most Common Use Cases")
    print("=" * 100)

    tests = [
        # 1. Basic wildcard matching with .*
        ("Wildcard match (.*)", "abc.*def", "abcXYZdef", True),

        # 2. One or more matches with .+
        ("One or more (.+)", "abc.+def", "abczdef", True),

        # 3. Optional match with .?
        ("Optional match (.?)", "abc.?def", "abcdef", True),

        # 4. Character class [a-z]
        ("Character class", "abc[a-z]*def", "abczzdef", True),

        # 5. Negated character class [^a-z]
        ("Negated class", "abc[^a-z]*def", "abcZZdef", True),

        # 6. Digit matching with \d
        ("Digit match (\\d)", "abc\\ddef", "abc0def", True),

        # 7. Whitespace matching with \s
        ("Whitespace (\\s)", "abc\\sdef", "abc def", True),

        # 8. Escape special characters
        ("Escape special chars", "abc\\.\\*def", "abc.*def", True),

        # 9. Repetition count {n,m}
        ("Repetition {n,m}", "abc.{2,3}def", "abczzdef", True),

        # 10. Capturing groups
        ("Capturing groups", "abc([a-z]*)def", "abczzdef", True),
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test_case(*test):
            passed += 1
        else:
            failed += 1

    print("=" * 100)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 100)

    return failed == 0


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
