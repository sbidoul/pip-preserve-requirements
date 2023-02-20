# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import textwrap
from pathlib import Path
from unittest.mock import Mock

from pip_preserve_requirements._tag_requirements import (
    get_vault_for_pip_vcs_url,
    tag_requirements_file,
    tag_requirements_files,
    _tag_commit_if_needed,
)
from pip_preserve_requirements._pip_vcs_url import PipVcsUrl
from pip_preserve_requirements._schemas import VcsVault
from pip_preserve_requirements._cache import Cache
from pip_preserve_requirements._tag_name_factory import TagNameFactory

SHA = "a" * 40
SHA2 = "b" * 40
SHA3 = "c" * 40


def test_get_vault_for_pip_vcs_url_vault_found() -> None:
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/sbidoul/pip-preserve-requirements.git@{SHA}"
    )
    vaults = [VcsVault(provider="github.com", owner="sbidoul")]
    vault, needs_push = get_vault_for_pip_vcs_url(pip_vcs_url, vaults)
    assert vault is not None
    assert needs_push is False
    assert (
        vault.repo_url("pip-preserve-requirements.git", for_push=False)
        == "https://github.com/sbidoul/pip-preserve-requirements.git"
    )


def test_get_vault_for_pip_vcs_url_no_default_vault() -> None:
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/nobody/pip-preserve-requirements.git@{SHA}"
    )
    vaults = [VcsVault(provider="github.com", owner="sbidoul")]
    vault, needs_push = get_vault_for_pip_vcs_url(pip_vcs_url, vaults)
    assert vault is None
    assert needs_push is True


def test_get_vault_for_pip_vcs_url_with_default_vault() -> None:
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/nobody/pip-preserve-requirements.git@{SHA}"
    )
    vaults = [VcsVault(provider="github.com", owner="sbidoul", default=True)]
    vault, needs_push = get_vault_for_pip_vcs_url(pip_vcs_url, vaults)
    assert vault is not None
    assert needs_push is True
    assert (
        vault.repo_url("pip-preserve-requirements.git", for_push=True)
        == "ssh://git@github.com/sbidoul/pip-preserve-requirements.git"
    )


def test_tag_commit_if_needed_needed(tmp_path: Path) -> None:
    """Test that a tag is placed if the commit has no tag yet."""
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/sbidoul/pip-preserve-requirements.git@{SHA}"
    )
    cache = Cache(tmp_path)
    tag_name_factory = TagNameFactory("ppr-", match_any_tag=False)
    vcs = Mock()
    vcs.get_remote_tags_for_commit.return_value = ["v1.1"]
    _tag_commit_if_needed(
        pip_vcs_url, cache, tag_name_factory, vcs_registry=lambda _name: vcs
    )
    assert cache.get_commit_tags(
        pip_vcs_url.provider, pip_vcs_url.owner, pip_vcs_url.repo, pip_vcs_url.revision
    ) == ["v1.1", f"ppr-{SHA}"]
    vcs.place_tag_on_commit.assert_called_once_with(
        "https://github.com/sbidoul/pip-preserve-requirements.git",
        "ssh://git@github.com/sbidoul/pip-preserve-requirements.git",
        SHA,
        f"ppr-{SHA}",
    )


def test_tag_commit_if_needed_not_needed(tmp_path: Path) -> None:
    """Test that no tag is placed if the commit is already tagged."""
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/sbidoul/pip-preserve-requirements.git@{SHA}"
    )
    cache = Cache(tmp_path)
    tag_name_factory = TagNameFactory("ppr-", match_any_tag=False)
    vcs = Mock()
    vcs.get_remote_tags_for_commit.return_value = [f"ppr-{SHA}"]
    _tag_commit_if_needed(
        pip_vcs_url, cache, tag_name_factory, vcs_registry=lambda _name: vcs
    )
    assert cache.get_commit_tags(
        pip_vcs_url.provider, pip_vcs_url.owner, pip_vcs_url.repo, pip_vcs_url.revision
    ) == [f"ppr-{SHA}"]
    vcs.place_tag_on_commit.assert_not_called()


