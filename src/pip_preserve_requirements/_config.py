# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pathlib import Path

from pydantic import BaseModel

from ._compat import tomllib
from ._schemas import VcsVault


class Config(BaseModel):
    vcs_vaults: list[VcsVault] = []

    @classmethod
    def from_pyproject_toml(cls, project_root: Path) -> "Config":
        pyproject_toml_path = project_root / "pyproject.toml"
        if not pyproject_toml_path.is_file():
            return Config()
        pyproject_toml = tomllib.loads(pyproject_toml_path.read_text(encoding="utf-8"))
        config_dict = pyproject_toml.get("tool", {}).get(
            "pip-preserve-requirements", {}
        )
        return Config(**config_dict)
