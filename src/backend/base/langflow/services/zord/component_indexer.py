"""Component indexer for Zord AI - extracts component type names from starter projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lfx.log.logger import logger


class ComponentIndexer:
    """Index component type names from starter projects for Zord AI workflow generation."""

    def __init__(self, starter_projects_path: Path | str | None = None):
        """Initialize component indexer.
        
        Args:
            starter_projects_path: Path to starter projects directory.
                If None, uses default path in lfx tests.
        """
        if starter_projects_path is None:
            # Path calculation from backend/base/langflow/services/zord/component_indexer.py
            # Go up 6 levels to reach langflow root
            current_file = Path(__file__).resolve()
            langflow_root = current_file.parent.parent.parent.parent.parent.parent
            
            # Try src/lfx/tests/data/starter_projects_1_6_0
            path1 = langflow_root / "src" / "lfx" / "tests" / "data" / "starter_projects_1_6_0"
            # Try lfx/tests/data/starter_projects_1_6_0
            path2 = langflow_root / "lfx" / "tests" / "data" / "starter_projects_1_6_0"
            
            if path1.exists():
                self.starter_projects_path = path1
            elif path2.exists():
                self.starter_projects_path = path2
            else:
                self.starter_projects_path = path1
        else:
            self.starter_projects_path = Path(starter_projects_path)
        
        self.component_types: set[str] = set()
        self._indexed = False
    
    def index_components(self) -> None:
        """Extract component type names from starter projects.
        
        We only extract TYPE NAMES, not full templates.
        The Langflow system will instantiate components with current definitions.
        """
        if self._indexed:
            return
        
        logger.info(f"Indexing component types from: {self.starter_projects_path}")
        
        if not self.starter_projects_path.exists():
            logger.error(f"Starter projects path not found: {self.starter_projects_path}")
            self._indexed = True
            return
        
        # Extract component type names from all starter projects
        for json_file in self.starter_projects_path.glob("*.json"):
            try:
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                
                nodes = data.get("data", {}).get("nodes", [])
                
                for node in nodes:
                    node_data = node.get("data", {})
                    node_type = node_data.get("type")
                    
                    # Skip note nodes
                    if node_type and node_type not in ["note", "noteNode"]:
                        self.component_types.add(node_type)
                        
            except Exception as e:
                logger.warning(f"Error reading {json_file.name}: {e}")
                continue
        
        self._indexed = True
        logger.info(f"Indexed {len(self.component_types)} component types")
        logger.info(f"Available types: {sorted(self.component_types)}")
    
    def get_all_component_types(self) -> list[str]:
        """Get list of all indexed component types.
        
        Returns:
            List of component type names
        """
        if not self._indexed:
            self.index_components()
        
        return sorted(self.component_types)
    
    def has_component_type(self, component_type: str) -> bool:
        """Check if a component type exists in the index.
        
        Args:
            component_type: The component type name
        
        Returns:
            True if the component type exists
        """
        if not self._indexed:
            self.index_components()
        
        return component_type in self.component_types
    
    def search_components(self, query: str) -> list[str]:
        """Search for component types matching a query string.
        
        Args:
            query: Search query (case-insensitive)
        
        Returns:
            List of matching component type names
        """
        if not self._indexed:
            self.index_components()
        
        query_lower = query.lower()
        return sorted([
            comp_type for comp_type in self.component_types
            if query_lower in comp_type.lower()
        ])


# Singleton instance
_component_indexer: ComponentIndexer | None = None


def get_component_indexer(starter_projects_path: Path | str | None = None) -> ComponentIndexer:
    """Get or create the global ComponentIndexer instance.
    
    Args:
        starter_projects_path: Optional path override for starter projects
    
    Returns:
        ComponentIndexer instance
    """
    global _component_indexer
    
    if _component_indexer is None:
        _component_indexer = ComponentIndexer(starter_projects_path)
        _component_indexer.index_components()
    
    return _component_indexer
