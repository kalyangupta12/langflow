"""Simple workflow JSON generator for Zord AI."""

from __future__ import annotations

import json
import uuid
from typing import Any


def generate_simple_chat_workflow(
    workflow_name: str = "Simple Chat Workflow",
    description: str = "Basic chat workflow with ChatInput, LLM, and ChatOutput"
) -> dict[str, Any]:
    """Generate a simple 3-node chat workflow JSON.
    
    Args:
        workflow_name: Name of the workflow
        description: Description of the workflow
    
    Returns:
        Complete Langflow workflow JSON
    """
    
    # Generate unique IDs
    chat_input_id = f"ChatInput-{uuid.uuid4().hex[:8]}"
    llm_id = f"LanguageModelComponent-{uuid.uuid4().hex[:8]}" 
    chat_output_id = f"ChatOutput-{uuid.uuid4().hex[:8]}"
    
    # Create nodes with minimal structure
    nodes = [
        {
            "id": chat_input_id,
            "data": {
                "id": chat_input_id,
                "type": "ChatInput"
            },
            "position": {"x": 100, "y": 100},
            "type": "genericNode"
        },
        {
            "id": llm_id,
            "data": {
                "id": llm_id,
                "type": "LanguageModelComponent"
            },
            "position": {"x": 500, "y": 100},
            "type": "genericNode"
        },
        {
            "id": chat_output_id,
            "data": {
                "id": chat_output_id,
                "type": "ChatOutput"
            },
            "position": {"x": 900, "y": 100},
            "type": "genericNode"
        }
    ]
    
    # Create edges with simplified format
    edges = [
        {
            "id": f"reactflow__edge-{chat_input_id}-{llm_id}",
            "source": chat_input_id,
            "target": llm_id,
            "sourceHandle": "message",
            "targetHandle": "input_value",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{llm_id}-{chat_output_id}",
            "source": llm_id,
            "target": chat_output_id,
            "sourceHandle": "text_output",
            "targetHandle": "input_value", 
            "animated": False
        }
    ]
    
    return {
        "data": {
            "nodes": nodes,
            "edges": edges,
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        },
        "name": workflow_name,
        "description": description
    }


def generate_rag_workflow(
    workflow_name: str = "RAG Workflow",
    description: str = "Document Q&A workflow with retrieval augmented generation"
) -> dict[str, Any]:
    """Generate a RAG workflow JSON.
    
    Args:
        workflow_name: Name of the workflow
        description: Description of the workflow
    
    Returns:
        Complete Langflow workflow JSON
    """
    
    # Generate unique IDs
    file_id = f"File-{uuid.uuid4().hex[:8]}"
    splitter_id = f"SplitText-{uuid.uuid4().hex[:8]}"
    embeddings_id = f"OpenAIEmbeddings-{uuid.uuid4().hex[:8]}"
    vectorstore_id = f"AstraDB-{uuid.uuid4().hex[:8]}"
    chat_input_id = f"ChatInput-{uuid.uuid4().hex[:8]}"
    prompt_id = f"Prompt-{uuid.uuid4().hex[:8]}"
    llm_id = f"LanguageModelComponent-{uuid.uuid4().hex[:8]}"
    chat_output_id = f"ChatOutput-{uuid.uuid4().hex[:8]}"
    
    # Create nodes
    nodes = [
        {
            "id": file_id,
            "data": {"id": file_id, "type": "File"},
            "position": {"x": 100, "y": 100},
            "type": "genericNode"
        },
        {
            "id": splitter_id,
            "data": {"id": splitter_id, "type": "SplitText"},
            "position": {"x": 300, "y": 100},
            "type": "genericNode"
        },
        {
            "id": embeddings_id,
            "data": {"id": embeddings_id, "type": "OpenAIEmbeddings"},
            "position": {"x": 500, "y": 100},
            "type": "genericNode"
        },
        {
            "id": vectorstore_id,
            "data": {"id": vectorstore_id, "type": "AstraDB"},
            "position": {"x": 700, "y": 100},
            "type": "genericNode"
        },
        {
            "id": chat_input_id,
            "data": {"id": chat_input_id, "type": "ChatInput"},
            "position": {"x": 100, "y": 300},
            "type": "genericNode"
        },
        {
            "id": prompt_id,
            "data": {"id": prompt_id, "type": "Prompt"},
            "position": {"x": 500, "y": 300},
            "type": "genericNode"
        },
        {
            "id": llm_id,
            "data": {"id": llm_id, "type": "LanguageModelComponent"},
            "position": {"x": 700, "y": 300},
            "type": "genericNode"
        },
        {
            "id": chat_output_id,
            "data": {"id": chat_output_id, "type": "ChatOutput"},
            "position": {"x": 900, "y": 300},
            "type": "genericNode"
        }
    ]
    
    # Create edges
    edges = [
        # Document processing chain
        {
            "id": f"reactflow__edge-{file_id}-{splitter_id}",
            "source": file_id,
            "target": splitter_id,
            "sourceHandle": "data",
            "targetHandle": "data",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{splitter_id}-{vectorstore_id}",
            "source": splitter_id,
            "target": vectorstore_id,
            "sourceHandle": "chunks",
            "targetHandle": "texts",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{embeddings_id}-{vectorstore_id}",
            "source": embeddings_id,
            "target": vectorstore_id,
            "sourceHandle": "embeddings",
            "targetHandle": "embedding",
            "animated": False
        },
        # Chat chain
        {
            "id": f"reactflow__edge-{chat_input_id}-{prompt_id}",
            "source": chat_input_id,
            "target": prompt_id,
            "sourceHandle": "message",
            "targetHandle": "question",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{vectorstore_id}-{prompt_id}",
            "source": vectorstore_id,
            "target": prompt_id,
            "sourceHandle": "documents",
            "targetHandle": "context",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{prompt_id}-{llm_id}",
            "source": prompt_id,
            "target": llm_id,
            "sourceHandle": "prompt",
            "targetHandle": "input_value",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{llm_id}-{chat_output_id}",
            "source": llm_id,
            "target": chat_output_id,
            "sourceHandle": "text_output",
            "targetHandle": "input_value",
            "animated": False
        }
    ]
    
    return {
        "data": {
            "nodes": nodes,
            "edges": edges,
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        },
        "name": workflow_name,
        "description": description
    }


