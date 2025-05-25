# pip-preserve-requirements

[![PyPI - Version](https://img.shields.io/pypi/v/pip-preserve-requirements.svg)](https://pypi.org/project/pip-preserve-requirements)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pip-preserve-requirements.svg)](https://pypi.org/project/pip-preserve-requirements)

-----

Preserve pinned PIP requirements in repositories you control.

It ensure pinned git references in pip requirements files are pushed to a repo you
control, and have a tag associated with the commit, so they are preserved from garbage
collection.

**Table of Contents**

- [pip-preserve-requirements](#pip-preserve-requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [Limitations](#limitations)
  - [License](#license)

## Installation

```console
pipx install pip-preserve-requirements
```

## Usage

```text
Usage: pip-preserve-requirements [OPTIONS] REQUIREMENTS_FILE...

  Ensure pinned VCS references in pip requirements files have a git tag.

Arguments:
  REQUIREMENTS_FILE...  The requirements files to look for requirements tag.
                        [required]

Options:
  --tag-prefix TEXT               The prefix to use when creating git tag
                                  names.  [default: ppr-]
  --match-any-tag                 Whether to consider that any tag on the
                                  commit is sufficient. If not, ensure commits
                                  are tagged with the requested prefix.
  -r, --project-root DIRECTORY    The project root directory. Default options
                                  and arguments are read from pyproject.toml
                                  in this directory.  [default: .]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```

## Configuration

`pip-preserve-requirements` is configured in a dedicated section of `pyproject.toml`:

Example:

```toml
[tool.pip-preserve-requirements]
tag_prefix = "ppr+"
# ensure a tag with the above prefix is present, if true, consider any tag is valid
match_any_tag = false

[[tool.pip-preserve-requirements.vcs_vaults]]
# any git provider which accepts URLs of the form https://host/owner/repo
# or ssh://git@host/owner/repo
provider = "github.com"
owner = "acme"
# set to true for private repos
ssh_only = false
# the vault where to push VCS reference
default = true
```

## Limitations

At the moment, only `git+https` and `git+ssh` URLs are supported.

The following improvements would be considered in scope, although there is no current
plan to work on them:

- supporting other VCS (such as `hg`);
- supporting non-VCS URLs, by pushing them to a user-controlled server;
- supporting regular requirements, by pushing them to a user-controlled index;
- supporting other lockfile formats (pylock.toml, uv.lock, ...).

## License

`pip-preserve-requirements` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
