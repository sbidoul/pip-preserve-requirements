# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pathlib import Path

from pip_preserve_requirements._cache import Cache


def test_cache_initialize(tmp_path: Path) -> None:
    _cache = Cache(tmp_path)
    cache_dir = tmp_path / ".pip_preserve_requirements_cache"
    assert cache_dir.is_dir()
    assert (cache_dir / ".gitignore").is_file()
    assert (cache_dir / "CACHEDIR.TAG").is_file()


def test_cache_get_tags(tmp_path: Path) -> None:
    cache = Cache(tmp_path)
    provider, org, repo, sha = (
        "github.com",
        "acsone",
        "pip-preserve-requirements",
        "some_sha",
    )
    cache.add_commit_tag(provider, org, repo, sha, "some_tag")
    cache.add_commit_tag(provider, org, repo, sha, "some_other_tag")
    assert cache.get_commit_tags(provider, org, repo, sha) == [
        "some_tag",
        "some_other_tag",
    ]
    # test persistence
    cache2 = Cache(tmp_path)
    assert cache2.get_commit_tags(provider, org, repo, sha) == [
        "some_tag",
        "some_other_tag",
    ]


def test_cache_remove_tags(tmp_path: Path) -> None:
    cache = Cache(tmp_path)
    provider, org, repo, sha = (
        "github.com",
        "acsone",
        "pip-preserve-requirements",
        "some_sha",
    )
    cache.add_commit_tag(provider, org, repo, sha, "some_tag")
    cache.add_commit_tag(provider, org, repo, sha, "some_other_tag")
    assert cache.get_commit_tags(provider, org, repo, sha) == [
        "some_tag",
        "some_other_tag",
    ]
    cache2 = Cache(tmp_path)
    cache2.remove_commit_tags(provider, org, repo, sha)
    assert not cache2.get_commit_tags(provider, org, repo, sha)
    cache3 = Cache(tmp_path)
    assert not cache3.get_commit_tags(provider, org, repo, sha)


def test_cache_update_tags(tmp_path: Path) -> None:
    cache = Cache(tmp_path)
    provider, org, repo, sha = (
        "github.com",
        "acsone",
        "pip-preserve-requirements",
        "some_sha",
    )
    cache.add_commit_tag(provider, org, repo, sha, "some_tag")
    cache.add_commit_tag(provider, org, repo, sha, "some_other_tag")
    assert cache.get_commit_tags(provider, org, repo, sha) == [
        "some_tag",
        "some_other_tag",
    ]
    cache.update_commit_tags(provider, org, repo, sha, ["tag1", "tag2"])
    assert cache.get_commit_tags(provider, org, repo, sha) == [
        "tag1",
        "tag2",
    ]
