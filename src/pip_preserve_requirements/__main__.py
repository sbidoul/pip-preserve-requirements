# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any

import typer

from ._cache import Cache
from ._compat import tomllib
from ._config import Config
from ._tag_name_factory import TagNameFactory
from ._tag_requirements import tag_requirements_files

app = typer.Typer()


def _project_root_callback(
    ctx: typer.Context,
    _param: Any,
    value: Path,
) -> Path:
    """Load default values from pyproject.toml."""
    pyproject_toml_path = value / "pyproject.toml"
    if pyproject_toml_path.is_file():
        ctx.default_map = (
            tomllib.loads(pyproject_toml_path.read_text(encoding="utf-8"))
            .get("tool", {})
            .get("pip-preserve-requirements", {})
        )
    return value


@app.command()
def command(
    requirements_files: list[Path] = typer.Argument(  # noqa: B008
        ...,
        metavar="REQUIREMENTS_FILE...",
        file_okay=True,
        dir_okay=False,
        exists=True,
        help=("The requirements files to look for requirements tag."),
    ),
    *,
    tag_prefix: str = typer.Option(
        "ppr-", "--tag-prefix", help="The prefix to use when creating git tag names."
    ),
    match_any_tag: bool = typer.Option(
        False,
        "--match-any-tag",
        help=(
            "Whether to consider that any tag on the commit is sufficient. "
            "If not, ensure commits are tagged with the requested prefix."
        ),
    ),
    project_root: Path = typer.Option(  # noqa: B008
        ".",
        "--project-root",
        "-r",
        # Process this parameter first so we can load default values from pyproject.toml
        is_eager=True,
        callback=_project_root_callback,
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
        help=(
            "The project root directory. "
            "Default options and arguments "
            "are read from pyproject.toml in this directory."
        ),
    ),
) -> None:
    """Ensure pinned VCS references in pip requirements files have a git tag."""
    config = Config.from_pyproject_toml(project_root)
    cache = Cache(project_root)
    tag_name_factory = TagNameFactory(tag_prefix, match_any_tag)
    tag_requirements_files(
        requirements_files, config.vcs_vaults, cache, tag_name_factory
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
