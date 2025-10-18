# 🚀 State-of-the-Art CI Workflow for Python Projects

This document provides a modern, efficient CI workflow template that replaces outdated tools with cutting-edge alternatives. Perfect for Python projects using Ruff, modern GitHub Actions, and current Python versions.

## 🎯 What Makes This SOTA?

### **Modern Tool Stack**
- ✅ **Ruff** replaces Black + isort + flake8 (10-100x faster)
- ✅ **Python 3.10+** minimum (3.9 is EOL)
- ✅ **Latest GitHub Actions** (v5, v4)
- ✅ **Streamlined workflow** (no redundant jobs)

### **Key Improvements Over Legacy CI**
- 🚀 **10-100x faster** linting with Ruff
- 🔧 **Single tool** instead of multiple formatters/linters
- 📦 **Consolidated dependencies** installation
- 🎯 **Focused jobs** without duplication
- 🔒 **Modern security** scanning

## 📋 Complete CI Workflow Template

### **`.github/workflows/ci.yml`**

```yaml
name: CI - Quality Assurance

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.10'

jobs:
  quality-assurance:
    name: Quality Assurance
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        include:
          - python-version: "3.10"
            coverage: true

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache pip dependencies
      uses: actions/cache@v4
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-${{ matrix.python-version }}-
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install ruff mypy pytest pytest-cov pytest-xdist

    - name: Linting and formatting (Ruff)
      run: |
        ruff check src/ --output-format=github
        ruff format --check src/

    - name: Type checking (mypy)
      run: |
        mypy src/ --ignore-missing-imports

    - name: Security scanning (bandit)
      run: |
        pip install bandit
        bandit -r src/ -f json -o bandit-report.json || true

    - name: Run tests
      run: |
        pytest -v --cov=src/ --cov-report=term-missing --cov-report=xml --cov-report=html --junitxml=test-results.xml

    - name: Build Python package
      run: |
        pip install build
        python -m build

    - name: Validate package
      run: |
        pip install twine
        twine check dist/*

    - name: Upload coverage reports
      if: matrix.coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

    - name: Upload test results
      uses: actions/upload-artifact@v4
      with:
        name: test-results-py${{ matrix.python-version }}
        path: |
          test-results.xml
          coverage.xml
          htmlcov/
          bandit-report.json
        retention-days: 30

  windows-compatibility:
    name: Windows Compatibility
    runs-on: windows-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Basic import test
      run: |
        python -c "import sys; sys.path.insert(0, 'src'); import your_package; print('✅ Import successful')"

    - name: Run basic tests
      run: |
        pip install pytest
        pytest tests/test_basic.py -v

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v3
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  dependency-review:
    name: Dependency Review
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Dependency Review
      uses: actions/dependency-review-action@v4
      with:
        config-file: '.github/dependency-review-config.yml'
```

## ⚙️ Ruff Configuration

### **`pyproject.toml`**

```toml
[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E402", # Module level import not at top of file (intentional in some cases)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
disallow_untyped_calls = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true

[[tool.mypy.overrides]]
module = ["third_party.*"]
ignore_missing_imports = true
```

## 📦 Dependencies

### **`requirements.txt`**
```txt
# Core dependencies
ruff>=0.1.0
mypy>=1.0.0
pytest>=7.0.0
pytest-cov>=3.0.0
pytest-xdist>=3.0.0
bandit>=1.7.0
build>=0.10.0
twine>=4.0.0
```

## 🔧 Customization Guide

### **1. Adjust Python Versions**
```yaml
# For different minimum versions
env:
  PYTHON_VERSION: '3.11'  # Change minimum version

strategy:
  matrix:
    python-version: ["3.11", "3.12"]  # Adjust matrix
```

### **2. Modify Source Path**
```yaml
# Change from 'src/' to your package structure
ruff check your_package/ --output-format=github
mypy your_package/ --ignore-missing-imports
bandit -r your_package/ -f json -o bandit-report.json || true
pytest -v --cov=your_package/ --cov-report=term-missing
```

### **3. Add Package-Specific Steps**
```yaml
# Add after "Install dependencies"
- name: Install package-specific dependencies
  run: |
    pip install -r requirements-dev.txt  # If you have dev requirements
    pip install -r requirements-test.txt  # If you have test requirements
```

### **4. Custom Ruff Rules**
```toml
[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "B", "C4", "UP",  # Basic rules
    "S",  # flake8-bandit (security)
    "TCH", # flake8-type-checking
    "SIM", # flake8-simplify
]
ignore = [
    "E402",  # Module level import not at top
    "S101",  # Use of assert detected
    "TCH001", # Move standard library import into TYPE_CHECKING
]
```

## 🚀 Migration from Legacy CI

### **What This Replaces:**
- ❌ **Black** → ✅ **Ruff format**
- ❌ **isort** → ✅ **Ruff import sorting**
- ❌ **flake8** → ✅ **Ruff linting**
- ❌ **pylint** → ✅ **Ruff + mypy**
- ❌ **Python 3.9** → ✅ **Python 3.10+**

### **Migration Steps:**
1. **Replace** old CI workflow with template
2. **Update** `pyproject.toml` with Ruff config
3. **Remove** old tool configurations (Black, isort, flake8)
4. **Update** dependencies in `requirements.txt`
5. **Test** locally with `ruff check` and `ruff format`

## 📊 Performance Comparison

| Tool | Speed | Features | Maintenance |
|------|-------|----------|-------------|
| **Ruff** | 🚀 **10-100x faster** | All-in-one | ✅ **Low** |
| Black + isort + flake8 | 🐌 Slow | Multiple tools | ❌ **High** |
| pylint | 🐌 Slow | Heavy | ❌ **High** |

## 🎯 Benefits

### **For Developers:**
- ⚡ **Faster CI runs** (minutes → seconds)
- 🔧 **Single tool** to learn and configure
- 📝 **Better error messages** with GitHub integration
- 🎨 **Consistent formatting** across team

### **For Projects:**
- 💰 **Lower CI costs** (faster runs)
- 🔒 **Better security** scanning
- 📈 **Higher code quality** with modern rules
- 🚀 **Future-proof** with latest tools

## 🔗 Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Python Packaging Guide](https://packaging.python.org/)
- [Mypy Documentation](https://mypy.readthedocs.io/)

## 📝 License

This template is provided under MIT License. Feel free to use, modify, and distribute.

---

**🎉 Enjoy your blazing-fast, modern CI workflow!** 🚀
