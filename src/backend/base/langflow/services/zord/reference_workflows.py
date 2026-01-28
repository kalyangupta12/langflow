"""Reference workflows for Zord AI to learn from.

These are working, validated Langflow workflows that demonstrate proper:
- Component connections and edge patterns
- Type compatibility between outputs and inputs
- Common workflow structures
- Tool usage patterns
"""

# Simple Agent workflow - demonstrates agent with tools
SIMPLE_AGENT_REFERENCE = {
    "name": "Simple Agent",
    "description": "A simple but powerful starter agent.",
    "pattern": "agent_with_tools",
    "components": ["ChatInput", "Agent", "ChatOutput", "CalculatorComponent", "URLComponent"],
    "key_connections": [
        {
            "source": "ChatInput",
            "source_output": "message",
            "source_types": ["Message"],
            "target": "Agent",
            "target_input": "input_value",
            "target_types": ["Message"],
            "note": "User input goes to agent"
        },
        {
            "source": "Agent",
            "source_output": "response",
            "source_types": ["Message"],
            "target": "ChatOutput",
            "target_input": "input_value",
            "target_types": ["Data", "DataFrame", "Message"],
            "note": "Agent output goes to chat display"
        },
        {
            "source": "CalculatorComponent",
            "source_output": "component_as_tool",
            "source_types": ["Tool"],
            "target": "Agent",
            "target_input": "tools",
            "target_types": ["Tool"],
            "note": "Tool connection to agent"
        },
        {
            "source": "URLComponent",
            "source_output": "component_as_tool",
            "source_types": ["Tool"],
            "target": "Agent",
            "target_input": "tools",
            "target_types": ["Tool"],
            "note": "Tool connection to agent"
        }
    ],
    "insights": [
        "Agents accept Message type for input_value field",
        "Tools connect to agents via 'tools' field which accepts Tool type",
        "Multiple tools can connect to same agent",
        "ChatOutput accepts Data, DataFrame, or Message types"
    ]
}

# YouTube Analysis workflow - demonstrates complex multi-component RAG pattern
YOUTUBE_ANALYSIS_REFERENCE = {
    "name": "YouTube Analysis",
    "description": "Complex workflow with data extraction, processing, and agent analysis",
    "pattern": "data_processing_agent",
    "components": [
        "ChatInput", "YouTubeCommentsComponent", "YouTubeTranscripts", 
        "BatchRunComponent", "parser", "Prompt", "Agent", "ChatOutput"
    ],
    "key_connections": [
        {
            "source": "ChatInput",
            "source_output": "message",
            "source_types": ["Message"],
            "target": "YouTubeCommentsComponent",
            "target_input": "video_url",
            "target_types": ["Message"],
            "note": "User input (URL) to data source"
        },
        {
            "source": "YouTubeCommentsComponent",
            "source_output": "comments",
            "source_types": ["DataFrame"],
            "target": "BatchRunComponent",
            "target_input": "df",
            "target_types": ["DataFrame"],
            "note": "DataFrame to DataFrame processing"
        },
        {
            "source": "parser",
            "source_output": "parsed_text",
            "source_types": ["Message"],
            "target": "Prompt",
            "target_input": "analysis",
            "target_types": ["Message"],
            "note": "Parsed data to prompt variable"
        },
        {
            "source": "Prompt",
            "source_output": "prompt",
            "source_types": ["Message"],
            "target": "Agent",
            "target_input": "input_value",
            "target_types": ["Message"],
            "note": "Prompt to agent input"
        },
        {
            "source": "YouTubeTranscripts",
            "source_output": "component_as_tool",
            "source_types": ["Tool"],
            "target": "Agent",
            "target_input": "tools",
            "target_types": ["Tool"],
            "note": "Tool connection"
        }
    ],
    "insights": [
        "DataFrame outputs connect to DataFrame inputs (type matching)",
        "Parser/data processing components output Message type",
        "Prompts can have dynamic variables that accept Message type",
        "Batch processing components work with DataFrame type",
        "Tools can be used alongside direct inputs in agents"
    ]
}

# Common patterns extracted from references
COMMON_PATTERNS = {
    "agent_with_tools": {
        "structure": "ChatInput -> Agent (with Tools) -> ChatOutput",
        "components": ["ChatInput", "Agent", "ChatOutput", "Tool components"],
        "key_fields": {
            "Agent.input_value": ["Message"],
            "Agent.tools": ["Tool"],
            "ChatOutput.input_value": ["Data", "DataFrame", "Message"]
        }
    },
    "basic_chat": {
        "structure": "ChatInput -> Model -> ChatOutput",
        "components": ["ChatInput", "LLM Model", "ChatOutput"],
        "key_fields": {
            "Model.input_value": ["Message"],
            "Model.system_message": ["Message"],
            "ChatOutput.input_value": ["Data", "DataFrame", "Message"]
        }
    },
    "rag_workflow": {
        "structure": "Data Source -> Splitter -> Embeddings -> Vector Store -> Retrieval -> Model -> Output",
        "components": ["Data Source", "Text Splitter", "Embeddings", "Vector Store", "Model", "ChatOutput"],
        "key_fields": {
            "TextSplitter.data_input": ["Data"],
            "VectorStore.ingest_data": ["Data", "DataFrame"],
            "VectorStore.embedding": ["Embeddings"],
            "Model.input_value": ["Message"]
        }
    }
}

