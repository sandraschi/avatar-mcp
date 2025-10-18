# SOTA Python CI Template

This directory contains a complete, reusable CI workflow template for modern Python projects.

## 📁 Template Structure

```
.github/
├── workflows/
│   └── ci.yml                    # Main CI workflow
├── dependency-review-config.yml  # Dependency review config
└── templates/                    # Reusable templates
    ├── ci-workflow.yml           # CI workflow template
    ├── ruff-config.toml          # Ruff configuration
    └── pyproject-template.toml   # Complete pyproject.toml
```

## 🚀 Quick Setup

### 1. Copy CI Workflow
```bash
cp .github/templates/ci-workflow.yml .github/workflows/ci.yml
```

### 2. Merge Ruff Config
```bash
# Add to your pyproject.toml
cat .github/templates/ruff-config.toml >> pyproject.toml
```

### 3. Update Dependencies
```bash
# Add to requirements.txt
echo "ruff>=0.1.0" >> requirements.txt
echo "mypy>=1.0.0" >> requirements.txt
echo "pytest>=7.0.0" >> requirements.txt
echo "pytest-cov>=3.0.0" >> requirements.txt
echo "bandit>=1.7.0" >> requirements.txt
```

## 🔧 Customization Variables

Replace these placeholders in the templates:

- `{{PROJECT_NAME}}` → Your project name
- `{{PACKAGE_NAME}}` → Your package name (e.g., `src/your_package/`)
- `{{MIN_PYTHON_VERSION}}` → Minimum Python version (e.g., `3.10`)
- `{{PYTHON_MATRIX}}` → Python versions to test (e.g., `["3.10", "3.11", "3.12"]`)

## 📊 Template Features

### ✅ Included
- Ultra-fast Ruff linting and formatting
- Modern Python 3.10+ support
- Latest GitHub Actions (v5, v4)
- Comprehensive testing with pytest
- Security scanning with Bandit + Trivy
- Type checking with mypy
- Cross-platform compatibility
- Package building and validation
- Dependency review
- Coverage reporting

### ❌ Removed (Outdated)
- Black (replaced by Ruff)
- isort (replaced by Ruff)
- flake8 (replaced by Ruff)
- Python 3.9 (EOL)
- Old GitHub Actions versions
- Redundant quality metrics jobs
- Deprecated output syntax

## 🎯 Performance Comparison

| Tool | Speed | Lines/sec | Memory |
|------|-------|-----------|---------|
| **Ruff** | 🚀 **10-100x faster** | 100k+ | Low |
| Black + isort + flake8 | 🐌 Slow | 1k-5k | High |
| pylint | 🐌 Slow | 500-2k | Very High |

## 🔗 Integration Examples

### For Data Science Projects
```yaml
# Add to ci.yml
- name: Install data science dependencies
  run: |
    pip install numpy pandas matplotlib seaborn
    pip install jupyter notebook
```

### For Web Applications
```yaml
# Add to ci.yml
- name: Install web dependencies
  run: |
    pip install fastapi uvicorn
    pip install pytest-asyncio httpx
```

### For ML/AI Projects
```yaml
# Add to ci.yml
- name: Install ML dependencies
  run: |
    pip install torch tensorflow scikit-learn
    pip install pytest-mock
```

## 📝 Usage Examples

### Basic Python Package
```bash
# 1. Copy template
cp .github/templates/ci-workflow.yml .github/workflows/ci.yml

# 2. Replace placeholders
sed -i 's/{{PACKAGE_NAME}}/src\/mypackage/g' .github/workflows/ci.yml
sed -i 's/{{PROJECT_NAME}}/mypackage/g' .github/workflows/ci.yml

# 3. Add Ruff config
cat .github/templates/ruff-config.toml >> pyproject.toml
```

### FastAPI Application
```bash
# 1. Copy template
cp .github/templates/ci-workflow.yml .github/workflows/ci.yml

# 2. Customize for FastAPI
sed -i 's/{{PACKAGE_NAME}}/app/g' .github/workflows/ci.yml
sed -i 's/{{PROJECT_NAME}}/fastapi-app/g' .github/workflows/ci.yml

# 3. Add FastAPI-specific dependencies
echo "fastapi>=0.100.0" >> requirements.txt
echo "uvicorn>=0.20.0" >> requirements.txt
echo "pytest-asyncio>=0.21.0" >> requirements.txt
```

## 🎉 Benefits

### For Developers
- ⚡ **Blazing fast** CI runs
- 🔧 **Single tool** to learn
- 📝 **Better error messages**
- 🎨 **Consistent formatting**

### For Projects
- 💰 **Lower CI costs**
- 🔒 **Better security**
- 📈 **Higher code quality**
- 🚀 **Future-proof**

## 📚 Documentation

- [Complete Setup Guide](../SOTA_CI_WORKFLOW.md)
- [GitHub Template README](../GITHUB_TEMPLATE_README.md)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

**🎯 Ready to modernize your Python CI? Use these templates!** 🚀
