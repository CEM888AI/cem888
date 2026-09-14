from setuptools import find_packages, setup

TOP_LEVEL_MODULES = [
    "batch_runner",
    "cem888_bootstrap",
    "cem888_constants",
    "cem888_logging",
    "cem888_state",
    "cem888_time",
    "cli",
    "model_tools",
    "run_agent",
    "toolset_distributions",
    "toolsets",
    "trajectory_compressor",
    "utils",
]

setup(
    name="cem888-agent",
    version="1.0.3",
    description="CEM888 customer runtime",
    author="CEM888.AI",
    author_email="hello@cem888.ai",
    url="https://cem888.ai",
    package_dir={"": "src"},
    packages=find_packages("src"),
    py_modules=TOP_LEVEL_MODULES,
    include_package_data=True,
    package_data={"": ["plugin.yaml"]},

    install_requires=[
        "aiohttp>=3.9",
        "httpx>=0.28",
        "pydantic>=2.0",
        "pyyaml>=6.0",
        "rich>=13.0",
        "prompt_toolkit>=3.0",
        "python-dotenv>=1.0",
        "websockets>=12.0",
        "requests>=2.31",
        "openai>=1.0",
        "python-telegram-bot>=21,<23",
        "mautrix>=0.20,<0.22",
        "aiosqlite>=0.20",
        "asyncpg>=0.29",
        "Markdown>=3.5",
        "aiohttp-socks>=0.9",
        "psutil>=5.9",
        "ddgs>=9,<10",
        "mcp>=1.12,<2",
    ],
    extras_require={
        "customer": [
            "aiosqlite",
            "aiohttp-socks",
            "asyncpg",
            "chromadb",
            "keyring",
            "Markdown",
            "mautrix",
            "mcp>=1.12,<2",
            "openai",
            "playwright",
            "python-telegram-bot>=21,<23",
            "rank-bm25",
            "sentence-transformers",
        ]
    },
    entry_points={
        "console_scripts": [
            "cem888=cem888_cli.main:main",
            "cem888-gateway=gateway.run:main",
        ]
    },
    python_requires=">=3.14",
)
