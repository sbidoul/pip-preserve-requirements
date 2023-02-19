# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pip_preserve_requirements._tag_name_factory import TagNameFactory

SHA = "a" * 40
PREFIX = "my-repo-"


def test_make_tag() -> None:
    tag_name_factory = TagNameFactory(PREFIX)
    assert tag_name_factory.make_tag(SHA) == PREFIX + SHA


def test_matches_tag() -> None:
    tag_name_factory = TagNameFactory(PREFIX)
    assert tag_name_factory.matches_tag(tag_name_factory.make_tag(SHA))
    assert not tag_name_factory.matches_tag(PREFIX + SHA + "a")


def test_matches_tag_any() -> None:
    tag_name_factory = TagNameFactory(PREFIX, match_any_tag=True)
    assert tag_name_factory.matches_tag(tag_name_factory.make_tag(SHA))
    assert tag_name_factory.matches_tag(PREFIX + SHA + "a")
