# MobileFarm

MobileFarm is a Python-based project designed to manage and interact with mobile devices. It includes tools, plugins, and templates for working with various Android phones, and provides a framework for testing and automation.

## Features

- **Device Management**: Includes modules for managing specific devices like Pixel 8 Pro.
- **Plugins**: Extend functionality with plugins.
- **Testing Framework**: Support for a comprehensive testing setup using `pytest`.
- **Results Reporting**: Generates detailed test reports in HTML and XML formats.

## Project Structure

```bash
mobilefarm/
    devices/        # Modules for specific devices
    lib/            # Core libraries, including GUI support
    plugins/        # Extendable plugins for additional functionality
    templates/      # Templates for device-specific operations
results/            # Test results and reports
    pytest_run_report.html
    pytest_run_report.xml
tests/              # Test cases and configurations
    test_settings.py
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
