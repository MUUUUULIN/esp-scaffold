from setuptools import setup, find_packages

setup(
    name="esp-scaffold",
    version="0.1.0",
    description="ESP-IDF project scaffolding tool — ESP32 CubeMX-lite",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click>=8.0", "jinja2>=3.1"],
    entry_points={
        "console_scripts": [
            "esp-scaffold=esp_scaffold.cli:main",
        ],
    },
    python_requires=">=3.8",
)
