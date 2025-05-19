# CHAI Agent Playground Test Suite

This directory contains unit tests for the CHAI Agent Playground application.

## Setup

Before running the tests, make sure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/services/test_character_sandbox_service.py
```

To run a specific test class:

```bash
pytest tests/services/test_character_sandbox_service.py::TestCharacterSandboxService
```

To run a specific test method:

```bash
pytest tests/services/test_character_sandbox_service.py::TestCharacterSandboxService::test_post_process_character_name_generation_response
```

## Test Coverage

To run tests with coverage report:

```bash
pytest --cov=app tests/
```

## Test Structure

- `conftest.py`: Contains shared fixtures used across multiple test files
- `services/`: Tests for service layer components
  - `test_character_sandbox_service.py`: Tests for the CharacterSandboxService class

## Mocking Strategy

The tests use pytest-mock to mock external dependencies:

- `CHAIAPIClient`: Mocked to avoid making actual API calls
- `validate_chai_api_key`: Mocked to avoid needing an actual API key

## Adding New Tests

When adding new tests:

1. Create a new test file in the appropriate directory
2. Import the necessary fixtures from conftest.py
3. Use the pytest.mark.asyncio decorator for async tests
4. Follow the existing test patterns for consistency
