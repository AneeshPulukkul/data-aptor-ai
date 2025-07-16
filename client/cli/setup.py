from setuptools import setup, find_packages

setup(
    name="dataaptor",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.1.3",
        "requests>=2.28.2",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "dataaptor=dataaptor:cli",
        ],
    },
)
