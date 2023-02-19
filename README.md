# pip-preserve-requirements

[![PyPI - Version](https://img.shields.io/pypi/v/pip-preserve-requirements.svg)](https://pypi.org/project/pip-preserve-requirements)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pip-preserve-requirements.svg)](https://pypi.org/project/pip-preserve-requirements)

-----

Ensure pinned VCS requirements in a pip requirements file have a tag associated with the
commit sha, so they are preserved from garbage collection.

**Table of Contents**

- [pip-preserve-requirements](#pip-preserve-requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [License](#license)

## Installation

```console
pipx install pip-preserve-requirements
```

## Configuration

`pip-preserve-requirements` is configured in a dedicated section of `pyproject.toml`:

Example:

```toml
[[tool.pip-preserve-requirements.vaults]]

```

## License

`pip-preserve-requirements` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
