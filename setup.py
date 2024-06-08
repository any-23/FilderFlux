from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()


setup(
    name="filderflux",
    # extracting semantic version from git tag
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "local_scheme": "no-local-version",
    },
    description="A CLI tool to support operations for the file synchronisation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/any-23/FilderFlux",
    author="Aneta Vasko",
    author_email="aneta.vaskova2310@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points={
        "console_scripts": [
            "filderflux=filderflux.filderflux:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
