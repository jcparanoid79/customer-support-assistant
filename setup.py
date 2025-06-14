"""Setup configuration for the customer support assistant package."""
from setuptools import setup, find_packages

setup(
    name="customer-support-assistant",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},    install_requires=[
        "langchain>=0.1.0",
        "langchain-google-genai>=0.0.5",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=24.1.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=2.0.0",
            "myst-parser>=2.0.0",
        ],
    },
    python_requires=">=3.9",
    author="Your Name",
    description="An AI-powered customer support assistant using LangChain and Google Gemini",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
