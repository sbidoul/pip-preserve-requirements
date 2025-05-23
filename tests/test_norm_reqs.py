# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import textwrap

from pip_preserve_requirements._norm_reqs import normalize_req_lines


def test_normalize_req_lines() -> None:
    assert normalize_req_lines(
        textwrap.dedent(
            """\
                prj
                prj==1.0
                name @https://g.c/o/p@branch
                name@https://g.c/o/p@branch
                name[extra] @https://g.c/o/p@branch
                """
        )
    ) == textwrap.dedent(
        """\
                prj
                prj==1.0
                name @ https://g.c/o/p@branch
                name @ https://g.c/o/p@branch
                name[extra] @ https://g.c/o/p@branch
            """
    )
