"""Setup parameters."""
from setuptools import find_packages, setup

setup(
    name="fuzzy-multi-dict",
    packages=find_packages(),
    version="0.1.0",
    python_requires=">=3.11, <4",
    description="A flexible data structure for storing and retrieving information using string-based keys with fuzzy matching capabilities.",
    author=["Tetiana Lytvynenko <lytvynenkotv@gmail.com>", "Denis Shchutskyi <denisshchutskyi@gmail.com>"],
    install_requires=[
        "dill==0.3.9"
    ],
    setup_requires=[
        "pytest-runner",
    ],
    tests_require=[
        "pytest==8.3.4",
        "coverage==7.6.10"
    ],
    test_suite="tests",
)