def test_tag_commit_if_needed_cached(tmp_path: Path) -> None:
    """Test that no VCS operation is attempted if the commit tag is already cached."""
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/sbidoul/pip-preserve-requirements.git@{SHA}"
    )
    cache = Cache(tmp_path)
    # add non matching tag
    cache.add_commit_tag(
        pip_vcs_url.provider, pip_vcs_url.owner, pip_vcs_url.repo, SHA, "v1.1"
    )
    # add matching tag
    cache.add_commit_tag(
        pip_vcs_url.provider, pip_vcs_url.owner, pip_vcs_url.repo, SHA, f"ppr-{SHA}"
    )
    tag_name_factory = TagNameFactory("ppr-", match_any_tag=False)
    vcs = Mock()
    _tag_commit_if_needed(
        pip_vcs_url, cache, tag_name_factory, vcs_registry=lambda _name: vcs
    )
    vcs.get_remote_tags_for_commit.assert_not_called()
    vcs.place_tag_on_commit.assert_not_called()


def test_tag_commit_if_needed_any_tag(tmp_path: Path) -> None:
    """Test that no tag is placed if the commit is already tagged a non matching tag."""
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/sbidoul/pip-preserve-requirements.git@{SHA}"
    )
    cache = Cache(tmp_path)
    tag_name_factory = TagNameFactory("ppr-", match_any_tag=True)
    vcs = Mock()
    vcs.get_remote_tags_for_commit.return_value = ["v1.1"]
    _tag_commit_if_needed(
        pip_vcs_url, cache, tag_name_factory, vcs_registry=lambda _name: vcs
    )
    assert cache.get_commit_tags(
        pip_vcs_url.provider, pip_vcs_url.owner, pip_vcs_url.repo, pip_vcs_url.revision
    ) == ["v1.1"]
    vcs.place_tag_on_commit.assert_not_called()


def test_tag_requirements_file_basic(tmp_path: Path, capsys) -> None:
    """A basic integration test."""
    requirements_file_path = tmp_path / "requirements.txt"
    requirements_file_path.write_text(
        textwrap.dedent(
            f"""\
            git+https://github.com/OCA/mis-builder@{SHA}
            git+https://gitlab.acme.com/acme/my-repo@{SHA2}
            git+ssh://git@github.com/upstream/private-repo@{SHA3}
            --find-links=https://example.com/wheelhouse
            pkga==1.0
            https://example.com/pkgb-1.0.tar.gz
            """
        )
    )
    cache = Cache(tmp_path)
    vcs = Mock()
    vcs.get_remote_tags_for_commit.return_value = []
    tag_requirements_files(
        [requirements_file_path],
        [VcsVault(provider="gitlab.acme.com", owner="acme", default=True)],
        cache,
        TagNameFactory("ppr-", match_any_tag=False),
        vcs_registry=lambda _name: vcs,
    )
    assert requirements_file_path.read_text() == textwrap.dedent(
        f"""\
            git+https://gitlab.acme.com/acme/mis-builder@{SHA}
            git+https://gitlab.acme.com/acme/my-repo@{SHA2}
            git+ssh://git@gitlab.acme.com/acme/private-repo@{SHA3}
            --find-links https://example.com/wheelhouse
            pkga==1.0
            https://example.com/pkgb-1.0.tar.gz
        """
    )
    assert cache.get_commit_tags("gitlab.acme.com", "acme", "mis-builder", SHA) == [
        f"ppr-{SHA}"
    ]
    assert cache.get_commit_tags("gitlab.acme.com", "acme", "my-repo", SHA2) == [
        f"ppr-{SHA2}"
    ]
    assert cache.get_commit_tags("gitlab.acme.com", "acme", "private-repo", SHA3) == [
        f"ppr-{SHA3}"
    ]
    assert (
        capsys.readouterr().err == "Can't preserve unsupported requirement URL: "
        "https://example.com/pkgb-1.0.tar.gz\n"
    )


def test_tag_requirements_file_private_vault(tmp_path: Path) -> None:
    requirements_file_path = tmp_path / "requirements.txt"
    requirements_file_path.write_text(
        textwrap.dedent(
            f"""\
            --find-links=https://example.com/wheelhouse
            git+https://github.com/OCA/mis-builder@{SHA}
            """
        )
    )
    cache = Cache(tmp_path)
    vcs = Mock()
    vcs.get_remote_tags_for_commit.return_value = []
    tag_requirements_file(
        requirements_file_path,
        [
            VcsVault(
                provider="gitlab.acme.com", owner="acme", ssh_only=True, default=True
            )
        ],
        cache,
        TagNameFactory("ppr-", match_any_tag=False),
        vcs_registry=lambda _name: vcs,
    )
    assert requirements_file_path.read_text() == textwrap.dedent(
        f"""\
            --find-links https://example.com/wheelhouse
            git+ssh://git@gitlab.acme.com/acme/mis-builder@{SHA}
        """
    )
