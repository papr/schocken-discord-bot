import toml
from setuptools import setup, find_namespace_packages

package_dir = "src"
pyproject = toml.load("pyproject.toml")

setup(
    **pyproject["project"],
    install_requires=pyproject["dependencies"].keys(),
    package_dir={"": package_dir},
    packages=find_namespace_packages(where=package_dir),
)
