# Port Documentation AI Agent

Ingest markdown documentation into Port and create an AI agent to query and interact with your docs.

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