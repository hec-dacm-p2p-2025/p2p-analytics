# Installation

## 1. Clone the main project repository

```bash
git clone https://github.com/hec-dacm-p2p-2025/final-project.git
cd final-project/phase2_package
```

## 2. Create and activate a virtual environment

**Windows**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install the package in editable mode

```bash
pip install -e ".[dev]"
```
This install all required runtime dependencies and all developer tools: `pytest`, `ruff`, `mypy`, `mkdocs`, etc.

## 4. Verify installation

Open a Python shell and run: 

```python
import p2p_analytics
p2p_analytics.__version__
```

If no error appears, the package is successfully installed.