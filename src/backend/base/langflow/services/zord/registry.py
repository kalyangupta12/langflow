"""Component Registry for Zord AI - Dynamic component knowledge base."""

from __future__ import annotations

from typing import Any

from lfx.interface.components import get_and_cache_all_types_dict
from lfx.log.logger import logger


class ComponentRegistry:
    """Registry for all available Langflow components and their metadata.
    
    This registry serves as the knowledge base for Zord AI to generate
    workflows with real, validated components from the Langflow system.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._components: dict[str, dict[str, Any]] = {}
        self._loaded = False

    async def load_components(self, settings_service: Any = None, telemetry_service: Any = None) -> None:
        """Load all available components from Langflow's component system.
        
        Args:
            settings_service: Langflow settings service
            telemetry_service: Optional telemetry service
        """
        if self._loaded:
            return

        try:
            logger.info("Loading component registry from Langflow component system...")
            
            # Get all components from Langflow's centralized component loader
            # This is the same API the frontend uses
            if settings_service:
                self._components = await get_and_cache_all_types_dict(
                    settings_service=settings_service,
                    telemetry_service=telemetry_service
                )
            else:
                # Fallback: try to load without settings
                from langflow.services.deps import get_settings_service
                settings = get_settings_service()
                self._components = await get_and_cache_all_types_dict(
                    settings_service=settings,
                    telemetry_service=telemetry_service
                )
            
            self._loaded = True
            
            # Log statistics
            total_components = sum(len(comps) for comps in self._components.values())
            logger.info(
                f"Component registry loaded successfully: "
                f"{len(self._components)} categories, {total_components} components"
            )
            
        except Exception as e:
            logger.error(f"Failed to load component registry: {e}", exc_info=True)
            self._components = {}
            self._loaded = False

    def get_all_components(self) -> dict[str, dict[str, Any]]:
        """Get all components by category.
        
        Returns:
            Dictionary mapping component category to component definitions
        """
        return self._components

    def get_component_types(self) -> list[str]:
        """Get list of all available component types (excluding legacy).
        
        Returns:
            List of modern component type names
        """
        component_types = []
        for category, components in self._components.items():
            for comp_name, comp_data in components.items():
                # Skip legacy and deprecated components
                if comp_data.get("legacy", False) or comp_data.get("deprecated", False):
                    continue
                component_types.append(comp_name)
        return sorted(component_types)

    def get_component_by_type(self, component_type: str) -> dict[str, Any] | None:
        """Get component definition by type name.
        
        Args:
            component_type: Component type name (e.g., "ChatInput")
        
        Returns:
            Component definition dictionary or None if not found
        """
        for category, components in self._components.items():
            if component_type in components:
                return components[component_type]
        return None

    def get_components_by_category(self, category: str) -> dict[str, Any]:
        """Get all components in a specific category.
        
        Args:
            category: Category name (e.g., "inputs", "models", "vectorstores")
        
        Returns:
            Dictionary of components in the category
        """
        return self._components.get(category, {})

    def get_component_template(self, component_type: str) -> dict[str, Any] | None:
        """Get the full template for a component type.
        
        Args:
            component_type: Component type name
        
        Returns:
            Component template dictionary with all fields or None
        """
        component = self.get_component_by_type(component_type)
        if component and "template" in component:
            return component["template"]
        return None

    def get_component_outputs(self, component_type: str) -> list[dict[str, Any]]:
        """Get output definitions for a component.
        
        Args:
            component_type: Component type name
        
        Returns:
            List of output definitions
        """
        component = self.get_component_by_type(component_type)
        if component and "outputs" in component:
            return component["outputs"]
        return []

    def get_component_inputs(self, component_type: str) -> dict[str, Any]:
        """Get input parameter definitions for a component.
        
        Args:
            component_type: Component type name
        
        Returns:
            Dictionary of input parameters from template
        """
        template = self.get_component_template(component_type)
        if template:
            # Filter out metadata fields
            return {
                k: v for k, v in template.items()
                if not k.startswith("_") and k != "code"
            }
        return {}

    def format_for_llm(self, include_templates: bool = False, compact: bool = True) -> str:
        """Format component registry for LLM consumption.
        
        Args:
            include_templates: Whether to include full component templates (not recommended - uses many tokens)
            compact: Whether to use compact format (recommended to save tokens)
        
        Returns:
            Formatted string describing available components
        """
        if compact:
            return self._format_compact()
        
        output = []
        output.append("# AVAILABLE LANGFLOW COMPONENTS\n")
        output.append("These are the ONLY components available in this Langflow instance.\n")
        output.append("**CRITICAL**: Only use components from this list. Do not invent component names.\n")
        
        for category, components in sorted(self._components.items()):
            output.append(f"\n## {category.upper()} ({len(components)} components)\n")
            
            for comp_name, comp_data in sorted(components.items()):
                display_name = comp_data.get("display_name", comp_name)
                description = comp_data.get("description", "No description")
                
                output.append(f"\n### {comp_name}")
                output.append(f"**Display Name**: {display_name}")
                output.append(f"**Description**: {description}")
                
                # Add output information
                if "outputs" in comp_data:
                    outputs = comp_data["outputs"]
                    if outputs:
                        output.append("**Outputs**:")
                        for out in outputs:
                            out_name = out.get("name", "unknown")
                            out_types = ", ".join(out.get("types", []))
                            output.append(f"  - `{out_name}` → {out_types}")
                
                # Add input information from template
                if "template" in comp_data:
                    template = comp_data["template"]
                    inputs = [k for k in template.keys() if not k.startswith("_") and k != "code"]
                    if inputs:
                        output.append("**Inputs**:")
                        for inp in sorted(inputs):
                            inp_data = template[inp]
                            if isinstance(inp_data, dict):
                                inp_type = inp_data.get("type", "unknown")
                                inp_required = inp_data.get("required", False)
                                req_str = " (required)" if inp_required else ""
                                output.append(f"  - `{inp}` ← {inp_type}{req_str}")
                
                # Optionally include full template
                if include_templates and "template" in comp_data:
                    output.append("\n**Full Template**:")
                    output.append(f"```json\n{comp_data}\n```")
                
                output.append("")
        
        return "\n".join(output)
    
    def _format_compact(self) -> str:
        """Format component registry in ultra-compact format to minimize tokens.
        
        Filters out legacy components and prioritizes modern, commonly used components.
        
        Returns:
            Concise component list optimized for token efficiency
        """
        output = []
        output.append("## AVAILABLE COMPONENTS (Modern, Non-Legacy)\n")
        output.append("**CRITICAL**: Only use components from this list. All legacy components are excluded.\n")
        
        # Group by category with minimal formatting
        for category, components in sorted(self._components.items()):
            comp_list = []
            for comp_name, comp_data in sorted(components.items()):
                # Skip legacy components completely
                if comp_data.get("legacy", False):
                    continue
                
                # Skip if marked as deprecated or has replacement
                if comp_data.get("deprecated", False) or comp_data.get("replacement"):
                    continue
                
                # Get first output type if available
                outputs = comp_data.get("outputs", [])
                output_type = outputs[0].get("types", ["Data"])[0] if outputs else "Data"
                
                # Truncate description to first 50 chars (increased from 40)
                desc = comp_data.get("description", "")
                if len(desc) > 50:
                    desc = desc[:47] + "..."
                
                # Format: ComponentName → OutputType: description
                comp_list.append(f"- {comp_name} → {output_type}: {desc}")
            
            if comp_list:
                output.append(f"\n**{category}** ({len(comp_list)}):")
                output.extend(comp_list[:30])  # Increased from 20 to 30 per category
                if len(comp_list) > 30:
                    output.append(f"  ... and {len(comp_list) - 30} more (use these component names)")
        
        output.append("\n**IMPORTANT**: Use exact component names from this list. All components are modern and actively maintained.")
        return "\n".join(output)

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        total_components = sum(len(comps) for comps in self._components.values())
        
        # Count modern vs legacy components
        modern_count = 0
        legacy_count = 0
        for category, components in self._components.items():
            for comp_name, comp_data in components.items():
                if comp_data.get("legacy", False) or comp_data.get("deprecated", False):
                    legacy_count += 1
                else:
                    modern_count += 1
        
        return {
            "loaded": self._loaded,
            "categories": len(self._components),
            "total_components": total_components,
            "modern_components": modern_count,
            "legacy_components": legacy_count,
            "category_names": list(self._components.keys()),
        }


# Global registry instance
_registry: ComponentRegistry | None = None


def get_component_registry() -> ComponentRegistry:
    """Get the global component registry instance.
    
    Returns:
        Global ComponentRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ComponentRegistry()
    return _registry


async def initialize_registry(settings_service: Any = None, telemetry_service: Any = None) -> ComponentRegistry:
    """Initialize and load the component registry.
    
    Args:
        settings_service: Langflow settings service
        telemetry_service: Optional telemetry service
    
    Returns:
        Loaded ComponentRegistry instance
    """
    registry = get_component_registry()
    await registry.load_components(settings_service, telemetry_service)
    return registry
