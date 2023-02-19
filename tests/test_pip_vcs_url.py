# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import pytest

from pip_preserve_requirements._pip_vcs_url import PipVcsUrl, UnsupportedVcsUrlError

SHA = "a" * 40


def test_pip_vcs_url() -> None:
    url = (
        f"git+ssh://git@github.com/sbidoul/pip-preserve-requirements.git"
        f"@{SHA}"
        f"#subdirectory=subdir&egg=blah"
    )
    pip_vcs_url = PipVcsUrl.from_url(url)
    assert pip_vcs_url.vcs == "git"
    assert pip_vcs_url.provider == "github.com"
    assert pip_vcs_url.owner == "sbidoul"
    assert pip_vcs_url.repo == "pip-preserve-requirements.git"
    assert pip_vcs_url.revision == SHA
    assert str(pip_vcs_url) == url


def test_pip_vcs_url_no_revision() -> None:
    url = f"git+ssh://git@github.com/sbidoul/pip-preserve-requirements.git@{SHA}"
    pip_vcs_url = PipVcsUrl.from_url(url)
    assert pip_vcs_url.owner == "sbidoul"
    assert pip_vcs_url.repo == "pip-preserve-requirements.git"
    assert pip_vcs_url.revision == SHA
    assert str(pip_vcs_url) == url


@pytest.mark.parametrize(
    "url, for_push, expected",
    [
        (
            f"git+ssh://git@github.com/sbidoul/pip-preserve-requirements@{SHA}",
            False,
            "ssh://git@github.com/sbidoul/pip-preserve-requirements",
        ),
        (
            f"git+https://github.com/sbidoul/pip-preserve-requirements@{SHA}",
            False,
            "https://github.com/sbidoul/pip-preserve-requirements",
        ),
        (
            f"git+https://github.com/sbidoul/pip-preserve-requirements@{SHA}",
            True,
            "ssh://git@github.com/sbidoul/pip-preserve-requirements",
        ),
    ],
)
def test_vcs_url(url: str, for_push: bool, expected: str) -> None:
    pip_vcs_url = PipVcsUrl.from_url(url)
    assert pip_vcs_url.vcs_url(for_push) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/sbidoul/pip-preserve-requirements.git",
    ],
)
def test_unsupported_vcs_url(url: str) -> None:
    with pytest.raises(UnsupportedVcsUrlError):
        PipVcsUrl.from_url(url)


def test_with_provider() -> None:
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://github.com/sbidoul/pip-preserve-requirements@{SHA}"
    ).with_provider(provider="gitlab.acme.com", owner="acme")
    assert str(pip_vcs_url) == (
        f"git+https://gitlab.acme.com/acme/pip-preserve-requirements@{SHA}"
    )


def test_with_provider_private() -> None:
    pip_vcs_url = PipVcsUrl.from_url(
        f"git+https://$USR:$PWD@github.com/sbidoul/pip-preserve-requirements@{SHA}"
    ).with_provider(provider="gitlab.acme.com", owner="acme", ssh_only=True)
    assert str(pip_vcs_url) == (
        f"git+ssh://git@gitlab.acme.com/acme/pip-preserve-requirements@{SHA}"
    )
