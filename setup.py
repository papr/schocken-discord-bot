import toml
from setuptools import setup, find_namespace_packages

package_dir = "src"
pyproject = toml.load("pyproject.toml")

# install dev using pipenv:
# pipenv install -e. ".[dev]"

setup(
    **pyproject["project"],
    install_requires=pyproject["dependencies"].keys(),
    extras_require={"dev": pyproject["dev-dependencies"].keys()},
    package_dir={"": package_dir},
    packages=find_namespace_packages(where=package_dir),
    entry_points={"console_scripts": ["schocken = schocken.__main__:run_bot",],},
)
