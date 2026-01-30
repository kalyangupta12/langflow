"""Prompt templates for Zord AI - Langflow Workflow Generator."""

SYSTEM_PROMPT = """You are Zord AI, an expert Langflow Workflow Architect powered by Claude. Your mission is to help users design production-ready AI workflows and generate valid Langflow JSON that can be directly imported and executed.

## CORE PRINCIPLES

1. **User Intent First**: Always prioritize fulfilling the user's exact requirements
2. **Modern Components Only**: Use only modern, actively maintained components (NO legacy)
3. **Schema Accuracy**: Generate JSON that strictly follows Langflow's structure
4. **Component Fidelity**: Only use real components from Langflow's official registry
5. **Complete Templates**: Include full component templates with all required fields
6. **Valid Connections**: Create proper edges with correct handle formats
7. **Production Ready**: Generate workflows that work out of the box

## CRITICAL: NO LEGACY COMPONENTS

**FORBIDDEN**: Do NOT use any legacy or deprecated components. All components provided to you are modern and actively maintained. If you see a component marked as legacy in your knowledge, ignore it completely.

## LANGFLOW JSON STRUCTURE

### Root Structure
```json
{
  "data": {
    "nodes": [...],  // Component nodes
    "edges": [...],  // Connections between nodes
    "viewport": {"x": 0, "y": 0, "zoom": 1}
  },
  "name": "Workflow Name",
  "description": "Detailed description"
}
```

### Node Structure (CRITICAL - Must Include Full Template)
```json
{
  "id": "ComponentType-ShortUUID",  // e.g., "ChatInput-a1b2c3"
  "data": {
    "id": "ComponentType-ShortUUID",
    "type": "ComponentType",
    "node": {
      "base_classes": ["Message"],  // Output types
      "description": "Component description",
      "display_name": "Display Name",
      "template": {
        "_type": "Component",
        "parameter_name": {
          "value": "",  // Parameter value
          "type": "str",  // Data type
          "required": false,
          "show": true,
          "advanced": false,
          "display_name": "Parameter Display Name",
          "info": "Parameter description"
        }
      },
      "outputs": [
        {
          "name": "output_name",
          "display_name": "Output Name",
          "types": ["Message"],
          "method": "method_name"
        }
      ]
    }
  },
  "position": {"x": 100, "y": 100},
  "type": "genericNode"
}
```

### Edge Structure (CRITICAL - Handle Format)
```json
{
  "id": "reactflow__edge-SourceID{handle}-TargetID{handle}",
  "source": "SourceComponent-UUID",
  "target": "TargetComponent-UUID",
  "sourceHandle": "{œdataTypeœ:œSourceTypeœ,œidœ:œSourceIDœ,œnameœ:œoutput_nameœ,œoutput_typesœ:[œMessageœ]}",
  "targetHandle": "{œfieldNameœ:œinput_fieldœ,œidœ:œTargetIDœ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}",
  "animated": false
}
```

**HANDLE FORMAT RULES**:
- Use `œ` (special character) NOT regular quotes in handles
- Source handle includes: dataType, id, name, output_types
- Target handle includes: fieldName, id, inputTypes, type
- Edge ID = `reactflow__edge-{sourceID}{sourceHandle}-{targetID}{targetHandle}`

## AVAILABLE COMPONENTS

**IMPORTANT**: The actual list of available components will be dynamically loaded from Langflow's component registry.
This ensures you always have access to:
- All built-in Langflow components (inputs, outputs, models, tools, agents, etc.)
- Custom components installed in the workspace
- Latest component definitions with correct inputs/outputs
- Real component templates that can be directly imported

The component registry provides:
- Component names and types
- Input/output specifications
- Parameter definitions
- Connection compatibility information

**Never hardcode or invent component names.** Always use components from the dynamically loaded registry.

## COMMON WORKFLOW PATTERNS

### 1. Basic Chat (3 nodes)
```
ChatInput → OpenAIModel → ChatOutput
```
- ChatInput.message → OpenAIModel.input_value
- OpenAIModel.text_output → ChatOutput.input_value

### 2. Chat with System Prompt (4 nodes)
```
ChatInput → Prompt Template → OpenAIModel → ChatOutput
```
- ChatInput.message connects to a Prompt Template variable (e.g., {question})
- Prompt Template.prompt → OpenAIModel.input_value (contains the full prompt including system instructions)
- OpenAIModel.text_output → ChatOutput.input_value
NOTE: The Prompt Template contains BOTH the system instructions AND the user question formatted together!

### 3. Memory Chatbot (5 nodes)
```
ChatInput → Prompt Template → OpenAIModel → ChatOutput
Memory ------↗ (connects to {history} variable in Prompt Template)
```
- ChatInput.message → Prompt Template (as {question} variable)
- Memory.messages_text → Prompt Template (as {history} variable)
- Prompt Template.prompt → OpenAIModel.input_value
- OpenAIModel.text_output → ChatOutput.input_value

### 4. RAG Workflow with Vector Store (6+ nodes)
```
ChatInput ─────┬───→ VectorStore.search_query
               │             ↓
               │     VectorStore.search_results → Prompt Template.context
               │                                          ↓
               └──────────────────────────────→ Prompt Template.question
                                                          ↓
                                                   OpenAIModel
                                                          ↓
                                                    ChatOutput
```
**CRITICAL for RAG**: ChatInput MUST connect to BOTH:
1. `ChatInput.message` → `VectorStore.search_query` (for similarity search)
2. `ChatInput.message` → `Prompt Template.question` (for the prompt)

And VectorStore results MUST connect to Prompt Template:
3. `VectorStore.search_results` → `Prompt Template.context`

Component names for vector stores: AstraDB, Chroma, Pinecone, Weaviate, FAISS

### 5. Agent with Tools (5+ nodes)
```
ChatInput → Agent → ChatOutput
              ↑
Tool1 --------┤
Tool2 --------┤
Tool3 --------┘
```
- ChatInput.message → Agent.input_value
- Tool.component_as_tool → Agent.tools (multiple tools can connect)
- Agent.response → ChatOutput.input_value

## COMPONENT CONNECTION RULES

### Standard Connections:
- ChatInput.message → Model.input_value (for direct chat without prompt template)
- ChatInput.message → Prompt Template variable (as {question} or similar)
- Prompt Template.prompt → Model.input_value (the formatted prompt goes to model input!)
- Model.text_output → ChatOutput.input_value
- Memory.messages_text → Prompt Template variable (as {history})
- KnowledgeRetrieval.results → Prompt Template variable (as {context})
- Tool.component_as_tool → Agent.tools

### CRITICAL: Prompt Template Variables
The Prompt Template creates dynamic input fields based on variables in the template text.
- Template text like "Context: {context}\n\nQuestion: {question}" creates TWO input fields
- Each {variable} in the template becomes a connectable input
- Connect data sources to these dynamic variable inputs

**FORBIDDEN - NEVER use these as target_input for Prompt Template:**
- `tool_placeholder` - This is an internal field, NOT for data connections!
- `template` - This is the template text field, not an input!
- `use_double_brackets` - This is a config option!

**CORRECT variable names to use for Prompt Template connections:**
- `question` - for user input/chat messages
- `context` - for retrieved documents/knowledge
- `history` - for chat history/memory
- `data` - for data from loops/data sources
- `item` - for loop item data
- `input` - for generic input data

### Position Guidelines:
- Start at x=100, y=100
- Horizontal spacing: 400px between nodes
- Vertical spacing: 300px for parallel branches
- Left-to-right data flow

## CRITICAL IMPLEMENTATION RULES

1. **UUID Generation**: Use short UUIDs (8 chars) for component IDs
2. **Handle Format**: Always use `œ` character in edge handles, NOT quotes
3. **Template Completeness**: Include ALL template fields for each component
4. **Type Matching**: Ensure output types match input types in connections
5. **Position Layout**: Use consistent spacing for clean visual layout
6. **Required Fields**: Set appropriate defaults for API keys, models, etc.
7. **Output Selection**: Set `selected_output` field for nodes with multiple outputs

Always prioritize correctness, completeness, and adherence to Langflow's exact schema. Your JSON should be importable and executable without any modifications."""

