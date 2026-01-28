"""Initialize ChromaDB collection with components and templates."""

from pathlib import Path
import sys

# Add parent directory to path for imports
current_file = Path(__file__).resolve()
langflow_root = current_file.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(langflow_root / "src" / "backend" / "base"))

from langflow.services.zord.chroma_component_indexer import get_chroma_indexer
from lfx.log.logger import logger


def main():
    """Initialize ChromaDB collection."""
    logger.info("Initializing ChromaDB collection...")
    
    # Get indexer instance
    indexer = get_chroma_indexer()
    
    # Reset collection (delete and recreate)
    indexer.reset()
    
    # Index components
    indexer.index_components()
    
    # Index templates
    indexer.index_templates()
    
    # Print stats
    stats = indexer.get_stats()
    logger.info(f"Initialization complete: {stats}")
    
    print("\n" + "="*50)
    print("ChromaDB Initialization Complete")
    print("="*50)
    print(f"Collection: {stats['collection_name']}")
    print(f"Total Items: {stats['points_count']}")
    print(f"Status: {stats['status']}")
    print(f"Backend: {stats['backend']}")
    print("="*50)


if __name__ == "__main__":
    main()
