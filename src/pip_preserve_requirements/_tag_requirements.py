# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pip_requirements_parser import (  # type: ignore[import-untyped]
    Link,
    RequirementsFile,
)

from ._cache import Cache
from ._norm_reqs import normalize_req_lines
from ._pip_vcs_url import PipVcsUrl, UnsupportedVcsUrlError
from ._schemas import VcsVault
from ._tag_name_factory import TagNameFactory
from ._utils import log_info, log_warning
from ._vcs_registry import VcsRegistry, vcs_registry


def get_vault_for_pip_vcs_url(
    pip_vcs_url: PipVcsUrl, vcs_vaults: Sequence[VcsVault]
) -> tuple[VcsVault | None, bool]:
    """Return the vault to use for the given url,
    and a flag telling whether a push to that vault is required."""
    default_vault = None
    for allowed_vault in vcs_vaults:
        if (
            pip_vcs_url.provider == allowed_vault.provider
            and pip_vcs_url.owner == allowed_vault.owner
        ):
            return allowed_vault, False
        if allowed_vault.default:
            default_vault = allowed_vault
    return default_vault, True


def _tag_commit_if_needed(
    pip_vcs_url: PipVcsUrl,
    cache: Cache,
    tag_name_factory: TagNameFactory,
    vcs_registry: VcsRegistry = vcs_registry,
) -> None:
    for tag in cache.get_commit_tags(
        pip_vcs_url.provider,
        pip_vcs_url.owner,
        pip_vcs_url.repo,
        pip_vcs_url.revision,
    ):
        if tag_name_factory.matches_tag(tag):
            # we have a tag in cache, assume it has not been removed on the remote
            return
    remote_tags = vcs_registry(pip_vcs_url.vcs).get_remote_tags_for_commit(
        pip_vcs_url.vcs_url(), pip_vcs_url.revision
    )
    new_tags = []
    for tag in remote_tags:
        if tag_name_factory.matches_tag(tag):
            # a tag already exists on the remote
            break
    else:
        # no matching tag found on the remote, create one
        tag = tag_name_factory.make_tag(pip_vcs_url.revision)
        log_info(f"Creating tag {tag} on {pip_vcs_url.vcs_url()}")
        vcs_registry(pip_vcs_url.vcs).place_tag_on_commit(
            pip_vcs_url.vcs_url(),
            pip_vcs_url.vcs_url(for_push=True),
            pip_vcs_url.revision,
            tag,
        )
        new_tags.append(tag)
    # update the cache with the tags found on the remote
    cache.update_commit_tags(
        pip_vcs_url.provider,
        pip_vcs_url.owner,
        pip_vcs_url.repo,
        pip_vcs_url.revision,
        remote_tags + new_tags,
    )


def _push_and_tag_commit_to_vault(
    pip_vcs_url: PipVcsUrl,
    vcs_vault: VcsVault,
    cache: Cache,
    tag_name_factory: TagNameFactory,
    vcs_registry: VcsRegistry = vcs_registry,
) -> PipVcsUrl:
    vault_pip_vcs_url = pip_vcs_url.with_provider(
        provider=vcs_vault.provider, owner=vcs_vault.owner, ssh_only=vcs_vault.ssh_only
    )
    tag = tag_name_factory.make_tag(pip_vcs_url.revision)
    source_url = pip_vcs_url.vcs_url()
    target_url = vault_pip_vcs_url.vcs_url(for_push=True)
    log_info(f"Pushing {source_url} to {target_url} and tagging as {tag}")
    vcs_registry(pip_vcs_url.vcs).place_tag_on_commit(
        source_url,
        target_url,
        pip_vcs_url.revision,
        tag,
    )
    cache.add_commit_tag(
        vault_pip_vcs_url.provider,
        vault_pip_vcs_url.owner,
        vault_pip_vcs_url.repo,
        pip_vcs_url.revision,
        tag,
    )
    return vault_pip_vcs_url


def tag_requirements_file(
    requirements_file_path: Path,
    vcs_vaults: Sequence[VcsVault],
    cache: Cache,
    tag_name_factory: TagNameFactory,
    vcs_registry: VcsRegistry = vcs_registry,
) -> None:
    requirements_file = RequirementsFile.from_file(requirements_file_path)
    for requirement in requirements_file.requirements:
        if not requirement.link:
            continue
        try:
            pip_vcs_url = PipVcsUrl.from_url(requirement.link.url)
        except UnsupportedVcsUrlError:
            log_warning(
                f"Can't preserve unsupported requirement URL: {requirement.link.url}"
            )
            continue
        vcs_vault, needs_push = get_vault_for_pip_vcs_url(pip_vcs_url, vcs_vaults)
        if needs_push:
            if vcs_vault is None:
                log_warning(
                    f"No vault defined for: {requirement.link.url}. "
                    f"Make sure to configure a vcs_vault with default = true."
                )
                continue
            pip_vcs_url = _push_and_tag_commit_to_vault(
                pip_vcs_url, vcs_vault, cache, tag_name_factory, vcs_registry
            )
            requirement.link = Link(str(pip_vcs_url))
        else:
            _tag_commit_if_needed(pip_vcs_url, cache, tag_name_factory, vcs_registry)
    requirements_file_path.write_text(
        normalize_req_lines(requirements_file.dumps()), encoding="utf-8"
    )


def tag_requirements_files(
    requirements_files: Sequence[Path],
    vcs_vaults: Sequence[VcsVault],
    cache: Cache,
    tag_name_factory: TagNameFactory,
    vcs_registry: VcsRegistry = vcs_registry,
) -> None:
    for requirements_file in requirements_files:
        tag_requirements_file(
            requirements_file, vcs_vaults, cache, tag_name_factory, vcs_registry
        )
