![Demo of the project](docs/filderflux_demo.gif)

# FilderFlux
Simple tool for folder synchronisation

## Installation

### Prefered way

To install FilderFlux, use pip:

```
pip install git+https://github.com/any-23/FilderFlux.git
```

⚠️ **Warning:** PyPI distribution is still in progress.

## Commands

List of available commands:

- [version](filderflux/commands/version/README.md)
- [sync](filderflux/commands/sync/README.md)

List of available arguments:

- [--source, -s](filderflux/commands/sync/README.md)
- [--replica, -r](filderflux/commands/sync/README.md)
- [--interval, -i](filderflux/commands/sync/README.md)
- [--log-file, -l](filderflux/commands/sync/README.md)

## Development and Tests

### Building Distribution Packages

To create distribution packages for FilderFlux package, you can use the following command:

```
python3 setup.py sdist bdist_wheel
```

### Contribution Hygiene

Before opening a pull request, please ensure that your code satisfies basic code standards and tests are successful by running the following commands in root folder of this repository:

```
make lint
make test
```

### Creating a new command

To add a new command, follow these steps:

1. **Create a new module for your command:**
   - Go to the `filderflux/commands` folder.
   - Create a new directory named after your command (e.g., `sync`).

2. **Add a subparser function:**
   - Inside your new command directory, create an `__init__.py` file.
   - Define a function in `__init__.py` to add a subparser for your command called `add_<new_command>_parser(root_parser)`.
   - Write your `add_<new_command>_parser(root_parser)` under comment `# your commands go here` in `filderflux.py`.

3. **Create a tests subfolder:**
    - Inside your new command directory, create a tests folder.
    - Add unit tests for your command inside the tests folder.

**Example Folder Structure**

After adding a new command, your folder structure should look like this:

```
filderflux/
├── commands/
│   ├── new_command/
│   │   ├── __init__.py
│   │   ├── new_command.py
│   │   ├── README.md
│   │   └── tests/
│   │       ├── test_new_command.py
│   │       ├── __init__.py
│   └── __init__.py
```

### Logging

When adding a new command and incorporating logging, it is recommended to utilise the preconfigured logger defined in filderflux.py. To instantiate the logger in your module, use the following convention:

```
logger = logging.getLogger(__name__)
```

### Unit Tests

The package includes comprehensive unit tests to cover various scenarios for both the sync and version commands. When adding new features or modifying existing ones, ensure to include corresponding unit tests to maintain the integrity of the package.

## Contributing

Contributions and feature requests are welcome! Please ensure that any changes are accompanied by relevant tests and documentation updates.

## Future plans
- add E2E tests to validate the entire workflow
- test cases:
    1. Run complete synchronisation cycles (filderflux sync command) with varying folder structures and content.
    2. Validate synchronisation across different operating systems and environments.
    3. Test edge cases such as network interruptions, permission issues, large file handling, and scalability.
    4. Test security handling such as authentication, encryption of data, secure file handling, etc.
