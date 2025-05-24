# SPDX-FileCopyrightText: 2025-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import subprocess
from pathlib import Path

import pytest

from pip_preserve_requirements._vcs import Vcs
from pip_preserve_requirements._vcs_git import GitVcs
from pip_preserve_requirements._vcs_registry import vcs_registry


@pytest.fixture(scope="module")
def git_vcs() -> Vcs:
    return vcs_registry("git")


def test_get_git_version(git_vcs: GitVcs) -> None:
    version = git_vcs._get_git_version()
    assert isinstance(version[0], int)
    assert isinstance(version[1], int)


def test_get_remote_tags_for_commit(git_vcs: GitVcs) -> None:
    tags = git_vcs.get_remote_tags_for_commit(
        "https://github.com/sbidoul/pip-preserve-requirements.git",
        "7b5bf15c487293a7cdbd19e3715993ed38457c4d",
    )
    assert tags == ["v0.3.0"]


def test_place_tag_on_commit(git_vcs: GitVcs, tmp_path: Path) -> None:
    subprocess.run(["git", "init"], check=True, cwd=tmp_path)
    git_vcs.place_tag_on_commit(
        source_repo="https://github.com/sbidoul/pip-preserve-requirements.git",
        target_repo=str(tmp_path),
        sha="7b5bf15c487293a7cdbd19e3715993ed38457c4d",
        tag="test-tag",
    )
