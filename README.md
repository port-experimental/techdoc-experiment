# Port Documentation Ingestion Framework

This project provides a modular and extensible framework for ingesting documentation from various sources into a Port software catalog. It allows you to populate your catalog with documentation from local markdown files and `README` files discovered in remote Git repositories.

## Features

- **Modular Architecture**: Built with a clean, decoupled structure that separates data fetching, parsing, and ingestion logic.
- **Multiple Data Sources**:
  - **Local**: Ingests markdown files from a local directory.
  - **Remote**: Fetches and ingests `README.md` files from repositories across:
    - GitHub (Cloud)
    - GitLab (Cloud & Self-Hosted)
    - Azure Repos
- **Centralized Schema**: Uses a single, unified `documentation` blueprint in Port for all ingested content.
- **Modern Python**: Uses Poetry for dependency management and follows modern project structure best practices.
- **Configurable & Extensible**: Easily configure repository targets via a TOML file and extend the framework to support new data sources.
- **Testable**: Includes a `pytest` suite for validating functionality.

## Project Structure

```
.
├── .env                    # Local environment variables (created via setup script)
├── docs/                   # Default directory for local markdown files
├── scripts/                # All executable entry-point scripts
│   ├── check_status.py
│   ├── cleanup_entities.py
│   ├── create_ai_agent.py
│   ├── custom_search.py
│   ├── ingest_local_docs.py
│   ├── ingest_remote_readmes.py
│   ├── setup_credentials.py
│   └── test_ai_agent.py
├── src/                    # Main application source code
│   └── port_tools/
│       ├── ai_agent/
│       ├── clients/
│       ├── fetchers/
│       ├── parsers/
│       └── search/
├── tests/                  # Pytest test suite
├── ai-agent-config.json    # Configuration for the Port AI Agent
├── port-docs-blueprint.json# The official schema for the 'documentation' blueprint
├── pyproject.toml          # Project metadata and dependencies (Poetry)
├── poetry.lock             # Exact dependency versions
└── repositories.toml       # Configuration for remote repository targets
```

## Getting Started

### 1. Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation) installed on your system.

### 2. Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies using Poetry:**
    This command will create a virtual environment and install all necessary packages.
    ```bash
    poetry install
    ```

3.  **Configure Credentials:**
    Run the setup script. It will interactively prompt you for your Port credentials and any Git provider tokens you wish to use, then create a `.env` file for you.
    ```bash
    poetry run python scripts/setup_credentials.py
    ```

### 3. Configure Remote Targets

If you plan to ingest remote READMEs, edit the `repositories.toml` file to specify which repositories to scan. Add the names of your organizations (GitHub), groups (GitLab), or projects (Azure Repos).

```toml
[github]
orgs = ["my-github-org", "another-org"]

[gitlab]
groups = ["my-gitlab-group"]

[azure_repos]
projects = ["my-azure-devops-project"]
```

## Usage

All scripts should be run using `poetry run`.

### Ingesting Local Documentation

This script scans a local directory (defaults to `./docs`) for markdown files and ingests them into Port.

```bash
poetry run python scripts/ingest_local_docs.py
```

### Ingesting Remote READMEs

This script uses your configuration to find and ingest `README.md` files from your Git providers.

```bash
poetry run python scripts/ingest_remote_readmes.py
```

## Utility Scripts

This project includes several utility scripts located in the `scripts/` directory to help manage and interact with the Port environment.

### `check_status.py`
A simple script to test your connection to the Port API and check if the `documentation` blueprint contains any entities.
```bash
poetry run python scripts/check_status.py
```

### `custom_search.py`
Performs an interactive search across the ingested documentation in your Port catalog.
```bash
poetry run python scripts/custom_search.py
```

### `cleanup_entities.py`
Deletes all entities associated with the "Documentation" blueprint. This is useful for clearing out old data before a fresh ingestion. **Use with caution!**
```bash
poetry run python scripts/cleanup_entities.py
```

### `create_ai_agent.py`
(Conceptually) creates or updates the Port AI Agent using `ai-agent-config.json`. The agent creation API is not yet public, so this serves as a placeholder.
```bash
poetry run python scripts/create_ai_agent.py
```

### `test_ai_agent.py`
Runs a series of test queries against the AI agent to verify that it is active and responding.
```bash
poetry run python scripts/test_ai_agent.py
```

## Running Tests

To run the `pytest` test suite:
```bash
poetry run pytest
```

## Troubleshooting

### Poetry Installation Error
**Error**: `No file/folder found for package` when running `poetry install`.

**Cause**: This occurs when Poetry cannot find the source code for the package it's trying to install.

**Solution**: The `pyproject.toml` file has been configured with the following line to resolve this. Ensure it is present if you encounter this error.
```toml
[tool.poetry]
# ... other settings
packages = [{include = "port_tools", from = "src"}]
```

### Other Notes
- **Bitbucket Support**: Support for Bitbucket Cloud has been deferred due to a lack of a stable, compatible Python client. It can be added in the future.
- **Idempotency**: The ingestion scripts are idempotent. Running them multiple times will update existing entities rather than creating duplicates.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Port Credentials
```bash
python setup_credentials.py
```
This will guide you through:
- Getting your Port API credentials
- Creating a `.env` file
- Testing the connection

### 3. Test the Setup
```bash
python quick_start.py
```

### 4. Ingest Your Documentation
```bash
# Place your markdown files in ./docs/ or specified path
python ingest_docs.py
```

### 5. Query Your Documentation
```bash
# Interactive documentation search
python custom_search.py
```

## 📁 Project Files

- `setup_credentials.py` - Credential setup and testing
- `quick_start.py` - End-to-end testing script
- `ingest_docs.py` - Documentation ingestion script
- `custom_search.py` - AI-powered search interface
- `port-docs-blueprint.json` - Port blueprint definition
- `ai-agent-config.json` - AI agent configuration
- `IMPLEMENTATION_GUIDE.md` - Detailed implementation guide

## 🔑 Getting Port Credentials

1. Go to https://app.getport.io
2. Settings → Developers → API Keys
3. Create API Key
4. Copy Client ID and Client Secret

## ⚠️ AI Agent Beta Access

Port AI Agents are in closed beta. Contact Port support for access, or use the custom search implementation provided.

## 📚 Documentation

See `IMPLEMENTATION_GUIDE.md` for detailed setup, limitations, and advanced configuration.

## 🆘 Troubleshooting

- **Authentication errors**: Run `python setup_credentials.py` to reconfigure
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **API limits**: See workarounds in `IMPLEMENTATION_GUIDE.md`

---

**Need help?** Check the implementation guide or contact Port support. 