# Type compatibility rules learned from references
TYPE_COMPATIBILITY_RULES = {
    "Message": {
        "can_connect_to": ["Message", "str fields with Message in input_types"],
        "common_sources": ["ChatInput.message", "Prompt.prompt", "Model.text_output", "Parser.parsed_text"],
        "common_targets": ["Model.input_value", "Agent.input_value", "Prompt variables", "ChatOutput.input_value"]
    },
    "Tool": {
        "can_connect_to": ["Tool"],
        "common_sources": ["Component.component_as_tool (when tool_mode=true)"],
        "common_targets": ["Agent.tools"]
    },
    "DataFrame": {
        "can_connect_to": ["DataFrame"],
        "common_sources": ["DataSource.output", "VectorStore.search_results"],
        "common_targets": ["VectorStore.ingest_data", "BatchRun.df", "Parser.data"]
    },
    "Data": {
        "can_connect_to": ["Data", "DataFrame"],
        "common_sources": ["TextSplitter.data", "Component.result"],
        "common_targets": ["VectorStore.ingest_data", "Model inputs"]
    },
    "Embeddings": {
        "can_connect_to": ["Embeddings"],
        "common_sources": ["OpenAIEmbeddings.embeddings", "EmbeddingModel.embeddings"],
        "common_targets": ["VectorStore.embedding"]
    }
}

# Component-specific connection rules
COMPONENT_CONNECTION_RULES = {
    "Agent": {
        "required_inputs": ["input_value"],
        "input_value": {
            "accepted_types": ["Message"],
            "typical_sources": ["ChatInput.message", "Prompt.prompt"]
        },
        "tools": {
            "accepted_types": ["Tool"],
            "typical_sources": ["*.component_as_tool"],
            "note": "Can accept multiple tool connections"
        }
    },
    "ChatOutput": {
        "required_inputs": ["input_value"],
        "input_value": {
            "accepted_types": ["Data", "DataFrame", "Message"],
            "typical_sources": ["Agent.response", "Model.text_output", "*.message"]
        }
    },
    "VectorStore": {
        "required_inputs": ["ingest_data", "embedding"],
        "ingest_data": {
            "accepted_types": ["Data", "DataFrame"],
            "typical_sources": ["TextSplitter.data", "DataSource.output"]
        },
        "embedding": {
            "accepted_types": ["Embeddings"],
            "typical_sources": ["OpenAIEmbeddings.embeddings"]
        }
    }
}


def get_reference_examples() -> list[dict]:
    """Get all reference workflow examples."""
    return [SIMPLE_AGENT_REFERENCE, YOUTUBE_ANALYSIS_REFERENCE]


def get_pattern_by_name(pattern_name: str) -> dict | None:
    """Get a specific workflow pattern by name."""
    return COMMON_PATTERNS.get(pattern_name)


def get_type_compatibility(type_name: str) -> dict | None:
    """Get compatibility rules for a specific type."""
    return TYPE_COMPATIBILITY_RULES.get(type_name)


def get_component_rules(component_name: str) -> dict | None:
    """Get connection rules for a specific component."""
    return COMPONENT_CONNECTION_RULES.get(component_name)


def format_references_for_prompt() -> str:
    """Format reference information for inclusion in AI prompts."""
    prompt_text = """
# Reference Workflow Examples

## Working Connection Patterns:

### Simple Agent Pattern:
- ChatInput.message (Message) → Agent.input_value (Message)
- Tool.component_as_tool (Tool) → Agent.tools (Tool)
- Agent.response (Message) → ChatOutput.input_value (Message)

### Data Processing Pattern:
- DataSource.output (DataFrame) → BatchRun.df (DataFrame)
- Parser.parsed_text (Message) → Prompt.variable (Message)
- Prompt.prompt (Message) → Agent.input_value (Message)

## Type Compatibility Rules:
- Message → Message (always compatible)
- Tool → Tool (only for agent tools)
- DataFrame → DataFrame (data processing)
- Data → Data or DataFrame (flexible)
- Embeddings → Embeddings (vector stores only)

## Critical Rules:
1. ALWAYS match output types with input types
2. Use 'input_value' for Message inputs to models/agents
3. Use 'tools' field for Tool connections to agents
4. Use 'ingest_data' for Data/DataFrame to vector stores
5. Check component's input_types array for compatibility
"""
    return prompt_text
