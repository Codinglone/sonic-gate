# Contributing to Sonic Gate

Thank you for your interest in contributing! This document provides guidelines for contributing to Sonic Gate.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the [existing issues](https://github.com/Codinglone/sonic-gate/issues) to see if the problem has already been reported.

When filing a bug report, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, Sonic Gate version, FFmpeg version)
- A sample file if applicable

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature has already been suggested
- Provide a clear use case
- Explain why it would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run the test suite (`pytest`)
5. Commit with a clear message
6. Push to your fork and open a Pull Request

## Development Setup

```bash
git clone https://github.com/Codinglone/sonic-gate.git
cd sonic-gate
pip install -e ".[dev]"
```

## Code Style

- Follow PEP 8
- Use `black` for formatting (`black sonic_gate tests`)
- Add type hints where appropriate
- Write docstrings for public functions

## Testing

All changes should include tests. Run the full suite:

```bash
pytest
```

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add new analyzer`
- `fix: correct LUFS threshold calculation`
- `docs: update README with examples`
- `test: add coverage for video extraction`

## Release Process

Releases are managed by the maintainer. Version bumps follow [SemVer](https://semver.org/).

## Questions?

Open a [Discussion](https://github.com/Codinglone/sonic-gate/discussions) or reach out via GitHub issues.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
