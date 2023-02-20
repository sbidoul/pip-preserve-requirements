# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import typer


_verbosity = 0


def increase_verbosity() -> None:
    global _verbosity
    _verbosity += 1


def decrease_verbosity() -> None:
    global _verbosity
    _verbosity -= 1


def log_debug(msg: str) -> None:
    if _verbosity > 0:
        typer.secho(msg, dim=True, err=True)


def log_info(msg: str, nl: bool = True) -> None:
    typer.secho(msg, fg=typer.colors.BRIGHT_BLUE, err=True, nl=nl)


def log_notice(msg: str, nl: bool = True) -> None:
    typer.secho(msg, fg=typer.colors.GREEN, err=True, nl=nl)


def log_warning(msg: str) -> None:
    typer.secho(msg, fg=typer.colors.YELLOW, err=True)


def log_error(msg: str) -> None:
    typer.secho(msg, fg=typer.colors.RED, err=True)
