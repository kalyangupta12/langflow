"""Test script for component indexer."""

import asyncio
from pathlib import Path

from langflow.services.zord.component_indexer import ComponentIndexer


async def test_indexer():
    """Test the component indexer."""
    print("=" * 80)
    print("TESTING COMPONENT INDEXER")
    print("=" * 80)
    
    # Initialize indexer
    indexer = ComponentIndexer()
    indexer.index_components()
    
    print(f"\n✓ Indexed {len(indexer.components)} unique component types")
    
    # Show all component types
    print("\n" + "=" * 80)
    print("ALL COMPONENT TYPES")
    print("=" * 80)
    for comp_type in sorted(indexer.get_all_component_types()):
        print(f"  - {comp_type}")
    
    # Show components by category
    print("\n" + "=" * 80)
    print("COMPONENTS BY CATEGORY")
    print("=" * 80)
    categories = indexer.get_components_by_category()
    for category, components in sorted(categories.items()):
        if components:
            print(f"\n{category.upper()} ({len(components)}):")
            for comp in sorted(components):
                print(f"  - {comp}")
    
    # Test getting a specific template
    print("\n" + "=" * 80)
    print("TESTING SPECIFIC COMPONENT: ChatInput")
    print("=" * 80)
    chat_input_template = indexer.get_component_template("ChatInput")
    if chat_input_template:
        print(f"✓ ChatInput template found")
        print(f"  Display Name: {chat_input_template.get('display_name')}")
        print(f"  Description: {chat_input_template.get('description')}")
        print(f"  Outputs: {[o.get('name') for o in chat_input_template.get('outputs', [])]}")
        print(f"  Template fields: {len(chat_input_template.get('template', {}))}")
    else:
        print("✗ ChatInput template not found")
    
    # Test searching
    print("\n" + "=" * 80)
    print("TESTING SEARCH: 'openai'")
    print("=" * 80)
    results = indexer.search_components("openai")
    print(f"Found {len(results)} components:")
    for comp in results:
        print(f"  - {comp}")
    
    # Test component info
    print("\n" + "=" * 80)
    print("DETAILED INFO: OpenAIModel")
    print("=" * 80)
    info = indexer.get_component_info("OpenAIModel")
    if info:
        print(f"  Type: {info.get('type')}")
        print(f"  Display Name: {info.get('display_name')}")
        print(f"  Description: {info.get('description')[:100]}...")
        print(f"  Category: {info.get('category')}")
        print(f"  Outputs: {[o.get('name') for o in info.get('outputs', [])]}")
        print(f"  Used in {info.get('usage_count')} starter projects")
        print(f"  Examples: {[ex['source'] for ex in info.get('examples', [])[:3]]}")
    else:
        print("✗ OpenAIModel not found")
    
    print("\n" + "=" * 80)
    print("INDEXER TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_indexer())
