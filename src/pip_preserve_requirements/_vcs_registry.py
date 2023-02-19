# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from typing import Callable

from ._vcs import Vcs
from ._vcs_git import GitVcs


VcsFactory = Callable[[str], Vcs]


def vcs(name: str) -> Vcs:
    if name == "git":
        return GitVcs()
    raise ValueError(f"Unsupported VCS: {name}")
