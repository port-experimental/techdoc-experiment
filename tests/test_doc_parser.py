import sys
import os
from datetime import datetime, timezone

import pytest

# Add src to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from port_tools.parsers.doc_parser import DocParser, DocMetadata

SAMPLE_CONTENT = """---
title: My Test Document
description: A sample for testing.
tags: [test, sample]
category: Guide
---
# Main Header

This is the first paragraph. It serves as a summary.

## Sub-header

Some more text here. It mentions `python` and `docker`.
"""

@pytest.fixture
def parser():
    return DocParser()

def test_parse_full_content(parser):
    now = datetime.now(timezone.utc).isoformat()
    metadata = parser.parse(
        content=SAMPLE_CONTENT,
        source='local',
        file_path='guides/test-document.md',
        last_updated=now,
    )

    assert isinstance(metadata, DocMetadata)
    assert metadata.title == "My Test Document"
    assert "Main Header" in metadata.content
    assert metadata.summary == "A sample for testing."
    assert metadata.category == "Guide"
    assert "test" in metadata.tags
    assert "sample" in metadata.tags
    assert "python" in metadata.tags
    assert "docker" in metadata.tags
    assert "guides" in metadata.tags
    assert metadata.source == 'local'
    assert metadata.file_path == 'guides/test-document.md'
    assert metadata.last_updated == now
    assert metadata.word_count > 0
    assert metadata.reading_time > 0

def test_parse_content_no_frontmatter(parser):
    content = "# Just a Header\n\nSome text."
    now = datetime.now(timezone.utc).isoformat()
    
    metadata = parser.parse(
        content=content,
        source='github',
        file_path='org/repo/README.md',
        last_updated=now
    )

    assert metadata.title == "Just a Header"
    assert metadata.summary.startswith("Just a Header")
    assert "Some text." in metadata.summary
    assert "repo" in metadata.tags # From file path
