# dds_glossary

[![PyPI](https://img.shields.io/pypi/v/dds_glossary.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/dds_glossary.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/dds_glossary)][pypi status]
[![License](https://img.shields.io/pypi/l/dds_glossary)][license]

[![Read the documentation at https://dds_glossary.readthedocs.io/](https://img.shields.io/readthedocs/dds_glossary/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/Depart-de-Sentier/dds_glossary/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/Depart-de-Sentier/dds_glossary/branch/main/graph/badge.svg)][codecov]
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)][security_bandit]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/dds_glossary/
[read the docs]: https://dds_glossary.readthedocs.io/
[tests]: https://github.com/Depart-de-Sentier/dds_glossary/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/Depart-de-Sentier/dds_glossary
[security_bandit]: https://github.com/PyCQA/bandit
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

Sustainability assessment classifications glossary.

## Shell Utilities for `dds_glossary`

`tasks.py` provides shell utilities for the `dds_glossary` project, utilizing `invoke` for task execution. Below are the tasks available:

### Clean Task
Cleans up the project directory by removing specified files and directories.

#### Usage
```sh
invoke clean [--bytecode] [--pytest] [--mypy] [--extra <extra_patterns>]
```

#### Options
- `bytecode` `"-b"`: Cleans up compiled Python files.
- `pytest` `"-p"`: Cleans up pytest cache and coverage files.
- `mypy` `"-m"`: Cleans up mypy cache files.
- `extra` `"-e"`: Specifies additional directories or files to clean up.

### Install Task
Installs the project with optional modes and dependencies.

#### Usage
```sh
invoke install [--editable] [--testing] [--dev] [--report]
```

#### Options
- `editable` `"-e"`: Installs the project in editable mode.
- `testing` `"-t"`: Installs test dependencies.
- `dev` `"-d"`: Installs development dependencies.
- `report` `"-r"`: Displays the command output.

### Precommit Task
Runs pre-commit checks to ensure code quality and consistency.

#### Usage
```sh
invoke precommit
```

### Test Task
Runs unit and integration tests for the project.

#### Usage
```sh
invoke test [--integration] [--report]
```

#### Options
- `integration` `"-i"`: Runs integration tests.
- `report` `"-r"`: Displays the command output.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [BSD-3-Clause][License],
_pyilcd_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://dds_glossary.readthedocs.io/en/latest/usage.html
[License]: https://github.com/Depart-de-Sentier/dds_glossary/blob/main/LICENSE
[Contributor Guide]: https://github.com/Depart-de-Sentier/dds_glossary/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/Depart-de-Sentier/dds_glossary/issues
