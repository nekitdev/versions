from typing import Iterable

import pytest

from versions.functions import parse_version

# NOTE: versions are ordered from smallest to largest


@pytest.mark.parametrize(
    "strings",
    (
        (
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-beta",
            "1.0.0-beta.1",
            "1.0.0-rc.1",
            "1.0.0-rc.1+build.1",
            "1.0.0",
            "1.0.0+build",
            "1.0.0+build.1",
            "1.0.0+1",
            "1.2.0",
            "1.2.3",
            "1.3.0",
            "2.0.0",
            "2.2.0",
        ),
        (
            "1.0.0-dev.0",
            "1.0.0-alpha.0-dev.0",
            "1.0.0-alpha.0",
            "1.0.0-alpha.1-dev.0",
            "1.0.0-beta.0-dev.0",
            "1.0.0-beta.1",
            "1.0.0-beta.1-post.0-dev.0",
            "1.0.0-beta.1-post.0",
            "1.0.0-rc.1",
            "1.0.0",
            "1.0.0+build.0",
            "1.0.0+build.1",
            "1.0.0-post.0-dev.0",
            "1.0.0-post.0",
            "1.1.1-dev.1",
        ),
    ),
)
def test_comparison(strings: Iterable[str]) -> None:
    versions = list(map(parse_version, strings))

    for i, v in enumerate(versions):
        for j, w in enumerate(versions):
            assert (i == j) is (v == w)
            assert (i != j) is (v != w)
            assert (i <= j) is (v <= w)
            assert (i >= j) is (v >= w)
            assert (i < j) is (v < w)
            assert (i > j) is (v > w)
