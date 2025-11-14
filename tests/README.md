# SLPlayer Test Suite

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_device_id.py
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test
```bash
pytest tests/test_device_id.py::test_get_device_id
```

### Run with coverage (requires pytest-cov)
```bash
pytest --cov=. --cov-report=html
```

## Test Structure

- `test_device_id.py` - Tests for device ID generation
- `test_license_verifier.py` - Tests for license verification
- `test_base_controller.py` - Tests for base controller functionality

## Adding New Tests

1. Create test file: `tests/test_<module_name>.py`
2. Import the module to test
3. Write test functions starting with `test_`
4. Use fixtures from `conftest.py` for common test data

## Test Fixtures

- `temp_config_dir` - Temporary config directory
- `sample_program_data` - Sample program data
- `mock_controller_info` - Mock controller device info

