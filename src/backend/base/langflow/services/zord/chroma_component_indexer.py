"""ChromaDB-based component indexer for Zord AI."""

from __future__ import annotations

import json
import os
import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from lfx.log.logger import logger


class ChromaComponentIndexer:
    """Local ChromaDB indexer for semantic component search."""

    def __init__(self):
        """Initialize ChromaDB indexer."""
        # Setup ChromaDB with local persistence
        persist_dir = Path(__file__).parent / ".chroma_db"
        persist_dir.mkdir(exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection_name = "langflow_components"
        self.collection = None
        
        # Initialize embedding model
        logger.info("Loading sentence-transformers model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully")
        
        # Setup collection
        self._setup_collection()
    
    def _setup_collection(self) -> None:
        """Setup or get ChromaDB collection."""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing ChromaDB collection: {self.collection_name}")
        except Exception:
            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Langflow components and workflow templates"}
            )
            logger.info(f"Created new ChromaDB collection: {self.collection_name}")
    
    def _embed(self, text: str) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def _extract_component_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract component info from Python file using AST.
        
        Args:
            file_path: Path to Python component file
            
        Returns:
            List of component dictionaries
        """
        components = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Skip base classes
                    if (node.name.startswith('_') or 
                        node.name.endswith('Base') or
                        'base' in node.name.lower()):
                        continue
                    
                    component_info = {
                        'name': node.name,
                        'file_path': str(file_path),
                        'category': file_path.parent.name,
                        'description': '',
                        'display_name': '',
                        'documentation': '',
                        'type': 'python_component'
                    }
                    
                    # Extract docstring
                    if (node.body and 
                        isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant)):
                        component_info['documentation'] = node.body[0].value.value
                    
                    # Extract class attributes
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    attr_name = target.id
                                    if isinstance(item.value, ast.Constant):
                                        value = item.value.value
                                        if attr_name == 'display_name':
                                            component_info['display_name'] = value
                                        elif attr_name == 'description':
                                            component_info['description'] = value
                    
                    if not component_info['display_name']:
                        component_info['display_name'] = component_info['name']
                    
                    components.append(component_info)
        
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return components
    
    def _extract_workflow_template(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract workflow template info from JSON file.
        
        Args:
            file_path: Path to workflow JSON file
            
        Returns:
            Template dictionary or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            name = data.get('name', file_path.stem)
            description = data.get('description', '')
            
            return {
                'name': name,
                'file_path': str(file_path),
                'category': 'workflow_template',
                'description': description,
                'display_name': name,
                'documentation': description,
                'type': 'workflow_template'
            }
        
        except Exception as e:
            logger.warning(f"Error parsing template {file_path}: {e}")
            return None
    
    def index_components(self) -> None:
        """Index all Python components from LFX."""
        logger.info("Indexing Python components...")
        
        # Find LFX components path
        current_file = Path(__file__).resolve()
        langflow_root = current_file.parent.parent.parent.parent.parent.parent
        lfx_components_path = langflow_root / "lfx" / "src" / "lfx" / "components"
        
        logger.info(f"Looking for components in: {lfx_components_path}")
        
        if not lfx_components_path.exists():
            logger.error(f"LFX components path not found: {lfx_components_path}")
            return
        
        components_to_add = []
        
        # Extract components from Python files
        for category_dir in lfx_components_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('_'):
                continue
            
            for py_file in category_dir.glob('*.py'):
                if py_file.name.startswith('_'):
                    continue
                
                components = self._extract_component_from_file(py_file)
                components_to_add.extend(components)
        
        # Prepare data for ChromaDB
        if components_to_add:
            ids = []
            documents = []
            metadatas = []
            
            for i, comp in enumerate(components_to_add):
                # Create searchable text
                text_parts = [
                    f"Component: {comp['name']}",
                    f"Display Name: {comp['display_name']}",
                    f"Category: {comp['category']}",
                ]
                if comp['description']:
                    text_parts.append(f"Description: {comp['description']}")
                if comp['documentation']:
                    text_parts.append(f"Documentation: {comp['documentation']}")
                
                document_text = " | ".join(text_parts)
                
                ids.append(f"component_{i}")
                documents.append(document_text)
                metadatas.append({
                    'name': comp['name'],
                    'display_name': comp['display_name'],
                    'category': comp['category'],
                    'description': comp['description'],
                    'type': 'python_component'
                })
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(components_to_add)} Python components")
    
    def index_templates(self) -> None:
        """Index workflow templates from starter projects."""
        logger.info("Indexing workflow templates...")
        
        # Find starter projects path
        current_file = Path(__file__).resolve()
        templates_path = current_file.parent.parent.parent / "initial_setup" / "starter_projects"
        
        logger.info(f"Looking for templates in: {templates_path}")
        
        if not templates_path.exists():
            logger.error(f"Templates path not found: {templates_path}")
            return
        
        templates_to_add = []
        
        # Extract templates from JSON files
        for json_file in templates_path.glob('*.json'):
            template = self._extract_workflow_template(json_file)
            if template:
                templates_to_add.append(template)
        
        # Prepare data for ChromaDB
        if templates_to_add:
            ids = []
            documents = []
            metadatas = []
            
            base_id = self.collection.count()
            
            for i, tmpl in enumerate(templates_to_add):
                # Create searchable text
                text_parts = [
                    f"Template: {tmpl['name']}",
                    f"Description: {tmpl['description']}",
                ]
                
                document_text = " | ".join(text_parts)
                
                ids.append(f"template_{base_id + i}")
                documents.append(document_text)
                metadatas.append({
                    'name': tmpl['name'],
                    'display_name': tmpl['display_name'],
                    'category': tmpl['category'],
                    'description': tmpl['description'],
                    'type': 'workflow_template'
                })
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(templates_to_add)} workflow templates")
    
    def search(self, query: str, limit: int = 20, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for components/templates using semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            category_filter: Optional filter by type ('python_component' or 'workflow_template')
            
        Returns:
            List of search results with score and payload
        """
        try:
            # Build where filter
            where_filter = None
            if category_filter:
                where_filter = {"type": category_filter}
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'score': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                        'payload': results['metadatas'][0][i]
                    })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"ChromaDB search error: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexer statistics.
        
        Returns:
            Dictionary with collection stats
        """
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection_name,
                'points_count': count,
                'status': 'ready',
                'backend': 'chromadb'
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'collection_name': self.collection_name,
                'points_count': 0,
                'status': 'error',
                'backend': 'chromadb'
            }
    
    def reset(self) -> None:
        """Delete and recreate the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception:
            pass
        
        self._setup_collection()
        logger.info("Collection reset complete")
    
    def get_all_component_types(self) -> List[str]:
        """Get list of all component type names.
        
        Returns:
            List of component names
        """
        try:
            results = self.collection.get()
            if results and results['metadatas']:
                names = [meta['name'] for meta in results['metadatas']]
                return sorted(set(names))
            return []
        except Exception as e:
            logger.error(f"Error getting component types: {e}")
            return []
    
    def has_component_type(self, component_type: str) -> bool:
        """Check if a component type exists.
        
        Args:
            component_type: Component type name to check
            
        Returns:
            True if component exists
        """
        try:
            results = self.collection.get(
                where={"name": component_type}
            )
            return results and len(results['ids']) > 0
        except Exception as e:
            logger.error(f"Error checking component type: {e}")
            return False
    
    def get_component_info(self, component_type: str) -> Dict[str, Any]:
        """Get information about a specific component.
        
        Args:
            component_type: Component type name
            
        Returns:
            Component metadata dictionary
        """
        try:
            results = self.collection.get(
                where={"name": component_type}
            )
            if results and results['metadatas'] and len(results['metadatas']) > 0:
                return results['metadatas'][0]
            return {}
        except Exception as e:
            logger.error(f"Error getting component info: {e}")
            return {}


# Singleton instance
_indexer_instance: Optional[ChromaComponentIndexer] = None


def get_chroma_indexer() -> ChromaComponentIndexer:
    """Get or create the ChromaDB indexer singleton.
    
    Returns:
        ChromaComponentIndexer instance
    """
    global _indexer_instance
    
    if _indexer_instance is None:
        _indexer_instance = ChromaComponentIndexer()
    
    return _indexer_instance
