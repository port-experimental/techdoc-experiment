# Port Documentation AI Agent Implementation Guide

## 🎯 Project Overview

This project enables you to ingest markdown documentation into Port and create an AI agent to query and interact with the documentation within Port's ecosystem.

## 📋 Prerequisites

### 1. Port Account Setup
- Active Port organization account
- Admin permissions for blueprint and entity management
- API credentials (Client ID and Secret)

### 2. AI Agent Access
**⚠️ CRITICAL**: Port AI Agents are currently in **closed beta**
- Contact Port support to request beta access
- Alternative: Use custom implementation with Port's API

### 3. Technical Requirements
- Python 3.8+
- Access to your markdown documentation files
- Network access to Port API

## 🚀 Step-by-Step Implementation

### Step 1: Environment Setup

1. **Clone/Download this project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp config.example.env .env
   # Edit .env with your Port credentials and docs path
   ```

### Step 2: Get Port API Credentials

1. Log into your Port organization
2. Go to Settings → Developers → API Keys
3. Create new API key pair
4. Copy Client ID and Client Secret to your `.env` file

### Step 3: Prepare Documentation

1. **Organize your markdown files**:
   ```
   docs/
   ├── api/
   │   ├── authentication.md
   │   └── endpoints.md
   ├── guides/
   │   ├── getting-started.md
   │   └── advanced-usage.md
   └── examples/
       └── code-samples.md
   ```

2. **Optimize for AI agent** (optional):
   - Add frontmatter with metadata
   - Include clear headings and structure
   - Add relevant tags

### Step 4: Run Documentation Ingestion

```bash
# Set environment variables
export PORT_CLIENT_ID="your_client_id"
export PORT_CLIENT_SECRET="your_client_secret"
export DOCS_PATH="./docs"

# Run ingestion
python ingest_docs.py
```

### Step 5: Verify Data in Port

1. Log into Port UI
2. Navigate to Software Catalog
3. Look for "Documentation" blueprint
4. Verify your documents are listed as entities

### Step 6: Setup AI Agent

#### Option A: Port AI Agent (Beta Access Required)
1. Navigate to Port AI Agents section
2. Create new agent using `ai-agent-config.json`
3. Configure data access to documentation blueprint
4. Test conversation starters

#### Option B: Custom Implementation (Alternative)
If you don't have beta access, use the custom search script:

```python
# See custom_search.py for implementation
```

## ⚠️ Known Limitations & Workarounds

### Port API Limitations

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| Search API returns max 25 entities | Large doc sets truncated | Implement pagination logic |
| Similarity search max 10 entities | Limited context for AI | Use category-based filtering |
| 8K token limit for similarity search | Long docs not fully indexed | Split large files into sections |
| 2000 token output limit | Long responses truncated | Implement response chunking |

### Data Processing Workarounds

1. **Large Document Sets**:
   ```python
   # Split large markdown files into sections
   def split_large_docs(content, max_tokens=7000):
       sections = content.split('\n## ')
       return [f"## {section}" for section in sections if section.strip()]
   ```

2. **Enhanced Search**:
   ```python
   # Implement multi-step search for better results
   def enhanced_search(query, categories=None, tags=None):
       # 1. Direct content search
       # 2. Tag-based filtering  
       # 3. Category filtering
       # 4. Similarity scoring
   ```

3. **Content Optimization**:
   ```python
   # Pre-process content for better AI understanding
   def optimize_content(content):
       # Extract key concepts
       # Add context markers
       # Enhance with metadata
   ```

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
❌ 401 Unauthorized
```
**Solution**: Verify your Client ID and Secret are correct

#### 2. Blueprint Creation Fails
```bash
❌ Blueprint already exists
```
**Solution**: The script will update existing blueprints automatically

#### 3. Large File Ingestion Fails
```bash
❌ Request entity too large
```
**Solution**: Enable file splitting in the ingestion script

#### 4. AI Agent Not Available
```bash
❌ AI Agents feature not found
```
**Solution**: Request beta access from Port support

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎛️ Advanced Configuration

### Custom Content Processing

Modify `DocumentProcessor` class to handle specific document formats:

```python
@staticmethod
def custom_processor(content: str, file_path: str) -> DocMetadata:
    # Add custom logic for your specific needs
    # Extract API specifications, code blocks, etc.
    pass
```

### Enhanced AI Agent Prompts

Customize the system prompt in `ai-agent-config.json` for your specific use case:

```json
{
  "systemPrompt": "You are a specialist in [YOUR_DOMAIN]. Focus on..."
}
```

### Performance Optimization

1. **Batch Processing**:
   ```python
   def batch_ingest(files, batch_size=10):
       for i in range(0, len(files), batch_size):
           batch = files[i:i+batch_size]
           process_batch(batch)
   ```

2. **Caching**:
   ```python
   def cache_processed_files():
       # Cache file hashes to avoid reprocessing
       pass
   ```

## 📊 Monitoring & Maintenance

### Regular Updates

1. **Content Sync**: Re-run ingestion when docs change
2. **Schema Updates**: Update blueprint as needed
3. **Performance Monitoring**: Track query response times

### Metrics to Track

- Number of documents ingested
- Search query performance
- AI agent interaction rates
- User satisfaction scores

## 🆘 Support & Next Steps

### Getting Help

1. **Port Documentation**: Check official Port docs
2. **Community**: Join Port community Slack
3. **Support**: Contact Port support for AI agent beta access

### Future Enhancements

1. **Real-time Sync**: Webhook-based document updates
2. **Version Control**: Track document changes over time
3. **Analytics**: User interaction and content effectiveness
4. **Multi-format Support**: PDF, HTML, API specs

## 📋 Checklist

- [ ] Port account and API credentials configured
- [ ] Documentation files organized and accessible
- [ ] Dependencies installed
- [ ] Blueprint created successfully
- [ ] Documents ingested and visible in Port
- [ ] AI agent configured (or alternative implemented)
- [ ] Testing completed with sample queries
- [ ] Monitoring and maintenance plan in place

## 🔐 Security Considerations

1. **API Credentials**: Store securely, never commit to version control
2. **Content Sensitivity**: Review what documentation is being ingested
3. **Access Control**: Configure appropriate permissions in Port
4. **Data Retention**: Understand Port's data retention policies

---

**Need Help?** Contact Port support or check their documentation for the latest AI agent features and availability. 