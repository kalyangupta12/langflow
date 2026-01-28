"""Quick ChromaDB initialization script."""
from pathlib import Path
import sys

# Add to path
sys.path.insert(0, str(Path('e:/langflow/langflow/src/backend/base')))

from langflow.services.zord.chroma_component_indexer import get_chroma_indexer

# Initialize
indexer = get_chroma_indexer()
indexer.reset()
indexer.index_components()
indexer.index_templates()

# Print stats
print('\n' + '='*50)
print('ChromaDB Initialization Complete')
print('='*50)
stats = indexer.get_stats()
print(f'Collection: {stats["collection_name"]}')
print(f'Total Items: {stats["points_count"]}')
print(f'Status: {stats["status"]}')
print(f'Backend: {stats["backend"]}')
print('='*50)
