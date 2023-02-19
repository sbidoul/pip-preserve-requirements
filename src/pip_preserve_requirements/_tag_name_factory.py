# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import re


class TagNameFactory:
    def __init__(self, tag_prefix: str, match_any_tag: bool = False):
        self.tag_prefix = tag_prefix
        self.match_any_tag = match_any_tag

    def make_tag(self, sha: str) -> str:
        return f"{self.tag_prefix}{sha}"

    def matches_tag(self, tag: str) -> bool:
        if self.match_any_tag:
            return True
        return (
            tag.startswith(self.tag_prefix)
            and len(tag) == len(self.tag_prefix) + 40
            and bool(re.match(".*[0-9a-f]{40}$", tag))
        )