def generate_agent_workflow(
    workflow_name: str = "Agent Workflow", 
    description: str = "AI agent with tools for complex tasks"
) -> dict[str, Any]:
    """Generate an agent workflow JSON.
    
    Args:
        workflow_name: Name of the workflow
        description: Description of the workflow
    
    Returns:
        Complete Langflow workflow JSON
    """
    
    # Generate unique IDs
    chat_input_id = f"ChatInput-{uuid.uuid4().hex[:8]}"
    agent_id = f"Agent-{uuid.uuid4().hex[:8]}"
    calc_tool_id = f"CalculatorComponent-{uuid.uuid4().hex[:8]}"
    search_tool_id = f"TavilySearchComponent-{uuid.uuid4().hex[:8]}"
    chat_output_id = f"ChatOutput-{uuid.uuid4().hex[:8]}"
    
    # Create nodes
    nodes = [
        {
            "id": chat_input_id,
            "data": {"id": chat_input_id, "type": "ChatInput"},
            "position": {"x": 100, "y": 200},
            "type": "genericNode"
        },
        {
            "id": calc_tool_id,
            "data": {"id": calc_tool_id, "type": "CalculatorComponent"},
            "position": {"x": 300, "y": 100},
            "type": "genericNode"
        },
        {
            "id": search_tool_id,
            "data": {"id": search_tool_id, "type": "TavilySearchComponent"},
            "position": {"x": 300, "y": 300},
            "type": "genericNode"
        },
        {
            "id": agent_id,
            "data": {"id": agent_id, "type": "Agent"},
            "position": {"x": 500, "y": 200},
            "type": "genericNode"
        },
        {
            "id": chat_output_id,
            "data": {"id": chat_output_id, "type": "ChatOutput"},
            "position": {"x": 700, "y": 200},
            "type": "genericNode"
        }
    ]
    
    # Create edges
    edges = [
        {
            "id": f"reactflow__edge-{chat_input_id}-{agent_id}",
            "source": chat_input_id,
            "target": agent_id,
            "sourceHandle": "message",
            "targetHandle": "input_value",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{calc_tool_id}-{agent_id}",
            "source": calc_tool_id,
            "target": agent_id,
            "sourceHandle": "component_as_tool",
            "targetHandle": "tools",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{search_tool_id}-{agent_id}",
            "source": search_tool_id,
            "target": agent_id,
            "sourceHandle": "component_as_tool",
            "targetHandle": "tools",
            "animated": False
        },
        {
            "id": f"reactflow__edge-{agent_id}-{chat_output_id}",
            "source": agent_id,
            "target": chat_output_id,
            "sourceHandle": "response",
            "targetHandle": "input_value",
            "animated": False
        }
    ]
    
    return {
        "data": {
            "nodes": nodes,
            "edges": edges,
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        },
        "name": workflow_name,
        "description": description
    }


# Workflow templates mapping
WORKFLOW_TEMPLATES = {
    "chat": generate_simple_chat_workflow,
    "simple": generate_simple_chat_workflow,
    "basic": generate_simple_chat_workflow,
    "rag": generate_rag_workflow,
    "document": generate_rag_workflow,
    "qa": generate_rag_workflow,
    "agent": generate_agent_workflow,
    "tools": generate_agent_workflow,
}


def get_workflow_template(workflow_type: str) -> dict[str, Any] | None:
    """Get a workflow template by type.
    
    Args:
        workflow_type: Type of workflow (chat, rag, agent, etc.)
    
    Returns:
        Workflow JSON or None if type not found
    """
    workflow_type = workflow_type.lower()
    
    for key, generator in WORKFLOW_TEMPLATES.items():
        if key in workflow_type:
            return generator()
    
    # Default to simple chat
    return generate_simple_chat_workflow()