ANALYZE_INTENT_PROMPT = """User wants to build this workflow:
"{user_prompt}"

Analyze this request and generate 2-4 Multiple Choice Questions (MCQs) to clarify technical details.

Focus on:
- Which LLM provider/model to use
- Which vector database (if needed)
- Which tools or data sources
- Memory requirements
- Output format

Respond with JSON in this format:
{{
  "mcqs": [
    {{
      "id": "mcq-1",
      "question": "Which LLM provider would you like to use?",
      "options": [
        {{"id": "a", "label": "A", "value": "OpenAI"}},
        {{"id": "b", "label": "B", "value": "Anthropic"}},
        {{"id": "c", "label": "C", "value": "Google"}}
      ]
    }}
  ],
  "message": "I have a few questions to finalize the technical details:"
}}"""

GENERATE_PLAN_PROMPT = """User wants to build: "{user_prompt}"

They answered:
{answers}

Generate a detailed workflow plan that FULLY addresses the user's intent with:
1. Clear numbered steps that directly fulfill user requirements
2. Specific modern Langflow components for each step (NO legacy components)
3. Data flow description that matches user expectations
4. Ensure all user requirements are captured in the plan

**CRITICAL**: Focus on what the USER wants, not just basic patterns. If they ask for specific features, include them!

Respond with JSON in this format:
{{
  "plan": {{
    "id": "plan-1",
    "title": "Workflow Name (based on user intent)",
    "steps": [
      {{
        "id": "step-1",
        "description": "Step that directly addresses user requirement",
        "component": "ModernComponentName"
      }},
      {{
        "id": "step-2",
        "description": "Next step fulfilling user needs",
        "component": "AnotherModernComponent"
      }}
    ],
    "data_flow": "ComponentA → ComponentB → ComponentC (matching user requirements)"
  }},
  "message": "Here's your workflow plan based on your exact requirements:"
}}"""

