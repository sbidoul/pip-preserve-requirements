# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import subprocess
from typing import List
import tempfile

from ._vcs import Vcs


class GitVcs(Vcs):
    def get_remote_tags_for_commit(self, url: str, sha: str) -> List[str]:
        remote_tags = []
        tag_prefix = "refs/tags/"
        tag_lines = subprocess.run(
            ["git", "ls-remote", "-t", url], text=True, capture_output=True, check=True
        ).stdout
        for tag_line in tag_lines.split("\n"):
            if not tag_line:
                continue
            remote_sha, ref = tag_line.split()
            if remote_sha == sha:
                assert ref.startswith(tag_prefix)
                remote_tags.append(ref[len(tag_prefix) :])
        return remote_tags

    def place_tag_on_commit(
        self, source_repo: str, target_repo: str, sha: str, tag: str
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["git", "clone", "--bare", "--filter=blob:none", source_repo, tmpdir],
                check=True,
            )
            subprocess.run(
                ["git", "-C", tmpdir, "tag", tag, sha],
                check=True,
            )
            subprocess.run(
                ["git", "-C", tmpdir, "push", target_repo, tag],
                check=True,
            )
