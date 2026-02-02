# Contributing to CP4I Chief Console

Thank you for your interest in contributing to the CP4I Chief Console! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/chief-console.git
   cd chief-console
   ```
3. **Set up your development environment** (see below)

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Your environment details (OS, Python version, OpenShift version)
- Relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any implementation ideas you have

### Pull Requests

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Test your changes thoroughly

4. Commit with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: brief description"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/examples if applicable

## Development Setup

### Prerequisites

- Python 3.8 or higher
- OpenShift CLI (`oc`) installed and configured
- Access to a CP4I environment (TechZone or other)

### Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up configuration:
   ```bash
   cp config.local.yaml.example config.local.yaml
   cp environments.example.yaml environments.yaml
   ```

4. Configure your environment credentials in `environments.yaml`

### Running Tests

```bash
# Run basic functionality test
python chief_console.py

# Run specific test modules (when available)
python -m pytest tests/
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

### Code Organization

- Place new collectors in `src/collector_*.py`
- Place utilities in `src/` with descriptive names
- Keep templates in `templates/`
- Document new configuration options in `config.yaml`

### Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update docstrings when modifying functions
- Include examples in documentation

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add Kafka consumer lag monitoring`
- `fix: Correct namespace discovery logic`
- `docs: Update installation instructions`
- `refactor: Simplify profile builder logic`

## Submitting Changes

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits

### Pull Request Process

1. Ensure your PR has a clear title and description
2. Link related issues using keywords (e.g., "Fixes #123")
3. Request review from maintainers
4. Address review feedback promptly
5. Keep your branch up to date with main

### Review Process

- Maintainers will review PRs within a few days
- Feedback may be provided for improvements
- Once approved, maintainers will merge your PR

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the "question" label
- Reach out to maintainers

Thank you for contributing to CP4I Chief Console! 🚀