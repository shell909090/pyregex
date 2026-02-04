#!/usr/bin/env python3
"""
Quick test suite for regex library - supports both regex and nfa implementations
"""

import argparse
import sys
from typing import Callable


def test_case(name: str, pattern: str, text: str, expected: bool,
              match_func: Callable[[str, str], bool]) -> bool:
    """Test a single regex pattern with specified matcher function"""
    try:
        result = match_func(pattern, text)
        status = "✓" if result == expected else "✗"
        print(f"{status} {name:30s} | Pattern: {pattern:20s} | Text: {text:20s} | Expected: {expected}")
        return result == expected
    except Exception as e:
        print(f"✗ {name:30s} | Pattern: {pattern:20s} | Error: {e}")
        return False


def run_regex_tests() -> bool:
    """Run tests using the regex implementation"""
    import regex

    def regex_matcher(pattern: str, text: str) -> bool:
        return bool(regex.match(pattern, text))

    print("=" * 100)
    print("Regex Implementation Test Suite")
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
        if test_case(*test, match_func=regex_matcher):
            passed += 1
        else:
            failed += 1

    print("=" * 100)
    print(f"Regex Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 100)

    return failed == 0


def run_nfa_tests() -> bool:
    """Run tests using the NFA implementation"""
    import nfa

    def nfa_matcher(pattern: str, text: str) -> bool:
        compiled = nfa.compile(pattern)
        return compiled.match(text)

    print("=" * 100)
    print("NFA Implementation Test Suite")
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

        # 9. Non-greedy quantifiers
        ("Non-greedy (*?)", "a.*?b", "aXXXb", True),

        # 10. Alternation (|)
        ("Alternation (|)", "abc|def", "abc", True),
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test_case(*test, match_func=nfa_matcher):
            passed += 1
        else:
            failed += 1

    print("=" * 100)
    print(f"NFA Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 100)

    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Quick test suite for regex implementations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Run both regex and nfa tests
  %(prog)s --impl regex # Run only regex tests
  %(prog)s --impl nfa   # Run only nfa tests
        """
    )
    parser.add_argument(
        '--impl',
        choices=['regex', 'nfa', 'all'],
        default='all',
        help='Select implementation to test (default: all)'
    )

    args = parser.parse_args()

    results = []

    if args.impl in ['regex', 'all']:
        results.append(run_regex_tests())
        if args.impl == 'all':
            print()  # Add blank line between test suites

    if args.impl in ['nfa', 'all']:
        results.append(run_nfa_tests())

    # All test suites must pass
    return all(results)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
