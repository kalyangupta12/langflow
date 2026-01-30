# Generated from 52 working workflows
# Add this to reference_workflows.py

LEARNED_WORKFLOWS = {
    "memory_chatbot": {
        "structure": "ChatInput → ChatOutput → note → Prompt → Memory → LanguageModelComponent",
        "components": ["ChatInput","ChatOutput","note","Prompt","Memory","LanguageModelComponent"],
        "connections": [
            {"source": "Memory", "source_output": "messages_text", "target": "Prompt", "target_input": "memory"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "blog_writer_1_": {
        "structure": "Prompt → TextInput → ChatOutput → note → ParserComponent → URLComponent → LanguageModelComponent",
        "components": ["Prompt","TextInput","ChatOutput","note","ParserComponent","URLComponent","LanguageModelComponent"],
        "connections": [
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "instructions"},
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "Prompt", "target_input": "references"},
            {"source": "URLComponent", "source_output": "page_results", "target": "ParserComponent", "target_input": "input_data"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "basicexample": {
        "structure": "TimeTravelGuideChain → OpenAI → ConversationBufferMemory",
        "components": ["TimeTravelGuideChain","OpenAI","ConversationBufferMemory"],
        "connections": [
            {"source": "OpenAI", "source_output": "output", "target": "TimeTravelGuideChain", "target_input": "input"},
            {"source": "ConversationBufferMemory", "source_output": "output", "target": "TimeTravelGuideChain", "target_input": "input"},
        ],
    },
    "chatinputtest": {
        "structure": "PromptTemplate → LLMChain → ChatOpenAI → ChatInput → ChatOutput",
        "components": ["PromptTemplate","LLMChain","ChatOpenAI","ChatInput","ChatOutput"],
        "connections": [
            {"source": "PromptTemplate", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "ChatOpenAI", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "ChatInput", "source_output": "output", "target": "PromptTemplate", "target_input": "input"},
            {"source": "LLMChain", "source_output": "output", "target": "ChatOutput", "target_input": "input"},
        ],
    },
    "basic_chat_with_prompt_and_history_2_": {
        "structure": "ChatOpenAI → LLMChain → PromptTemplate → ConversationBufferMemory",
        "components": ["ChatOpenAI","LLMChain","PromptTemplate","ConversationBufferMemory"],
        "connections": [
            {"source": "ChatOpenAI", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "PromptTemplate", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "ConversationBufferMemory", "source_output": "output", "target": "LLMChain", "target_input": "input"},
        ],
    },
    "env_variable_test": {
        "structure": "Secret → ChatOutput",
        "components": ["Secret","ChatOutput"],
        "connections": [
            {"source": "Secret", "source_output": "text", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "complex_example": {
        "structure": "ZeroShotAgent → ZeroShotAgent → Tool → PythonFunctionTool → LLMChain → ZeroShotPrompt → OpenAI",
        "components": ["ZeroShotAgent","Tool","PythonFunctionTool","LLMChain","ZeroShotPrompt","OpenAI"],
        "connections": [
            {"source": "Tool", "source_output": "output", "target": "ZeroShotAgent", "target_input": "input"},
            {"source": "ZeroShotAgent", "source_output": "output", "target": "Tool", "target_input": "input"},
            {"source": "PythonFunctionTool", "source_output": "output", "target": "ZeroShotAgent", "target_input": "input"},
            {"source": "ZeroShotPrompt", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "OpenAI", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "LLMChain", "source_output": "output", "target": "ZeroShotAgent", "target_input": "input"},
            {"source": "LLMChain", "source_output": "output", "target": "ZeroShotAgent", "target_input": "input"},
        ],
    },
    "grouptest": {
        "structure": "ChatOpenAI → PromptTemplate → LLMChain",
        "components": ["ChatOpenAI","PromptTemplate","LLMChain"],
        "connections": [
            {"source": "PromptTemplate", "source_output": "output", "target": "LLMChain", "target_input": "prompt_LLMChain-2P369"},
            {"source": "ChatOpenAI", "source_output": "output", "target": "LLMChain", "target_input": "llm_LLMChain-2P369"},
        ],
    },
    "untitled_document": {
        "structure": "MyZipper → CustomComponent → LoopComponent → MessagetoData → ParseData → ChatOutput",
        "components": ["MyZipper","CustomComponent","LoopComponent","MessagetoData","ParseData","ChatOutput"],
        "connections": [
            {"source": "CustomComponent", "source_output": "output", "target": "LoopComponent", "target_input": "data"},
            {"source": "MessagetoData", "source_output": "data", "target": "LoopComponent", "target_input": "input"},
            {"source": "LoopComponent", "source_output": "item", "target": "ParseData", "target_input": "data"},
            {"source": "ParseData", "source_output": "text", "target": "MessagetoData", "target_input": "message"},
            {"source": "CustomComponent", "source_output": "output", "target": "MyZipper", "target_input": "list2"},
            {"source": "LoopComponent", "source_output": "done", "target": "MyZipper", "target_input": "list1"},
            {"source": "MyZipper", "source_output": "output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "memorychatbotnollm": {
        "structure": "Prompt → ChatInput → ChatOutput → Memory → TypeConverterComponent",
        "components": ["Prompt","ChatInput","ChatOutput","Memory","TypeConverterComponent"],
        "connections": [
            {"source": "Memory", "source_output": "dataframe", "target": "TypeConverterComponent", "target_input": "input_data"},
            {"source": "TypeConverterComponent", "source_output": "message_output", "target": "Prompt", "target_input": "context"},
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "user_message"},
            {"source": "Prompt", "source_output": "prompt", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "one_group": {
        "structure": "LLMChain",
        "components": ["LLMChain"],
        "connections": [
        ],
    },
    "openapi": {
        "structure": "JsonToolkit → OpenAPIToolkit → JsonAgent → TextRequestsWrapper → JsonSpec → ChatOpenAI",
        "components": ["JsonToolkit","OpenAPIToolkit","JsonAgent","TextRequestsWrapper","JsonSpec","ChatOpenAI"],
        "connections": [
            {"source": "JsonToolkit", "source_output": "output", "target": "JsonAgent", "target_input": "input"},
            {"source": "JsonAgent", "source_output": "output", "target": "OpenAPIToolkit", "target_input": "input"},
            {"source": "TextRequestsWrapper", "source_output": "output", "target": "OpenAPIToolkit", "target_input": "input"},
            {"source": "JsonSpec", "source_output": "output", "target": "JsonToolkit", "target_input": "input"},
            {"source": "ChatOpenAI", "source_output": "output", "target": "JsonAgent", "target_input": "input"},
        ],
    },
    "simplechatnollm": {
        "structure": "ChatInput → ChatOutput",
        "components": ["ChatInput","ChatOutput"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "simple_api_test": {
        "structure": "ChatInput → TextInput → ChatOutput",
        "components": ["ChatInput","TextInput","ChatOutput"],
        "connections": [
            {"source": "TextInput", "source_output": "text", "target": "ChatOutput", "target_input": "sender_name"},
            {"source": "ChatInput", "source_output": "message", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "twooutputstest": {
        "structure": "PromptTemplate → LLMChain → ChatOpenAI → ChatOutput → ChatInput → Tool",
        "components": ["PromptTemplate","LLMChain","ChatOpenAI","ChatOutput","ChatInput","Tool"],
        "connections": [
            {"source": "PromptTemplate", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "ChatOpenAI", "source_output": "output", "target": "LLMChain", "target_input": "input"},
            {"source": "ChatInput", "source_output": "output", "target": "PromptTemplate", "target_input": "input"},
            {"source": "LLMChain", "source_output": "output", "target": "ChatOutput", "target_input": "input"},
            {"source": "LLMChain", "source_output": "output", "target": "Tool", "target_input": "input"},
        ],
    },
    "vector_store": {
        "structure": "VectorStoreAgent → VectorStoreInfo → OpenAIEmbeddings → Chroma → RecursiveCharacterTextSplitter → WebBaseLoader → ChatOpenAI",
        "components": ["VectorStoreAgent","VectorStoreInfo","OpenAIEmbeddings","Chroma","RecursiveCharacterTextSplitter","WebBaseLoader","ChatOpenAI"],
        "connections": [
            {"source": "VectorStoreInfo", "source_output": "output", "target": "VectorStoreAgent", "target_input": "input"},
            {"source": "Chroma", "source_output": "output", "target": "VectorStoreInfo", "target_input": "input"},
            {"source": "WebBaseLoader", "source_output": "output", "target": "RecursiveCharacterTextSplitter", "target_input": "input"},
            {"source": "RecursiveCharacterTextSplitter", "source_output": "output", "target": "Chroma", "target_input": "input"},
            {"source": "ChatOpenAI", "source_output": "output", "target": "VectorStoreAgent", "target_input": "input"},
            {"source": "OpenAIEmbeddings", "source_output": "output", "target": "Chroma", "target_input": "input"},
        ],
    },
    "vector_store": {
        "structure": "VectorStoreAgent → VectorStoreInfo → ChatOpenAI → Chroma",
        "components": ["VectorStoreAgent","VectorStoreInfo","ChatOpenAI","Chroma"],
        "connections": [
            {"source": "VectorStoreInfo", "source_output": "output", "target": "VectorStoreAgent", "target_input": "vectorstoreinfo"},
            {"source": "ChatOpenAI", "source_output": "output", "target": "VectorStoreAgent", "target_input": "llm"},
            {"source": "Chroma", "source_output": "output", "target": "VectorStoreInfo", "target_input": "vectorstore"},
        ],
    },
    "webhook_test": {
        "structure": "CustomComponent → Webhook → ChatInput → ChatOutput → CustomComponent",
        "components": ["CustomComponent","Webhook","ChatInput","ChatOutput"],
        "connections": [
            {"source": "Webhook", "source_output": "output_data", "target": "CustomComponent", "target_input": "input_value"},
            {"source": "ChatInput", "source_output": "message", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "CustomComponent", "source_output": "output", "target": "CustomComponent", "target_input": "input_value"},
        ],
    },
    "social_media_agent_1_": {
        "structure": "ApifyActors → ApifyActors → note → note → note → ChatInput → ChatOutput → note → Agent",
        "components": ["ApifyActors","note","ChatInput","ChatOutput","Agent"],
        "connections": [
            {"source": "ApifyActors", "source_output": "tool", "target": "Agent", "target_input": "tools"},
            {"source": "ApifyActors", "source_output": "tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "basic_prompt_chaining": {
        "structure": "Prompt → ChatInput → ChatOutput → Prompt → Prompt → note",
        "components": ["Prompt","ChatInput","ChatOutput","note"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "tool_placeholder"},
            {"source": "Prompt", "source_output": "prompt", "target": "Prompt", "target_input": "tool_placeholder"},
            {"source": "Prompt", "source_output": "prompt", "target": "Prompt", "target_input": "tool_placeholder"},
            {"source": "Prompt", "source_output": "prompt", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "basic_prompting": {
        "structure": "ChatInput → Prompt → note → ChatOutput → LanguageModelComponent",
        "components": ["ChatInput","Prompt","note","ChatOutput","LanguageModelComponent"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "blog_writer": {
        "structure": "Prompt → TextInput → ChatOutput → note → ParserComponent → URLComponent → LanguageModelComponent",
        "components": ["Prompt","TextInput","ChatOutput","note","ParserComponent","URLComponent","LanguageModelComponent"],
        "connections": [
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "instructions"},
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "Prompt", "target_input": "references"},
            {"source": "URLComponent", "source_output": "page_results", "target": "ParserComponent", "target_input": "input_data"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "financial_report_parser": {
        "structure": "ChatOutput → ChatInput → note → note → StructuredOutput → ParserComponent",
        "components": ["ChatOutput","ChatInput","note","StructuredOutput","ParserComponent"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "StructuredOutput", "target_input": "input_value"},
            {"source": "StructuredOutput", "source_output": "dataframe_output", "target": "ParserComponent", "target_input": "input_data"},
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "custom_component_generator": {
        "structure": "Memory → Prompt → note → URL → URL → URL → ChatInput → ChatOutput → LanguageModelComponent",
        "components": ["Memory","Prompt","note","URL","ChatInput","ChatOutput","LanguageModelComponent"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "USER_INPUT"},
            {"source": "Memory", "source_output": "messages_text", "target": "Prompt", "target_input": "CHAT_HISTORY"},
            {"source": "URL", "source_output": "raw_results", "target": "Prompt", "target_input": "EXAMPLE_COMPONENTS"},
            {"source": "URL", "source_output": "raw_results", "target": "Prompt", "target_input": "CUSTOM_COMPONENT_CODE"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "URL", "source_output": "raw_results", "target": "Prompt", "target_input": "BASE_COMPONENT_CODE"},
        ],
    },
    "document_q_a": {
        "structure": "ChatInput → ChatOutput → note → Prompt → LanguageModelComponent → File",
        "components": ["ChatInput","ChatOutput","note","Prompt","LanguageModelComponent","File"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "File", "source_output": "message", "target": "Prompt", "target_input": "Document"},
        ],
    },
    "image_sentiment_analysis": {
        "structure": "ChatInput → ChatOutput → note → Prompt → parser → StructuredOutput → LanguageModelComponent",
        "components": ["ChatInput","ChatOutput","note","Prompt","parser","StructuredOutput","LanguageModelComponent"],
        "connections": [
            {"source": "parser", "source_output": "parsed_text", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "StructuredOutput", "source_output": "structured_output", "target": "parser", "target_input": "input_data"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "StructuredOutput", "target_input": "input_value"},
        ],
    },
    "hybrid_search_rag": {
        "structure": "ChatInput → ParserComponent → ChatOutput → ParserComponent → note → AstraDB → StructuredOutput",
        "components": ["ChatInput","ParserComponent","ChatOutput","note","AstraDB","StructuredOutput"],
        "connections": [
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "ChatInput", "source_output": "message", "target": "AstraDB", "target_input": "search_query"},
            {"source": "ChatInput", "source_output": "message", "target": "StructuredOutput", "target_input": "input_value"},
            {"source": "StructuredOutput", "source_output": "dataframe_output", "target": "ParserComponent", "target_input": "input_data"},
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "AstraDB", "target_input": "lexical_terms"},
            {"source": "AstraDB", "source_output": "dataframe", "target": "ParserComponent", "target_input": "input_data"},
        ],
    },
    "instagram_copywriter": {
        "structure": "ChatInput → Prompt → TextInput → Prompt → ChatOutput → Prompt → note → TavilySearchComponent → Agent → LanguageModelComponent → LanguageModelComponent",
        "components": ["ChatInput","Prompt","TextInput","ChatOutput","note","TavilySearchComponent","Agent","LanguageModelComponent"],
        "connections": [
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "guidelines"},
            {"source": "Prompt", "source_output": "prompt", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "TavilySearchComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "Prompt", "target_input": "post"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "Prompt", "target_input": "post"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "Prompt", "target_input": "image_description"},
            {"source": "Agent", "source_output": "response", "target": "Prompt", "target_input": "context"},
        ],
    },
    "invoice_summarizer": {
        "structure": "note → Prompt → ChatOutput → note → note → needle → ChatInput → Agent",
        "components": ["note","Prompt","ChatOutput","needle","ChatInput","Agent"],
        "connections": [
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "system_prompt"},
            {"source": "needle", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "knowledge_ingestion": {
        "structure": "SplitText → note → URLComponent → KnowledgeIngestion",
        "components": ["SplitText","note","URLComponent","KnowledgeIngestion"],
        "connections": [
            {"source": "URLComponent", "source_output": "page_results", "target": "SplitText", "target_input": "data_inputs"},
            {"source": "SplitText", "source_output": "dataframe", "target": "KnowledgeIngestion", "target_input": "input_df"},
        ],
    },
    "knowledge_retrieval": {
        "structure": "note → TextInput → ChatOutput → KnowledgeRetrieval",
        "components": ["note","TextInput","ChatOutput","KnowledgeRetrieval"],
        "connections": [
            {"source": "KnowledgeRetrieval", "source_output": "retrieve_data", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "TextInput", "source_output": "text", "target": "KnowledgeRetrieval", "target_input": "search_query"},
        ],
    },
    "market_research": {
        "structure": "ChatInput → ChatOutput → note → TavilySearchComponent → Agent → ParserComponent → StructuredOutput",
        "components": ["ChatInput","ChatOutput","note","TavilySearchComponent","Agent","ParserComponent","StructuredOutput"],
        "connections": [
            {"source": "TavilySearchComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "StructuredOutput", "target_input": "input_value"},
            {"source": "StructuredOutput", "source_output": "dataframe_output", "target": "ParserComponent", "target_input": "input_data"},
        ],
    },
    "meeting_summary": {
        "structure": "AssemblyAITranscriptionJobPoller → Prompt → ChatOutput → ChatOutput → ChatOutput → Prompt → Memory → ChatInput → note → note → note → note → AssemblyAITranscriptionJobCreator → note → parser → LanguageModelComponent → LanguageModelComponent",
        "components": ["AssemblyAITranscriptionJobPoller","Prompt","ChatOutput","Memory","ChatInput","note","AssemblyAITranscriptionJobCreator","parser","LanguageModelComponent"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "input"},
            {"source": "AssemblyAITranscriptionJobCreator", "source_output": "transcript_id", "target": "AssemblyAITranscriptionJobPoller", "target_input": "transcript_id"},
            {"source": "AssemblyAITranscriptionJobPoller", "source_output": "transcription_result", "target": "parser", "target_input": "input_data"},
            {"source": "parser", "source_output": "parsed_text", "target": "Prompt", "target_input": "transcript"},
            {"source": "parser", "source_output": "parsed_text", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Memory", "source_output": "messages_text", "target": "Prompt", "target_input": "history"},
        ],
    },
    "memory_chatbot": {
        "structure": "ChatInput → ChatOutput → note → Prompt → Memory → LanguageModelComponent",
        "components": ["ChatInput","ChatOutput","note","Prompt","Memory","LanguageModelComponent"],
        "connections": [
            {"source": "Memory", "source_output": "messages_text", "target": "Prompt", "target_input": "memory"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "news_aggregator": {
        "structure": "note → note → AgentQL → ChatInput → note → ChatOutput → Agent → SaveToFile",
        "components": ["note","AgentQL","ChatInput","ChatOutput","Agent","SaveToFile"],
        "connections": [
            {"source": "AgentQL", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "ChatOutput", "source_output": "message", "target": "SaveToFile", "target_input": "input"},
        ],
    },
    "nvidia_rtx_remix": {
        "structure": "ChatInput → ChatOutput → Agent → Prompt → RemixDocumentation → EmbeddingModel → FAISS → note → MCPTools",
        "components": ["ChatInput","ChatOutput","Agent","Prompt","RemixDocumentation","EmbeddingModel","FAISS","note","MCPTools"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "system_prompt"},
            {"source": "RemixDocumentation", "source_output": "dataframe_output", "target": "FAISS", "target_input": "ingest_data"},
            {"source": "EmbeddingModel", "source_output": "embeddings", "target": "FAISS", "target_input": "embedding"},
            {"source": "FAISS", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "MCPTools", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
        ],
    },
    "pok_dex_agent": {
        "structure": "ChatInput → ChatOutput → note → note → note → APIRequest → Agent",
        "components": ["ChatInput","ChatOutput","note","APIRequest","Agent"],
        "connections": [
            {"source": "APIRequest", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "portfolio_website_code_generator": {
        "structure": "TextInput → ChatOutput → note → note → note → note → note → parser → File → LanguageModelComponent → note → StructuredOutput",
        "components": ["TextInput","ChatOutput","note","parser","File","LanguageModelComponent","StructuredOutput"],
        "connections": [
            {"source": "parser", "source_output": "parsed_text", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "TextInput", "source_output": "text", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "File", "source_output": "message", "target": "StructuredOutput", "target_input": "input_value"},
            {"source": "StructuredOutput", "source_output": "dataframe_output", "target": "parser", "target_input": "input_data"},
        ],
    },
    "price_deal_finder": {
        "structure": "ChatInput → ChatOutput → TavilySearchComponent → AgentQL → note → note → note → note → Agent",
        "components": ["ChatInput","ChatOutput","TavilySearchComponent","AgentQL","note","Agent"],
        "connections": [
            {"source": "AgentQL", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "TavilySearchComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "research_agent": {
        "structure": "Prompt → ChatInput → Prompt → note → Prompt → Prompt → TavilySearchComponent → ChatOutput → LanguageModelComponent → LanguageModelComponent → Agent",
        "components": ["Prompt","ChatInput","note","TavilySearchComponent","ChatOutput","LanguageModelComponent","Agent"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "Prompt", "target_input": "previous_response"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "input_value"},
            {"source": "TavilySearchComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "Agent", "source_output": "response", "target": "Prompt", "target_input": "search_results"},
        ],
    },
    "research_translation_loop": {
        "structure": "ArXivComponent → ChatOutput → ChatInput → note → LanguageModelComponent → LoopComponent → ParserComponent",
        "components": ["ArXivComponent","ChatOutput","ChatInput","note","LanguageModelComponent","LoopComponent","ParserComponent"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "ArXivComponent", "target_input": "search_query"},
            {"source": "LoopComponent", "source_output": "item", "target": "ParserComponent", "target_input": "input_data"},
            {"source": "ParserComponent", "source_output": "parsed_text", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "LoopComponent", "target_input": "input"},
            {"source": "ArXivComponent", "source_output": "dataframe", "target": "LoopComponent", "target_input": "data"},
            {"source": "LoopComponent", "source_output": "done", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "saas_pricing": {
        "structure": "Prompt → ChatOutput → note → CalculatorComponent → Agent",
        "components": ["Prompt","ChatOutput","note","CalculatorComponent","Agent"],
        "connections": [
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "input_value"},
            {"source": "CalculatorComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "search_agent": {
        "structure": "ScrapeGraphSearchApi → ChatInput → ChatOutput → note → note → note → Agent",
        "components": ["ScrapeGraphSearchApi","ChatInput","ChatOutput","note","Agent"],
        "connections": [
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "ScrapeGraphSearchApi", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
        ],
    },
    "seo_keyword_generator": {
        "structure": "Prompt → note → Prompt → ChatOutput → note → LanguageModelComponent",
        "components": ["Prompt","note","ChatOutput","LanguageModelComponent"],
        "connections": [
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
        ],
    },
    "sequential_tasks_agents": {
        "structure": "Agent → Agent → Prompt → Prompt → Prompt → ChatInput → note → Agent → YfinanceComponent → CalculatorComponent → TavilySearchComponent → ChatOutput",
        "components": ["Agent","Prompt","ChatInput","note","YfinanceComponent","CalculatorComponent","TavilySearchComponent","ChatOutput"],
        "connections": [
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "system_prompt"},
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "system_prompt"},
            {"source": "Agent", "source_output": "response", "target": "Prompt", "target_input": "finance_agent_output"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "system_prompt"},
            {"source": "Agent", "source_output": "response", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "Prompt", "target_input": "research_agent_output"},
            {"source": "CalculatorComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "YfinanceComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "TavilySearchComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "simple_agent": {
        "structure": "note → note → CalculatorComponent → ChatInput → ChatOutput → Agent → URLComponent",
        "components": ["note","CalculatorComponent","ChatInput","ChatOutput","Agent","URLComponent"],
        "connections": [
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "CalculatorComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "URLComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
        ],
    },
    "social_media_agent": {
        "structure": "ApifyActors → ApifyActors → note → note → note → ChatInput → ChatOutput → note → Agent",
        "components": ["ApifyActors","note","ChatInput","ChatOutput","Agent"],
        "connections": [
            {"source": "ApifyActors", "source_output": "tool", "target": "Agent", "target_input": "tools"},
            {"source": "ApifyActors", "source_output": "tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "text_sentiment_analysis": {
        "structure": "Prompt → Prompt → Prompt → note → ChatOutput → ChatOutput → note → note → note → LanguageModelComponent → LanguageModelComponent → LanguageModelComponent → File",
        "components": ["Prompt","note","ChatOutput","LanguageModelComponent","File"],
        "connections": [
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "Prompt", "target_input": "summary"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "File", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "File", "source_output": "message", "target": "Prompt", "target_input": "text"},
        ],
    },
    "travel_planning_agents": {
        "structure": "ChatInput → ChatOutput → note → URL → CalculatorComponent → SearchComponent → Agent → Agent → Agent",
        "components": ["ChatInput","ChatOutput","note","URL","CalculatorComponent","SearchComponent","Agent"],
        "connections": [
            {"source": "SearchComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "ChatInput", "source_output": "message", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "URL", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "CalculatorComponent", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
        ],
    },
    "twitter_thread_generator": {
        "structure": "ChatInput → TextInput → ChatOutput → TextInput → TextInput → TextInput → TextInput → TextInput → note → Prompt → LanguageModelComponent",
        "components": ["ChatInput","TextInput","ChatOutput","note","Prompt","LanguageModelComponent"],
        "connections": [
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "CONTENT_GUIDELINES"},
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "OUTPUT_FORMAT"},
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "OUTPUT_LANGUAGE"},
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "PROFILE_DETAILS"},
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "PROFILE_TYPE"},
            {"source": "TextInput", "source_output": "text", "target": "Prompt", "target_input": "TONE_AND_STYLE"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "system_message"},
            {"source": "ChatInput", "source_output": "message", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
        ],
    },
    "vector_store_rag": {
        "structure": "ChatInput → Prompt → SplitText → note → note → ChatOutput → OpenAIEmbeddings → note → OpenAIEmbeddings → note → note → note → parser → File → LanguageModelComponent → AstraDB → AstraDB",
        "components": ["ChatInput","Prompt","SplitText","note","ChatOutput","OpenAIEmbeddings","parser","File","LanguageModelComponent","AstraDB"],
        "connections": [
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "question"},
            {"source": "parser", "source_output": "parsed_text", "target": "Prompt", "target_input": "context"},
            {"source": "File", "source_output": "message", "target": "SplitText", "target_input": "data_inputs"},
            {"source": "Prompt", "source_output": "prompt", "target": "LanguageModelComponent", "target_input": "input_value"},
            {"source": "LanguageModelComponent", "source_output": "text_output", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "SplitText", "source_output": "dataframe", "target": "AstraDB", "target_input": "ingest_data"},
            {"source": "ChatInput", "source_output": "message", "target": "AstraDB", "target_input": "search_query"},
            {"source": "AstraDB", "source_output": "dataframe", "target": "parser", "target_input": "input_data"},
            {"source": "OpenAIEmbeddings", "source_output": "embeddings", "target": "AstraDB", "target_input": "embedding_model"},
            {"source": "OpenAIEmbeddings", "source_output": "embeddings", "target": "AstraDB", "target_input": "embedding_model"},
        ],
    },
    "youtube_analysis": {
        "structure": "YouTubeCommentsComponent → Agent → Prompt → ChatOutput → YouTubeTranscripts → note → parser → ChatInput → BatchRunComponent",
        "components": ["YouTubeCommentsComponent","Agent","Prompt","ChatOutput","YouTubeTranscripts","note","parser","ChatInput","BatchRunComponent"],
        "connections": [
            {"source": "Prompt", "source_output": "prompt", "target": "Agent", "target_input": "input_value"},
            {"source": "Agent", "source_output": "response", "target": "ChatOutput", "target_input": "input_value"},
            {"source": "YouTubeTranscripts", "source_output": "component_as_tool", "target": "Agent", "target_input": "tools"},
            {"source": "parser", "source_output": "parsed_text", "target": "Prompt", "target_input": "analysis"},
            {"source": "ChatInput", "source_output": "message", "target": "YouTubeCommentsComponent", "target_input": "video_url"},
            {"source": "ChatInput", "source_output": "message", "target": "Prompt", "target_input": "url"},
            {"source": "YouTubeCommentsComponent", "source_output": "comments", "target": "BatchRunComponent", "target_input": "df"},
        ],
    },
}


def format_references_for_prompt() -> str:
    """Format reference workflows for inclusion in LLM prompts.
    
    Returns:
        Formatted string with workflow patterns and connection examples.
    """
    lines = ["## REFERENCE WORKFLOWS FROM KNOWLEDGE BASE\n"]
    lines.append("These are verified working workflow patterns:\n")
    
    for name, workflow in LEARNED_WORKFLOWS.items():
        lines.append(f"\n### {name.replace('_', ' ').title()}")
        lines.append(f"Structure: {workflow['structure']}")
        lines.append("Connections:")
        for conn in workflow.get("connections", []):
            source = conn.get("source", "")
            source_output = conn.get("source_output", "")
            target = conn.get("target", "")
            target_input = conn.get("target_input", "")
            lines.append(f"  - {source}.{source_output} → {target}.{target_input}")
    
    return "\n".join(lines)


def get_workflow_by_pattern(pattern_keywords: list[str]) -> dict | None:
    """Find a reference workflow matching the given keywords.
    
    Args:
        pattern_keywords: List of keywords to match (e.g., ["memory", "chat"])
        
    Returns:
        Matching workflow dict or None
    """
    pattern_keywords = [kw.lower() for kw in pattern_keywords]
    
    for name, workflow in LEARNED_WORKFLOWS.items():
        name_lower = name.lower()
        components_lower = [c.lower() for c in workflow.get("components", [])]
        
        # Check if keywords match workflow name or components
        matches = sum(1 for kw in pattern_keywords 
                     if kw in name_lower or any(kw in c for c in components_lower))
        
        if matches >= len(pattern_keywords) // 2 + 1:
            return {"name": name, **workflow}
    
    return None


def get_connection_pattern(source_type: str, target_type: str) -> list[dict]:
    """Get verified connection patterns between two component types.
    
    Args:
        source_type: Source component type (e.g., "ChatInput")
        target_type: Target component type (e.g., "Agent")
        
    Returns:
        List of connection dicts that match
    """
    patterns = []
    source_lower = source_type.lower()
    target_lower = target_type.lower()
    
    for workflow in LEARNED_WORKFLOWS.values():
        for conn in workflow.get("connections", []):
            if (source_lower in conn.get("source", "").lower() and 
                target_lower in conn.get("target", "").lower()):
                patterns.append(conn)
    
    return patterns
