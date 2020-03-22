from setuptools import setup, find_namespace_packages

package_dir = "src"

setup(
    name="schocken",
    version="0.1",
    description="Schocken - The game",
    author="Pablo Prietz",
    author_email="pablo@prietz.org",
    license="MIT",
    package_dir={"": package_dir},
    packages=find_namespace_packages(where=package_dir),
    zip_safe=False,
    install_requires=["python-statemachine",
                      "discord.py"],
)
