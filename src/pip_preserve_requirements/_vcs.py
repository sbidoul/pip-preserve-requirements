# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from typing import List


class Vcs(ABC):
    @abstractmethod
    def get_remote_tags_for_commit(self, url: str, commit: str) -> List[str]: ...

    @abstractmethod
    def place_tag_on_commit(
        self, source_repo: str, target_repo: str, sha: str, tag: str
    ) -> None: ...
