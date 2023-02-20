# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pytest import CaptureFixture

from pip_preserve_requirements._utils import (
    decrease_verbosity,
    increase_verbosity,
    log_debug,
    log_error,
    log_info,
    log_notice,
    log_warning,
)


def test_log_debug(capsys: CaptureFixture[str]) -> None:
    log_debug("debug")
    assert "debug" not in capsys.readouterr().err
    increase_verbosity()
    try:
        log_debug("debug")
        assert capsys.readouterr().err == "debug\n"
    finally:
        decrease_verbosity()


def test_log_info(capsys: CaptureFixture[str]) -> None:
    log_info("in", nl=False)
    log_info("fo")
    assert capsys.readouterr().err == "info\n"


def test_log_notice(capsys: CaptureFixture[str]) -> None:
    log_notice("in", nl=False)
    log_notice("fo")
    assert capsys.readouterr().err == "info\n"


def test_log_warning(capsys: CaptureFixture[str]) -> None:
    log_warning("warning")
    assert capsys.readouterr().err == "warning\n"


def test_log_error(capsys: CaptureFixture[str]) -> None:
    log_error("error")
    assert capsys.readouterr().err == "error\n"
