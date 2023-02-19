# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@gmail.com>
# SPDX-License-Identifier: MIT

from pydantic import BaseModel


class VcsVault(BaseModel):
    provider: str
    owner: str
    ssh_only: bool = False
    default: bool = False

    def repo_url(self, repo: str, for_push: bool = True) -> str:
        if for_push or self.ssh_only:
            return f"ssh://git@{self.provider}/{self.owner}/{repo}"
        else:
            return f"https://{self.provider}/{self.owner}/{repo}"