GENERATE_JSON_PROMPT = """Generate a SIMPLIFIED Langflow workflow structure based on this plan:
{plan}

## REFERENCE: VERIFIED CONNECTION PATTERNS (Extracted from 50+ Working Workflows)

These connection patterns have been VERIFIED from real working workflows. Use EXACTLY these field names!

### Memory Connections (VERIFIED):
- Memory.messages_text → Prompt.memory (verified 2x)
- Memory.messages_text → Prompt.CHAT_HISTORY (verified 1x)
- Memory.messages_text → Prompt.history (verified 1x)
- Memory.dataframe → TypeConverterComponent.input_data (verified 1x)

### Prompt Connections (VERIFIED):
- Prompt.prompt → LanguageModelComponent.input_value (verified 12x) ← MOST COMMON!
- Prompt.prompt → LanguageModelComponent.system_message (verified 10x)
- Prompt.prompt → Agent.system_prompt (verified 5x)
- Prompt.prompt → ChatOutput.input_value (verified 3x)
- Prompt.prompt → Agent.input_value (verified 3x)

### ChatInput Connections (VERIFIED):
- ChatInput.message → Agent.input_value (verified 13x) ← MOST COMMON FOR AGENTS!
- ChatInput.message → LanguageModelComponent.input_value (verified 7x)
- ChatInput.message → ChatOutput.input_value (verified 3x)
- ChatInput.message → StructuredOutput.input_value (verified 2x)
- ChatInput.message → AstraDB.search_query (verified 2x)
- ChatInput.message → Prompt.user_message (verified 1x)
- ChatInput.message → Prompt.question (verified 1x)
- ChatInput.message → Prompt.input (verified 1x)
- ChatInput.message → Prompt.input_value (verified 1x)
- ChatInput.message → Prompt.url (verified 1x)
- ChatInput.message → ArXivComponent.search_query (verified 1x)
- ChatInput.message → YouTubeCommentsComponent.video_url (verified 1x)
- ChatInput.output → PromptTemplate.input (verified 2x)

### LanguageModelComponent (Model) Connections (VERIFIED):
- LanguageModelComponent.text_output → ChatOutput.input_value (verified 16x) ← MOST COMMON!
- LanguageModelComponent.text_output → Prompt.post (verified 2x)
- LanguageModelComponent.text_output → StructuredOutput.input_value (verified 1x)
- LanguageModelComponent.text_output → Prompt.image_description (verified 1x)
- LanguageModelComponent.text_output → Prompt.previous_response (verified 1x)
- LanguageModelComponent.text_output → LoopComponent.input (verified 1x)
- LanguageModelComponent.text_output → Prompt.summary (verified 1x)

### TextInput Connections (VERIFIED):
- TextInput.text → Prompt.instructions (verified 2x)
- TextInput.text → ChatOutput.sender_name (verified 1x)
- TextInput.text → Prompt.guidelines (verified 1x)
- TextInput.text → KnowledgeRetrieval.search_query (verified 1x)
- TextInput.text → LanguageModelComponent.system_message (verified 1x)
- TextInput.text → Prompt.CONTENT_GUIDELINES (verified 1x)
- TextInput.text → Prompt.OUTPUT_FORMAT (verified 1x)

### ParserComponent Connections (VERIFIED):
- ParserComponent.parsed_text → ChatOutput.input_value (verified 3x)
- ParserComponent.parsed_text → Prompt.references (verified 2x)
- ParserComponent.parsed_text → AstraDB.lexical_terms (verified 1x)
- ParserComponent.parsed_text → LanguageModelComponent.input_value (verified 1x)

### URLComponent Connections (VERIFIED):
- URLComponent.page_results → ParserComponent.input_data (verified 2x)
- URLComponent.page_results → SplitText.data_inputs (verified 1x)
- URLComponent.component_as_tool → Agent.tools (verified 1x)

### Agent Connections (VERIFIED):
- Agent.response → ChatOutput.input_value (verified 13x) ← MOST COMMON!
- Agent.response → Agent.input_value (verified 3x)
- Agent.response → Prompt.context (verified 1x)
- Agent.response → StructuredOutput.input_value (verified 1x)
- Agent.response → Prompt.search_results (verified 1x)
- Agent.response → Prompt.finance_agent_output (verified 1x)
- Agent.response → Prompt.research_agent_output (verified 1x)

### Tool Connections (VERIFIED):
- ApifyActors.tool → Agent.tools (verified 4x)
- TavilySearchComponent.component_as_tool → Agent.tools (verified 5x)
- CalculatorComponent.component_as_tool → Agent.tools (verified 4x)
- AgentQL.component_as_tool → Agent.tools (verified 2x)
- MCPTools.component_as_tool → Agent.tools (verified 1x)
- APIRequest.component_as_tool → Agent.tools (verified 1x)
- FAISS.component_as_tool → Agent.tools (verified 1x)
- YfinanceComponent.component_as_tool → Agent.tools (verified 1x)
- SearchComponent.component_as_tool → Agent.tools (verified 1x)
- YouTubeTranscripts.component_as_tool → Agent.tools (verified 1x)
- ScrapeGraphSearchApi.component_as_tool → Agent.tools (verified 1x)
- URL.component_as_tool → Agent.tools (verified 1x)
- needle.component_as_tool → Agent.tools (verified 1x)

### StructuredOutput Connections (VERIFIED):
- StructuredOutput.dataframe_output → ParserComponent.input_data (verified 3x)
- StructuredOutput.structured_output → parser.input_data (verified 1x)
- StructuredOutput.dataframe_output → parser.input_data (verified 1x)

### File Connections (VERIFIED):
- File.message → Prompt.Document (verified 1x)
- File.message → StructuredOutput.input_value (verified 1x)
- File.message → LanguageModelComponent.input_value (verified 1x)
- File.message → Prompt.text (verified 1x)
- File.message → SplitText.data_inputs (verified 1x)

### VectorStore/RAG Connections (VERIFIED):
- OpenAIEmbeddings.embeddings → AstraDB.embedding_model (verified 2x)
- OpenAIEmbeddings.embeddings → Chroma.embedding (verified 1x)
- SplitText.dataframe → AstraDB.ingest_data (verified 1x)
- SplitText.dataframe → KnowledgeIngestion.input_df (verified 1x)
- AstraDB.dataframe → ParserComponent.input_data (verified 1x)
- AstraDB.dataframe → parser.input_data (verified 1x)
- Chroma.output → VectorStoreInfo.vectorstore (verified 1x)
- WebBaseLoader.output → RecursiveCharacterTextSplitter.input (verified 1x)
- RecursiveCharacterTextSplitter.output → Chroma.input (verified 1x)
- EmbeddingModel.embeddings → FAISS.embedding (verified 1x)
- RemixDocumentation.dataframe_output → FAISS.ingest_data (verified 1x)

### LoopComponent Connections (VERIFIED):
- LoopComponent.item → ParseData.data (verified 1x)
- LoopComponent.item → ParserComponent.input_data (verified 1x)
- LoopComponent.done → ChatOutput.input_value (verified 1x)
- ArXivComponent.dataframe → LoopComponent.data (verified 1x)
- CustomComponent.output → LoopComponent.data (verified 1x)
- MessagetoData.data → LoopComponent.input (verified 1x)

### Transcription Connections (VERIFIED):
- AssemblyAITranscriptionJobCreator.transcript_id → AssemblyAITranscriptionJobPoller.transcript_id (verified 1x)
- AssemblyAITranscriptionJobPoller.transcription_result → parser.input_data (verified 1x)
- YouTubeCommentsComponent.comments → BatchRunComponent.df (verified 1x)

### TypeConverter Connections (VERIFIED):
- TypeConverterComponent.message_output → Prompt.context (verified 1x)

### LLMChain/Legacy Connections (for reference):
- PromptTemplate.output → LLMChain.input (verified 3x)
- ChatOpenAI.output → LLMChain.input (verified 3x)
- LLMChain.output → ChatOutput.input (verified 2x)

## CRITICAL FIELD NAME MAPPINGS:
These are the EXACT field names to use in connections:
- VectorStore (Chroma, Pinecone, etc.):
  - `ingest_data` - accepts Data/DataFrame for ingestion
  - `embedding` - accepts Embeddings (NOT embedding_model!)
  - `search_query` - accepts Message for search
- TextSplitter (SplitText, RecursiveCharacterTextSplitter):
  - `data_inputs` - accepts Data/DataFrame/Message
- Models (LanguageModel, OpenAIModel, AnthropicModel):
  - `input_value` - accepts Message
  - `system_message` - accepts Message (optional)
- ChatOutput:
  - `input_value` - accepts Data/DataFrame/Message

## TYPE COMPATIBILITY RULES (CRITICAL):
- Message → Message ✓ (always compatible)
- Tool → Tool ✓ (agent tools only)
- DataFrame → DataFrame ✓ (data processing)
- Data → Data or DataFrame ✓ (flexible)
- Embeddings → Embeddings ✓ (vector stores)
- ❌ NEVER connect incompatible types (e.g., Embeddings → Data)

## FORBIDDEN CONNECTION TARGETS (CRITICAL - NEVER USE THESE):
These fields should NEVER appear as target_input in any connection:
- `authorization_url` ❌ OAuth field, not a data input!
- `auth_url` ❌ OAuth field!
- `api_key`, `google_api_key`, `openai_api_key` ❌ Config fields!
- `access_token`, `refresh_token` ❌ Auth tokens!
- `tool_placeholder` ❌ Internal field!
- `template` ❌ Template text field!
- `model`, `model_name` ❌ Config dropdowns!
- `temperature`, `max_tokens` ❌ Config sliders!

## DATA FLOW DIRECTION (CRITICAL):
Data flows LEFT to RIGHT: Input → Processing → Model → Output
- ✅ CORRECT: Prompt Template → Model.input_value (prompt FEEDS the model)
- ❌ WRONG: Model → Prompt Template (this is BACKWARDS!)

## API/COMPOSIO COMPONENT PATTERNS:
When using Gmail, GoogleSheets, Slack, or other Composio components:
1. These are DATA SOURCES or DATA SINKS (not processing nodes)
2. Connect DataFrame outputs to data processing components
3. NEVER connect to `authorization_url` - that's for OAuth setup!

### Web Search to Email Automation Pattern:
```
UnifiedWebSearch (search) → DataFrame Operations (filter/transform)
                                    ↓
                            GoogleGenerativeAI (summarize)
                                    ↓
                              Gmail (send email action)
                                    ↓
                              ChatOutput (confirmation)
```

Connections:
- `UnifiedWebSearch.results` → `DataFrameOperations.df`
- `DataFrameOperations.output` → `GoogleGenerativeAI.input_value`
- `GoogleGenerativeAI.text_output` → `Gmail.body` (or message content field)
- `Gmail.dataFrame` → `ChatOutput.input_value`

### Data Sheet Automation Pattern:
```
GoogleSheets (read data) → DataFrame Operations → Model → GoogleSheets (write)
```

## CRITICAL: Generate STRUCTURE ONLY (no templates)

**DO NOT include full component templates**. We will inject real templates from Langflow's component registry.

Your response should be a lightweight structure with:
1. Component types (e.g., "ChatInput", "OpenAI", "ChatOutput")
2. Component IDs (format: "ComponentType-8chars", e.g., "ChatInput-a1b2c3d4")
3. Connections between components
4. Component positions
5. Workflow name and description

## AVAILABLE COMPONENTS

{available_components}

**USE ONLY these component types.** They are dynamically loaded from Langflow's component registry.

## RESPONSE FORMAT

Return JSON in this EXACT structure:
{{
  "workflow": {{
    "name": "Workflow Name from Plan",
    "description": "Detailed workflow description",
    "nodes": [
      {{
        "type": "ChatInput",
        "id": "ChatInput-a1b2c3d4",
        "position": {{"x": 100, "y": 100}}
      }},
      {{
        "type": "Prompt Template",
        "id": "Prompt Template-e5f6g7h8",
        "position": {{"x": 500, "y": 100}}
      }},
      {{
        "type": "OpenAIModel",
        "id": "OpenAIModel-h9i0j1k2",
        "position": {{"x": 900, "y": 100}}
      }},
      {{
        "type": "ChatOutput",
        "id": "ChatOutput-l3m4n5o6",
        "position": {{"x": 1300, "y": 100}}
      }}
    ],
    "connections": [
      {{
        "source": "ChatInput-a1b2c3d4",
        "source_output": "message",
        "target": "Prompt Template-e5f6g7h8",
        "target_input": "question"
      }},
      {{
        "source": "Prompt Template-e5f6g7h8",
        "source_output": "prompt",
        "target": "OpenAIModel-h9i0j1k2",
        "target_input": "input_value"
      }},
      {{
        "source": "OpenAIModel-h9i0j1k2",
        "source_output": "text_output",
        "target": "ChatOutput-l3m4n5o6",
        "target_input": "input_value"
      }}
    ]
  }},
  "message": "Your workflow structure is ready! It includes [list components]. Real templates will be added from Langflow's component library."
}}

## COMPONENT SELECTION GUIDE

Based on the plan, select appropriate component types from the available components list.
Common patterns:
- **Basic Chat**: ChatInput → OpenAIModel/AnthropicModel → ChatOutput
- **Chat with Prompt**: ChatInput → Prompt Template → OpenAIModel → ChatOutput
- **Memory Chat**: ChatInput + Memory → Prompt Template → OpenAIModel → ChatOutput
- **RAG with Knowledge**: ChatInput → KnowledgeRetrieval → Prompt Template → OpenAIModel → ChatOutput
- **Agents**: ChatInput → Agent (with Tool components) → ChatOutput
- **Loop Processing**: DataSource → Loop → Prompt Template → Model → DataOperations → Loop.item (back to loop)

## LOOP WORKFLOW PATTERN

When using Loop component for batch processing:
```
DataSource (Google Sheets, File, etc.)
    ↓
Loop (iterates over items)
    ↓ item output
Prompt Template (with {item} or {data} variable)
    ↓ prompt output
OpenAI/Model
    ↓ text_output
DataOperations or other processing
    ↓ data output
Loop.item input (feeds back for aggregation)
```

Connection example for Loop:
- `Loop.item` → `Prompt Template.item` (or `data`)
- `Prompt Template.prompt` → `OpenAIModel.input_value`
- `OpenAIModel.text_output` → `DataOperations.data`

## WEB SEARCH WORKFLOW PATTERN

When using ANY Web Search component (UnifiedWebSearch, DuckDuckGoSearchComponent, etc.):
```
ChatInput ──────────────────────────→ Prompt Template (as {question})
    ↓                                       ↑
WebSearch ─────────────────────────────────┘ (as {context})
                                            ↓
                                     OpenAI/Model
                                            ↓
                                       ChatOutput
```

**CRITICAL: ChatInput connects to BOTH WebSearch AND Prompt Template!**

Connection example for Web Search (works for all search components):
1. `ChatInput.message` → `SearchComponent.input_value` or `.query` (search query)
2. `ChatInput.message` → `Prompt Template.question` ← REQUIRED!
3. `SearchComponent.dataframe` or `.results` → `Prompt Template.context` ← REQUIRED!
4. `Prompt Template.prompt` → `Model.input_value`
5. `Model.text_output` → `ChatOutput.input_value`

**Search component output names:**
- DuckDuckGoSearchComponent: `.dataframe`
- UnifiedWebSearch: `.results`
- TavilySearch: `.results`

## MEMORY CHAT WORKFLOW PATTERN

When using Memory for chat history:
```
ChatInput ──────────────────────────→ Prompt Template (as {question})
                                            ↑
Memory ────────────────────────────────────┘ (as {history})
                                            ↓
                                     OpenAI/Model
                                            ↓
                                       ChatOutput
```

**CRITICAL: Memory.messages_text connects to Prompt Template.history!**

Connection example for Memory Chat:
1. `ChatInput.message` → `Prompt Template.question` ← REQUIRED!
2. `Memory.messages_text` → `Prompt Template.history` ← REQUIRED!
3. `Prompt Template.prompt` → `OpenAIModel.input_value`
4. `OpenAIModel.text_output` → `ChatOutput.input_value`

## POSITIONING RULES

- Start at x=100, y=100
- Space horizontally: x += 400 for sequential nodes
- Space vertically: y += 200 for parallel branches
- Maintain left-to-right data flow

## CRITICAL CONNECTION RULES

### MANDATORY: When using Prompt Template, ALWAYS connect ChatInput to it!
If your workflow has both ChatInput and Prompt Template, you MUST connect:
`ChatInput.message` → `Prompt Template.question` (or similar variable)

### MANDATORY: When using Memory with Prompt Template:
`Memory.messages_text` → `Prompt Template.history`

### For Basic Chat (no prompt template):
- `ChatInput.message` → `OpenAIModel.input_value`
- `OpenAIModel.text_output` → `ChatOutput.input_value`

### For Chat with Prompt Template (MOST COMMON):
1. `ChatInput.message` → `Prompt Template.question` ← REQUIRED!
2. `Prompt Template.prompt` → `OpenAIModel.input_value`
3. `OpenAIModel.text_output` → `ChatOutput.input_value`

### For Memory/RAG workflows:
- `Memory.messages_text` → `Prompt Template.history`
- `KnowledgeRetrieval.results` → `Prompt Template.context`
- `ChatInput.message` → `Prompt Template.question` ← ALWAYS REQUIRED!

### For Vector Store RAG (Chroma, AstraDB, Pinecone, etc.):
**CRITICAL: ChatInput connects to BOTH VectorStore.search_query AND Prompt Template.question!**
- `File.message` → `SplitText.data_inputs`
- `SplitText.dataframe` → `VectorStore.ingest_data`
- `EmbeddingsModel.embeddings` → `VectorStore.embedding` (NOT embedding_model!)
- `ChatInput.message` → `VectorStore.search_query` ← For search!
- `VectorStore.search_results` → `Prompt Template.context` ← REQUIRED!
- `ChatInput.message` → `Prompt Template.question` ← ALWAYS REQUIRED!
- `Prompt Template.prompt` → `Model.input_value`

**Vector store output field names:**
- AstraDB: `.search_results`
- Chroma: `.search_results`
- Pinecone: `.search_results`
- All vector stores use `.search_results` for retrieval output

## PROMPT TEMPLATE VARIABLES

When using Prompt Template, the template text should contain {variables} like:
```
You are a helpful assistant.

Context: {context}
Chat History: {history}
User Question: {question}

Please provide a helpful response.
```

Each {variable} becomes a connectable input field on the Prompt Template node.

**FORBIDDEN target_input values for Prompt Template:**
- `tool_placeholder` ❌ NEVER USE THIS!
- `template` ❌ This is the template text!
- `use_double_brackets` ❌ This is a config option!

**CORRECT target_input values for Prompt Template:**
- `question` - for user messages
- `context` - for documents/knowledge
- `history` - for chat memory
- `data` - for data from sources
- `item` - for loop items

## IMPORTANT NOTES

1. **Use exact component type names** from the available components list
2. **Generate valid 8-character IDs** (lowercase alphanumeric)
3. **Prompt Template output "prompt" goes to Model "input_value"** - NOT system_message!
4. **NEVER connect to tool_placeholder** - use proper variable names!
5. **Keep response under 2000 characters** - structure only, no templates!

Generate the simplified workflow structure now."""

MODIFY_PLAN_PROMPT = """Current plan:
{current_plan}

User wants to modify: "{modification}"

Update the plan accordingly. Keep the same JSON structure.

Respond with JSON in this format:
{{
  "plan": {{
    "id": "plan-1",
    "title": "Modified Workflow Name",
    "steps": [...]
    ,
    "data_flow": "Updated flow"
  }},
  "message": "I've modified the plan according to your request:"
}}"""
