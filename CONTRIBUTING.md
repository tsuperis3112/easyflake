# Contributing Guidelines

## Reporting Issues and Requesting Features

Please report any issues or feature requests by creating a new issue on the GitHub repository.

## Development Guide

We welcome contributions to easyflake! To contribute, please follow these steps:

1. Fork the repository and clone your forked repository to your local machine.
1. Create a new branch for your changes: `git checkout -b my-new-branch`
1. Make changes to the code.
1. Add, commit, and push your changes: `git add . && git commit -m "Add some feature" && git push origin my-new-branch`
1. Open a pull request.

Before creating a pull request, please make sure your changes meet the following guidelines:

* Your code should follow the PEP 8 style guide.
* Your code should be well-documented with clear comments explaining its purpose and any algorithms used.
* Your code should include tests for any new features or bug fixes.

### Dependencies

easyflake uses [Poetry](https://python-poetry.org/) for package management. You can install dependencies using the following command:

```bash
poetry install -E all
```

### Testing

We use pytest for testing. You can run the tests with the following command:

```bash
poetry run pytest --cov=easyflake
```

Make sure that all tests pass before submitting your contribution.

### Code Formatting

This project uses the following code formatters and linters:

* [`black`](https://black.readthedocs.io/en/stable/)
* [`flake8`](https://flake8.pycqa.org/en/latest/)
* [`isort`](https://pycqa.github.io/isort/)
* [`mypy`](https://mypy.readthedocs.io/en/stable/)

We recommend to use [pre-commit](https://pre-commit.com/) for code formatting. pre-commit will check that your code is correctly formatted before each commit.

Install the pre-commit hooks with the following command:

```bash
pre-commit install
```

Now, pre-commit will automatically run the code formatter and linter before each commit.
