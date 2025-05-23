# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

import dataclasses
import re
from typing import Optional
from urllib.parse import SplitResult, urlsplit


class UnsupportedVcsUrlError(Exception):
    pass


_PATH_RE = re.compile(
    r"^/(?P<owner>[^/]+)/(?P<repo>[^/@]+)@(?P<revision>[a-z0-9]{40})$"
)


@dataclasses.dataclass
class PipVcsUrl:
    scheme: str
    username: Optional[str]
    password: Optional[str]
    hostname: str
    owner: str
    repo: str
    revision: str
    query: Optional[str]
    fragment: Optional[str]

    @classmethod
    def from_url(cls, url: str) -> "PipVcsUrl":
        try:
            split_result = urlsplit(url)
        except Exception as e:
            raise UnsupportedVcsUrlError(url) from e
        if split_result.scheme not in ("git+ssh", "git+https"):
            raise UnsupportedVcsUrlError(url)
        if not split_result.hostname:
            raise UnsupportedVcsUrlError(url)
        mo = _PATH_RE.match(split_result.path)
        if mo is None:
            raise UnsupportedVcsUrlError(url)
        return cls(
            scheme=split_result.scheme,
            username=split_result.username,
            password=split_result.password,
            hostname=split_result.hostname,
            owner=mo.group("owner"),
            repo=mo.group("repo"),
            revision=mo.group("revision"),
            query=split_result.query,
            fragment=split_result.fragment,
        )

    @property
    def vcs(self) -> str:
        return self.scheme.split("+")[0]

    @property
    def provider(self) -> str:
        return self.hostname

    @property
    def netloc(self) -> str:
        if self.username and self.password:
            return f"{self.username}:{self.password}@{self.hostname}"
        elif self.username:
            return f"{self.username}@{self.hostname}"
        return self.hostname

    @property
    def path(self) -> str:
        return f"/{self.owner}/{self.repo}@{self.revision}"

    def vcs_url(self, for_push: bool = False) -> str:
        """The URL, suitable for passing to the VCS CLI."""
        if for_push:
            scheme = "ssh"
            netloc = f"git@{self.hostname}"
        else:
            scheme = self.scheme.split("+")[1]
            netloc = self.netloc
        return SplitResult(
            scheme,
            netloc,
            f"/{self.owner}/{self.repo}",
            "",
            "",
        ).geturl()

    def __str__(self) -> str:
        return SplitResult(
            self.scheme,
            self.netloc,
            self.path,
            self.query or "",
            self.fragment or "",
        ).geturl()

    def with_provider(
        self, provider: str, owner: str, ssh_only: bool = False
    ) -> "PipVcsUrl":
        scheme = self.scheme
        username = self.username
        password = self.password
        if ssh_only:
            scheme = "git+ssh"
            username = "git"
            password = None
        return dataclasses.replace(
            self,
            scheme=scheme,
            username=username,
            password=password,
            hostname=provider,
            owner=owner,
        )
