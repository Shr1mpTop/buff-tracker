from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="buff-tracker",
    version="1.0.0",
    author="Buff Tracker",
    description="SteamDT API管理工具 - 支持密钥轮询和速率限制",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/buff-tracker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
)
