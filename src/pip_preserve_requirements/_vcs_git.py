# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import re
import subprocess
import tempfile

from ._vcs import Vcs

GIT_VERSION_REGEX = re.compile(
    r"^git version "  # Prefix.
    r"(\d+)"  # Major.
    r"\.(\d+)"  # Dot, minor.
    r"(?:\.(\d+))?"  # Optional dot, patch.
    r".*$"  # Suffix, including any pre- and post-release segments we don't care about.
)


class GitVcs(Vcs):
    @classmethod
    def _get_git_version(cls) -> tuple[int, ...]:
        version = subprocess.run(
            ["git", "version"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
        match = GIT_VERSION_REGEX.match(version)
        if not match:
            return ()
        return (int(match.group(1)), int(match.group(2)))

    def get_remote_tags_for_commit(self, url: str, sha: str) -> list[str]:
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
            clone_cmd = [
                "git",
                "clone",
                "--bare",
                "--filter=blob:none",
                source_repo,
                tmpdir,
            ]
            if self._get_git_version() >= (2, 49):
                # git 2.49 learned to clone a single commit with --revision
                clone_cmd.extend(["--revision", sha])
            subprocess.run(
                clone_cmd,
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
