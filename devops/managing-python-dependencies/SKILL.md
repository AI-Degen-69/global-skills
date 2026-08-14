---
name: managing-python-dependencies
description: Use when adding, changing, or running Python deps - prefer venv over global pip.
license: Apache-2.0
metadata:
  version: v1
  publisher: google
---

# Python Dependency Management Rule

> [!CAUTION] **BEFORE any `pip install`**: You MUST first detect the project's
> existing dependency manager and use it correctly. Do NOT override the
> project's established tooling.

## Dependency Manager Detection

Before installing ANY Python package, check the workspace for these files **in
priority order**:

1.  **Signal:** `uv.lock` or `pyproject.toml` with `[tool.uv]`
    *   **Tool:** **uv**
    *   **Install:** `uv add <package>`
    *   **Setup:** `uv sync`
2.  **Signal:** `pyproject.toml` with `[tool.poetry]`
    *   **Tool:** **Poetry**
    *   **Install:** `poetry add <package>`
    *   **Setup:** `poetry install`
3.  **Signal:** `Pipfile`
    *   **Tool:** **Pipenv**
    *   **Install:** `pipenv install <package>`
    *   **Setup:** `pipenv install`
4.  **Signal:** `environment.yml`
    *   **Tool:** **Conda**
    *   **Install:** `conda install <package>`
    *   **Setup:** `conda env create -f environment.yml`
5.  **Signal:** `requirements.txt` only
    *   **Tool:** **venv + pip**
    *   **Install:** `.venv/bin/pip install <package>`
    *   **Setup:** `.venv/bin/pip install -r requirements.txt`
6.  **Signal:** None of the above
    *   **Tool:** **venv + pip** (default)
    *   **Install:** `.venv/bin/pip install <package>`
    *   **Setup:** `.venv/bin/pip install -r requirements.txt`

## Default: venv + pip

If no dependency manager is detected, use **venv + pip + requirements.txt** as
the default:

```bash
# Initialize environment
python3 -m venv .venv

# Add dependencies
.venv/bin/pip install <package>

# Preserve state
.venv/bin/pip freeze > requirements.txt
```

**Rules for venv + pip workflow:**

-   Always use `.venv/bin/pip` or `.venv/bin/python` (explicit path).
-   After installing, run: `.venv/bin/pip freeze > requirements.txt`.
-   When setting up: `.venv/bin/pip install -r requirements.txt`.

## Prohibited

-   **NEVER** run `pip install` globally
-   **NEVER** override an existing dependency manager with a different one

## Note: Virtual Environment Awareness

In complex environments with multiple virtual environments (e.g., a project venv and a tool-specific venv), always verify you are using the correct interpreter and pip. The safest way is to use the explicit path to the Python executable in the target virtual environment and run `-m pip`:

```bash
/path/to/venv/bin/python -m pip list   # to see installed packages
/path/to/venv/bin/python -m pip install <package>
```

On Windows, the path might be `\\path\\to\\venv\\Scripts\\python.exe`.

Alternatively, activate the virtual environment first and then use `pip` and `python` (but be cautious of which environment is activated).

This avoids mistakes with path variations (like `bin` vs `Scripts` on Unix vs Windows) and ensures you are modifying the intended environment.
