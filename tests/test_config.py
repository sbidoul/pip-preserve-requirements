# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pathlib import Path
import textwrap

import pytest
import pydantic

from pip_preserve_requirements._config import Config


def test_config(tmp_path: Path) -> None:
    pyproject_toml_path = tmp_path / "pyproject.toml"
    pyproject_toml_path.write_text(
        textwrap.dedent(
            """\
            [project]
            name = "pkga"

            [tool.pip-preserve-requirements]
            invalid_ignored = "..."

            [[tool.pip-preserve-requirements.vcs_vaults]]
            provider = "github.com"
            owner = "acsone"
            default = true

            [[tool.pip-preserve-requirements.vcs_vaults]]
            provider = "gitlab.acme.com"
            owner = "acme"
            ssh_only = true
            """
        )
    )
    config = Config.from_pyproject_toml(tmp_path)
    assert config.vcs_vaults[0].provider == "github.com"
    assert config.vcs_vaults[0].owner == "acsone"
    assert config.vcs_vaults[0].ssh_only is False
    assert config.vcs_vaults[0].default is True
    assert config.vcs_vaults[1].provider == "gitlab.acme.com"
    assert config.vcs_vaults[1].owner == "acme"
    assert config.vcs_vaults[1].ssh_only is True
    assert config.vcs_vaults[1].default is False


def test_config_error(tmp_path: Path) -> None:
    pyproject_toml_path = tmp_path / "pyproject.toml"
    pyproject_toml_path.write_text(
        textwrap.dedent(
            """\
            [project]
            name = "pkga"

            [[tool.pip-preserve-requirements.vcs_vaults]]
            provider = "github.com"
            # missing owner
            """
        )
    )
    with pytest.raises(pydantic.ValidationError):
        Config.from_pyproject_toml(tmp_path)
