# Version

Version command manage and inspect the version of the FilderFlux package. It supports logging both to a file and to the console.

## Usage

To check the version of the FilderFlux package, you can run the following command:

```
filderflux --log-file <name-of-log-file> --version
```

Example output:

```
2024-06-09 16:27:18,701 - INFO - version.py:Version of filderflux is 0.0.1.
```

## Future plans
- add E2E tests to validate the entire workflow
- test cases:
    1. Run complete synchronisation cycles (filderflux sync command) with varying folder structures and content.
    2. Validate synchronisation across different operating systems and environments.
    3. Test edge cases such as network interruptions, permission issues, large file handling, and scalability.
    4. Test security handling such as authentication, encryption of data, secure file handling, etc.
