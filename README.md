# FilderFlux
Simple tool for folder synchronisation

## Installation

To install FilderFlux, use pip:

```
pip install git+https://github.com/any-23/FilderFlux.git
```

## Development

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
   - Create a new directory named after your command (e.g., `delete`).

2. **Add a subparser function:**
   - Inside your new command directory, create an `__init__.py` file.
   - Define a function in `__init__.py` to add a subparser for your command called `add_<new_command>_parser(root_parser)`.
   - Write your `add_<new_command>_parser(root_parser)` under comment `# your commands go here`.

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
│   │   └── tests/
│   │       └── test_new_command.py
│   ├── __init__.py
```
