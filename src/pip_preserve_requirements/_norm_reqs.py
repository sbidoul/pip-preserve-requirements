# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import re

_NORMALIZE_REQ_LINE_RE = re.compile(
    r"^(?P<name>[a-zA-Z0-9-_.\[\]]+)(?P<arobas>\s*@\s*)(?P<rest>.*)$"
)


def normalize_req_line(req_line: str) -> str:
    mo = _NORMALIZE_REQ_LINE_RE.match(req_line)
    if not mo:
        return req_line
    return mo.group("name") + " @ " + mo.group("rest")


def normalize_req_lines(req_lines: str) -> str:
    req_lines_list = []
    for req_line in req_lines.splitlines():
        req_lines_list.append(normalize_req_line(req_line))
    return "\n".join(req_lines_list) + "\n"
