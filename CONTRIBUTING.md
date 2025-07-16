# Contributing to DataAptor AI

Thank you for your interest in contributing to DataAptor AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Please be considerate of differing viewpoints and experiences, and focus on what is best for the community and the project.

## Getting Started

1. **Fork the Repository**: Create your own fork of the repository on GitHub.

2. **Clone Your Fork**: 
   ```bash
   git clone https://github.com/your-username/data-aptor-ai.git
   cd data-aptor-ai
   ```

3. **Set Up Development Environment**:
   Follow the instructions in the [Development Guide](docs/development/README.md) to set up your local development environment.

4. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   
   Naming conventions for branches:
   - `feature/` - for new features
   - `bugfix/` - for bug fixes
   - `docs/` - for documentation changes
   - `refactor/` - for code refactoring
   - `test/` - for adding or modifying tests

## Development Process

1. **Align with Roadmap**: Review the [Implementation Roadmap](docs/implementation-roadmap.md) to ensure your contribution aligns with the project's goals and timeline.

2. **Check Existing Issues**: Look for open issues that you can help with, or create a new issue to discuss your proposed changes before starting work.

3. **Development Steps**:
   - Make your changes in your feature branch
   - Add appropriate tests for your changes
   - Update documentation as needed
   - Ensure all tests pass
   - Follow the coding standards

## Pull Request Process

1. **Update Your Fork**: Before submitting a pull request, update your fork with the latest changes from the main repository:
   ```bash
   git remote add upstream https://github.com/AneeshPulukkul/data-aptor-ai.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   git checkout your-branch-name
   git rebase main
   ```

2. **Submit Your Pull Request**: Push your changes to your fork and submit a pull request to the main repository.

3. **PR Description**: In your pull request description:
   - Reference any related issues
   - Describe the changes you've made
   - Mention any breaking changes
   - List any dependencies that were added or removed

4. **Code Review**: Your pull request will be reviewed by maintainers. Be open to feedback and make necessary changes.

5. **Merge**: Once approved, a maintainer will merge your pull request.

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where appropriate
- Document functions and classes using docstrings
- Maximum line length: 100 characters

### JavaScript/TypeScript

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ES6+ features when possible
- Document functions and components with JSDoc comments
- Maximum line length: 100 characters

### General Guidelines

- Keep functions and methods small and focused
- Write self-documenting code with clear variable and function names
- Use comments to explain complex logic, not to describe what the code does
- Organize imports alphabetically
- Add appropriate error handling

## Testing Guidelines

- Write unit tests for all new code
- Ensure all tests pass before submitting a pull request
- Aim for at least 80% code coverage for new code
- Include integration tests for API endpoints and service interactions
- Test edge cases and error conditions

## Documentation

- Update documentation for any changes to APIs, CLIs, or user-facing features
- Use clear and concise language
- Include code examples where appropriate
- Ensure documentation is accessible and easy to understand

## Issue Reporting

When reporting issues, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots or logs if applicable
- Your environment (OS, browser, version, etc.)

---

Thank you for contributing to DataAptor AI! Your efforts help make this project better for everyone.
