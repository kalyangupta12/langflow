"""Zord AI Service - Claude-powered workflow architect."""

from __future__ import annotations

import copy
import json
import os
from typing import Any

from anthropic import AsyncAnthropic
from lfx.log.logger import logger

from langflow.services.zord.chroma_component_indexer import get_chroma_indexer
from langflow.services.zord.prompts import (
    ANALYZE_INTENT_PROMPT,
    GENERATE_JSON_PROMPT,
    GENERATE_PLAN_PROMPT,
    MODIFY_PLAN_PROMPT,
    SYSTEM_PROMPT,
)
from langflow.services.zord.reference_workflows import format_references_for_prompt
from langflow.services.zord.registry import get_component_registry, initialize_registry


class ZordAIService:
    """Service for Zord AI workflow design using Claude."""

    def __init__(self, settings_service: Any = None, telemetry_service: Any = None):
        """Initialize Zord AI Service with Claude client and component registry.
        
        Args:
            settings_service: Langflow settings service for component loading
            telemetry_service: Optional telemetry service
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            error_msg = (
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please add it to your .env file and restart the backend server. "
                "Get your API key from: https://console.anthropic.com/"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 8192  # Increased for better user intent fulfillment
        self.settings_service = settings_service
        self.telemetry_service = telemetry_service
        
        # Initialize ChromaDB semantic indexer
        try:
            self.indexer = get_chroma_indexer()
            stats = self.indexer.get_stats()
            logger.info(f"Zord AI initialized with ChromaDB indexer: {stats}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB indexer: {e}")
            logger.error("Please run initialize_chroma.py to set up the collection")
            raise
        
        # Get component registry instance (will be loaded on first use)
        self.registry = get_component_registry()
        logger.info("Zord AI ready - will use modern components only (legacy components excluded)")
        
        # Cache for component metadata (populated on first use)
        self._model_types_cache: set[str] | None = None
        self._search_types_cache: set[str] | None = None
        self._component_outputs_cache: dict[str, tuple[str, str]] | None = None

    def _clear_component_caches(self) -> None:
        """Clear component metadata caches to force refresh from registry."""
        self._model_types_cache = None
        self._search_types_cache = None
        self._component_outputs_cache = None
        logger.info("Cleared component metadata caches")

    def _get_model_types(self) -> set[str]:
        """Get all model component types from registry.
        
        Returns:
            Set of component type names that are language models
        """
        if self._model_types_cache is not None:
            return self._model_types_cache
        
        # If registry not loaded, return fallback known model types
        if not self.registry._loaded:
            logger.warning("Registry not loaded, using fallback model types")
            return {"OpenAIModel", "AnthropicModel", "GoogleGenerativeAIModel", 
                   "OllamaModel", "GroqModel", "MistralModel", "AzureOpenAIModel",
                   "HuggingFaceModel", "AmazonBedrockModel", "CohereModel", "LanguageModel"}
        
        model_types = set()
        all_components = self.registry.get_all_components()
        
        for category, components in all_components.items():
            for comp_name, comp_data in components.items():
                # Skip legacy components
                if comp_data.get("legacy", False):
                    continue
                
                # Check if it's a model by:
                # 1. Category contains 'model' 
                # 2. Base classes include LanguageModel
                # 3. Component name contains 'Model'
                base_classes = comp_data.get("base_classes", [])
                is_model = (
                    "model" in category.lower() or
                    "LanguageModel" in base_classes or
                    "Model" in comp_name
                )
                
                if is_model and "Message" in base_classes:
                    model_types.add(comp_name)
        
        self._model_types_cache = model_types
        logger.info(f"Discovered {len(model_types)} model types from registry: {sorted(model_types)[:10]}...")
        return model_types

    def _get_search_types(self) -> set[str]:
        """Get all search/retrieval component types from registry.
        
        Returns:
            Set of component type names that are search/retrieval components
        """
        if self._search_types_cache is not None:
            return self._search_types_cache
        
        # If registry not loaded, return fallback known search types
        if not self.registry._loaded:
            logger.warning("Registry not loaded, using fallback search types")
            return {"UnifiedWebSearch", "WebSearch", "DuckDuckGoSearchComponent", 
                   "DuckDuckGoSearch", "GoogleSearchAPIWrapper", "BingSearch",
                   "SerpAPIWrapper", "TavilySearch", "TavilySearchResults",
                   "WikipediaSearch", "ArxivSearch", "BraveSearch",
                   # Vector stores also provide search results
                   "AstraDB", "Chroma", "Pinecone", "Weaviate", "FAISS", "Milvus",
                   "Qdrant", "PGVector", "SupabaseVectorStore", "MongoDBAtlasVectorSearch",
                   "KnowledgeRetrieval"}
        
        search_types = set()
        all_components = self.registry.get_all_components()
        
        # Keywords that indicate a search/retrieval component (including vector stores)
        search_keywords = ["search", "retrieval", "web", "duckduckgo", "google", "bing", 
                          "serp", "tavily", "brave", "wikipedia", "arxiv",
                          # Vector store keywords
                          "vector", "astra", "chroma", "pinecone", "weaviate", "faiss",
                          "milvus", "qdrant", "pgvector", "supabase", "mongodb", "atlas"]
        
        for category, components in all_components.items():
            for comp_name, comp_data in components.items():
                # Skip legacy components
                if comp_data.get("legacy", False):
                    continue
                
                # Check if it's a search/vector component by name or description
                comp_name_lower = comp_name.lower()
                description = comp_data.get("description", "").lower()
                
                is_search = any(kw in comp_name_lower or kw in description for kw in search_keywords)
                
                # Also check category for vectorstores
                is_vectorstore = "vector" in category.lower()
                
                # Check if outputs DataFrame or Data (typical for search results)
                base_classes = comp_data.get("base_classes", [])
                outputs_data = "DataFrame" in base_classes or "Data" in base_classes
                
                if (is_search or is_vectorstore) and outputs_data:
                    search_types.add(comp_name)
        
        self._search_types_cache = search_types
        logger.info(f"Discovered {len(search_types)} search/vector types from registry: {sorted(search_types)}")
        return search_types

    def _get_component_output_info(self, component_type: str) -> tuple[str, str] | None:
        """Get the primary output name and type for a component.
        
        Args:
            component_type: Component type name
            
        Returns:
            Tuple of (output_name, output_type) or None if not found
        """
        comp_data = self.registry.get_component_by_type(component_type)
        if not comp_data:
            return None
        
        outputs = comp_data.get("outputs", [])
        if outputs:
            first_output = outputs[0]
            output_name = first_output.get("name", "output")
            output_types = first_output.get("types", ["Data"])
            return (output_name, output_types[0] if output_types else "Data")
        
        return None

    def _get_component_primary_input(self, component_type: str) -> str | None:
        """Get the primary input field name for a component.
        
        Args:
            component_type: Component type name
            
        Returns:
            Primary input field name or None
        """
        comp_data = self.registry.get_component_by_type(component_type)
        if not comp_data:
            return None
        
        template = comp_data.get("template", {})
        
        # Priority order for finding primary input
        priority_fields = ["input_value", "input", "query", "search_query", "message", "text", "data"]
        
        for field in priority_fields:
            if field in template:
                return field
        
        # Fallback: find first required field that accepts Message
        for field_name, field_data in template.items():
            if field_name.startswith("_") or field_name == "code":
                continue
            if isinstance(field_data, dict):
                input_types = field_data.get("input_types", [])
                if "Message" in input_types and field_data.get("required", False):
                    return field_name
        
        return None

    def _build_dynamic_component_connections(self) -> dict[str, tuple[str, str]]:
        """Build component connection mappings from registry.
        
        Returns:
            Dict mapping component_type to (output_name, target_variable)
            for components that should auto-connect to Prompt Template
        """
        if self._component_outputs_cache is not None:
            return self._component_outputs_cache
        
        # If registry not loaded yet, return hardcoded fallback
        if not self.registry._loaded:
            logger.warning("Registry not loaded, using fallback component connections")
            return {
                # Web search components
                "UnifiedWebSearch": ("results", "context"),
                "WebSearch": ("results", "context"),
                "DuckDuckGoSearchComponent": ("dataframe", "context"),
                "DuckDuckGoSearch": ("dataframe", "context"),
                "TavilySearch": ("results", "context"),
                "GoogleSearchAPIWrapper": ("results", "context"),
                # Vector store components (with common name variations)
                "AstraDB": ("search_results", "context"),
                "Astra DB": ("search_results", "context"),  # Display name variation
                "AstraDBVectorStoreComponent": ("search_results", "context"),
                "Chroma": ("search_results", "context"),
                "Pinecone": ("search_results", "context"),
                "Weaviate": ("search_results", "context"),
                "FAISS": ("search_results", "context"),
                "Milvus": ("search_results", "context"),
                "Qdrant": ("search_results", "context"),
                "PGVector": ("search_results", "context"),
                # Knowledge retrieval
                "KnowledgeRetrieval": ("results", "context"),
                # Memory
                "Memory": ("messages_text", "history"),
            }
        
        connections = {}
        search_types = self._get_search_types()
        
        for comp_type in search_types:
            output_info = self._get_component_output_info(comp_type)
            if output_info:
                output_name, output_type = output_info
                # Search components connect to 'context' variable
                connections[comp_type] = (output_name, "context")
        
        # Add Memory component (special case - always goes to 'history')
        memory_output = self._get_component_output_info("Memory")
        if memory_output:
            connections["Memory"] = (memory_output[0], "history")
        else:
            # Fallback if Memory component not found in registry
            connections["Memory"] = ("messages_text", "history")
        
        # Add KnowledgeRetrieval if not already detected
        kr_output = self._get_component_output_info("KnowledgeRetrieval")
        if kr_output and "KnowledgeRetrieval" not in connections:
            connections["KnowledgeRetrieval"] = (kr_output[0], "context")
        
        self._component_outputs_cache = connections
        logger.info(f"Built dynamic component connections: {list(connections.keys())}")
        return connections

    async def _call_claude(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> str:
        """Call Claude API with conversation context.

        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages

        Returns:
            Claude's response text
        """
        messages = []
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message,
        })

        try:
            # Ensure registry is loaded
            if not self.registry._loaded:
                await self.registry.load_components(
                    settings_service=self.settings_service,
                    telemetry_service=self.telemetry_service
                )
                # Clear caches after registry loads to use fresh data
                self._clear_component_caches()
            
            # Build system prompt with real available components from registry
            # Use compact format to minimize tokens
            component_info = self.registry.format_for_llm(include_templates=False, compact=True)
            
            # Log stats about components
            stats = self.registry.get_stats()
            logger.info(f"Registry stats: {stats['modern_components']} modern, {stats['legacy_components']} legacy (excluded)")
            
            # Log token estimate
            approx_tokens = len(component_info) // 4  # Rough estimate: 1 token ≈ 4 chars
            logger.info(f"Component info size: {len(component_info)} chars (~{approx_tokens} tokens)")
            
            # Enhance system prompt with actual component data from Langflow
            enhanced_system_prompt = SYSTEM_PROMPT + "\n\n" + component_info
            
            # Log total prompt size
            total_size = len(enhanced_system_prompt) + len(user_message)
            logger.info(f"Total prompt size: {total_size} chars (~{total_size // 4} tokens)")
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=enhanced_system_prompt,
                messages=messages,
            )
            
            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from Claude's response.

        Args:
            response: Claude's response text

        Returns:
            Extracted JSON object
        """
        logger.info(f"Extracting JSON from response (length: {len(response)})")
        
        # Try to find JSON in markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            logger.info("Found JSON in markdown code block")
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
            logger.info("Found JSON in generic code block")
        else:
            # Try to parse the entire response
            json_str = response.strip()
            logger.info("Trying to parse entire response as JSON")

        try:
            parsed = json.loads(json_str)
            logger.info(f"Successfully parsed JSON with keys: {list(parsed.keys())}")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"JSON string (first 500 chars): {json_str[:500]}")
            logger.error(f"Full response (first 1000 chars): {response[:1000]}")
            raise ValueError("Failed to extract valid JSON from response") from e

    async def analyze_intent(
        self,
        prompt: str,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Analyze user intent and generate clarifying MCQs.

        Args:
            prompt: User's workflow description
            conversation_history: Previous conversation

        Returns:
            Dict with 'mcqs' and 'message' keys
        """
        user_message = ANALYZE_INTENT_PROMPT.format(user_prompt=prompt)
        
        response = await self._call_claude(
            user_message=user_message,
            conversation_history=conversation_history,
        )
        
        # Extract JSON from response
        data = self._extract_json_from_response(response)
        
        return {
            "mcqs": data.get("mcqs", []),
            "message": data.get("message", "Here are some questions to clarify your workflow:"),
        }

    async def generate_plan(
        self,
        prompt: str,
        answers: dict[str, str],
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Generate a workflow plan based on user answers.

        Args:
            prompt: Original user prompt
            answers: MCQ answers (question_id -> answer)
            conversation_history: Previous conversation

        Returns:
            Dict with 'plan' and 'message' keys
        """
        answers_text = "\n".join([f"- {k}: {v}" for k, v in answers.items()])
        user_message = GENERATE_PLAN_PROMPT.format(
            user_prompt=prompt,
            answers=answers_text,
        )
        
        response = await self._call_claude(
            user_message=user_message,
            conversation_history=conversation_history,
        )
        
        # Extract JSON from response
        data = self._extract_json_from_response(response)
        
        return {
            "plan": data.get("plan", {}),
            "message": data.get("message", "Here's your workflow plan:"),
        }

    async def _enhance_plan_with_semantic_components(self, plan_dict: dict) -> dict:
        """Enhance workflow plan with semantically relevant components.
        
        Args:
            plan_dict: Original workflow plan
        
        Returns:
            Enhanced plan with better component suggestions
        """
        try:
            indexer = self.indexer
            
            # Extract keywords from plan description and title
            plan_text = f"{plan_dict.get('title', '')} {plan_dict.get('description', '')}"
            for step in plan_dict.get('steps', []):
                if isinstance(step, dict):
                    step_text = f"{step.get('title', '')} {step.get('description', '')}"
                    plan_text += " " + step_text
            
            # Use semantic search to find relevant components
            relevant_components = await indexer.search_components(plan_text, limit=20)
            
            # Add component suggestions to plan context
            plan_dict['suggested_components'] = relevant_components
            logger.info(f"Enhanced plan with {len(relevant_components)} semantically relevant components")
            
            return plan_dict
            
        except Exception as e:
            logger.warning(f"Failed to enhance plan with semantic components: {e}")
            return plan_dict

    async def generate_json(
        self,
        plan: dict | Any,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Generate Langflow JSON from workflow plan using Langflow's component API.

        Args:
            plan: Workflow plan object (dict or Pydantic model)
            conversation_history: Previous conversation

        Returns:
            Dict with 'json' and 'message' keys
        """
        # Convert plan to dict if it's a Pydantic model
        if hasattr(plan, 'model_dump'):
            plan_dict = plan.model_dump()
        elif hasattr(plan, 'dict'):
            plan_dict = plan.dict()
        else:
            plan_dict = plan
        
        try:
            # Extract workflow requirements
            plan_title = plan_dict.get("title", "")
            plan_description = plan_dict.get("description", "")
            
            # Extract components from steps (new plan format)
            steps = plan_dict.get("steps", [])
            components_list = []
            for step in steps:
                if isinstance(step, dict):
                    components_list.append({
                        "name": step.get("component", step.get("name", "")),
                        "type": step.get("component", step.get("type", "")),
                        "description": step.get("description", "")
                    })
            
            logger.info(f"Plan received - Title: '{plan_title}', Components count: {len(components_list)}")
            logger.info(f"Full plan_dict keys: {list(plan_dict.keys())}")
            if components_list:
                logger.info(f"First component: {components_list[0]}")
            
            # Fetch ALL available component templates from Langflow's component system
            logger.info("Fetching component templates from Langflow API")
            all_component_categories = await self._fetch_component_templates()
            
            # Flatten component dict: {category: {name: template}} -> {name: template}
            # Filter out legacy and deprecated components
            component_templates = {}
            legacy_count = 0
            for category, components in all_component_categories.items():
                if isinstance(components, dict):
                    for comp_name, comp_template in components.items():
                        # Skip legacy components
                        if comp_template.get("legacy", False):
                            legacy_count += 1
                            logger.debug(f"Skipping legacy component: {comp_name}")
                            continue
                        # Skip deprecated components
                        if comp_template.get("deprecated", False):
                            legacy_count += 1
                            logger.debug(f"Skipping deprecated component: {comp_name}")
                            continue
                        component_templates[comp_name] = comp_template
            
            logger.info(f"Loaded {len(component_templates)} modern components (excluded {legacy_count} legacy/deprecated) from {len(all_component_categories)} categories")

            # 1) Try LLM-generated simplified workflow structure first
            try:
                available_components = self.registry.format_for_llm(include_templates=False, compact=True)
                user_message = GENERATE_JSON_PROMPT.format(
                    plan=json.dumps(plan_dict, indent=2),
                    available_components=available_components,
                )
                # Add reference workflow patterns to guide connections
                user_message = f"{user_message}\n\n{format_references_for_prompt()}"

                response = await self._call_claude(
                    user_message=user_message,
                    conversation_history=conversation_history,
                )

                simplified_data = self._extract_json_from_response(response)
                simplified_workflow = simplified_data.get("workflow", {})

                if simplified_workflow and simplified_workflow.get("nodes"):
                    workflow = self._build_workflow_from_simplified(
                        simplified=simplified_workflow,
                        component_templates=component_templates,
                    )
                    return {
                        "json": workflow,
                        "message": simplified_data.get(
                            "message",
                            f"Successfully generated workflow with {len(workflow.get('data', {}).get('nodes', []))} components.",
                        ),
                    }
            except Exception as e:
                logger.warning(f"LLM simplified workflow generation failed, falling back to plan-based builder: {e}")
            
            # If no components in plan, fallback to basic workflow
            if not components_list or len(components_list) == 0:
                logger.info("No components in plan, generating basic chat workflow")
                workflow = await self._generate_basic_workflow(plan_title, plan_description, component_templates)
                return {
                    "json": workflow,
                    "message": "I've created a basic chat workflow! You can customize it by adding more components.",
                }
            
            # 2) Fallback: Build nodes from plan components  
            nodes = []
            node_id_map = {}
            
            for idx, comp in enumerate(components_list):
                comp_name = comp.get("name", f"Component_{idx}")
                comp_type = comp.get("type", "")
                
                # Try to find matching template by type or name
                template = None
                matched_name = None
                
                if comp_type and comp_type in component_templates:
                    template = component_templates[comp_type]
                    matched_name = comp_type
                elif comp_name in component_templates:
                    template = component_templates[comp_name]
                    matched_name = comp_name
                
                # If no exact match, try fuzzy matching by description
                if not template:
                    search_query = f"{comp_name} {comp.get('description', '')}".lower()
                    best_match = None
                    best_match_name = None
                    
                    for name, tmpl in component_templates.items():
                        if not isinstance(tmpl, dict):
                            continue
                        
                        # Skip legacy/deprecated components - they're already filtered out
                        # but double-check to be safe
                        if tmpl.get("legacy", False) or tmpl.get("deprecated", False):
                            continue
                        
                        tmpl_desc = tmpl.get("description", "").lower()
                        tmpl_display = tmpl.get("display_name", "").lower()
                        
                        if (search_query in tmpl_desc or 
                            name.lower() in search_query or 
                            search_query in tmpl_display or
                            comp_name.lower() in name.lower()):
                            # Found a match with modern component
                            best_match = tmpl
                            best_match_name = name
                    
                    if best_match:
                        template = best_match
                        matched_name = best_match_name
                        logger.info(f"Fuzzy matched '{comp_name}' to '{matched_name}'")
                
                if not template:
                    logger.warning(f"No modern template found for component: {comp_name} (type: {comp_type}). Component may be legacy or invalid.")
                    continue
                
                # Final check: ensure matched component is not legacy
                if template.get("legacy", False) or template.get("deprecated", False):
                    logger.warning(f"Rejecting legacy/deprecated component: {matched_name}. Looking for modern alternative.")
                    continue
                
                
                # Generate unique node ID with component type
                import uuid
                node_id = f"{matched_name}-{str(uuid.uuid4())[:5]}"
                # Allow duplicates; only store the first mapping for name-based connections
                key_name = comp_name or matched_name
                if key_name and key_name not in node_id_map:
                    node_id_map[key_name] = node_id
                
                # Build node with Langflow's expected structure
                # Match the Blog Writer format exactly
                node = {
                    "id": node_id,
                    "type": "genericNode",
                    "position": {"x": 150 + (len(nodes) * 400), "y": 250},  # Horizontal layout
                    "data": {
                        "type": matched_name,  # Component type name
                        "node": template,  # Full component template from Langflow
                        "id": node_id,
                        "display_name": template.get("display_name", matched_name),
                        "description": template.get("description", "")
                    },
                    "selected": False,
                    "dragging": False
                }

                # Set selected_output for components with multiple outputs (or default to first)
                outputs = template.get("outputs", [])
                if outputs and isinstance(outputs, list):
                    selected_output = outputs[0].get("name")
                    if selected_output:
                        node["data"]["selected_output"] = selected_output
                
                # Add measured dimensions if template has them
                if "metadata" in template:
                    node["measured"] = {"width": 320, "height": 300}
                
                nodes.append(node)
                logger.info(f"Added node {len(nodes)}: {matched_name} (id: {node_id}, legacy: {template.get('legacy', False)})")
            
            # Build edges - automatically connect nodes in sequence
            edges = []
            
            # Try to use connections from plan first
            connections = plan_dict.get("connections", [])
            if connections and len(connections) > 0:
                logger.info(f"Using {len(connections)} connections from plan")
                for conn in connections:
                    source_name = conn.get("from", "")
                    target_name = conn.get("to", "")
                    
                    if source_name in node_id_map and target_name in node_id_map:
                        source_id = node_id_map[source_name]
                        target_id = node_id_map[target_name]
                        
                        # Find source and target nodes to get their types
                        source_node = next((n for n in nodes if n["id"] == source_id), None)
                        target_node = next((n for n in nodes if n["id"] == target_id), None)
                        
                        if source_node and target_node:
                            edge = self._create_edge(source_node, target_node)
                            if edge:
                                edges.append(edge)
                                logger.info(f"Connected (from plan): {source_node['data']['type']} → {target_node['data']['type']}")
                            else:
                                logger.warning(f"Failed to create edge from plan: {source_name} → {target_name}")
            
            # Always ensure ALL nodes are connected in sequence (plan might be incomplete)
            if len(edges) < len(nodes) - 1:
                logger.info(f"Auto-connecting {len(nodes)} nodes in sequence (plan had {len(edges)} edges)")
                
                # Start fresh to ensure complete chain
                edges.clear()
                successful_connections = 0
                
                for i in range(len(nodes) - 1):
                    source_node = nodes[i]
                    target_node = nodes[i + 1]
                    edge = self._create_edge(source_node, target_node)
                    if edge:
                        edges.append(edge)
                        successful_connections += 1
                        logger.info(f"✓ Auto-connected: {source_node['data']['type']} → {target_node['data']['type']}")
                    else:
                        logger.error(
                            f"✗ Failed to connect: {source_node['data']['type']} → {target_node['data']['type']}. "
                            f"This will break the workflow chain!"
                        )
                
                logger.info(f"Created {successful_connections}/{len(nodes)-1} sequential connections")
            
            # Build complete workflow JSON
            workflow = {
                "data": {
                    "nodes": nodes,
                    "edges": edges,
                    "viewport": {"x": 0, "y": 0, "zoom": 1}
                },
                "name": plan_title,
                "description": plan_description
            }
            
            # Validate workflow completeness
            expected_edges = len(nodes) - 1
            if len(edges) < expected_edges:
                logger.warning(
                    f"⚠ Workflow incomplete: {len(edges)}/{expected_edges} edges created. "
                    f"Some components may not be connected!"
                )
            
            logger.info(f"✓ Built workflow: {len(nodes)} nodes, {len(edges)}/{expected_edges} edges")
            return {
                "json": workflow,
                "message": f"Successfully generated workflow with {len(nodes)} components and {len(edges)} connections."
            }
            
        except Exception as e:
            logger.error(f"Error in workflow generation: {e}", exc_info=True)
            
            return {
                "json": {"error": str(e)},
                "message": f"Failed to generate workflow: {str(e)}. Please check the logs for details.",
            }

    # Common field name corrections - LLM often generates wrong names
    FIELD_NAME_CORRECTIONS = {
        # Embeddings field corrections (most common mistake)
        "embedding_model": "embedding",
        "embeddings": "embedding",
        "embedding_input": "embedding",
        # VectorStore field corrections
        "ingest": "ingest_data",
        "data": "ingest_data",  # When targeting vector stores
        "search": "search_query",
        "query": "search_query",
        # Text splitter corrections
        "data_input": "data_inputs",
        "input": "data_inputs",
        "text": "data_inputs",
        # Model field corrections
        "message": "input_value",  # When targeting models
        "prompt": "input_value",
        # Output field corrections
        "response": "text_output",
        "output": "text_output",
        "result": "text_output",
    }
    
    # Component-specific field mappings (target_type -> {wrong_name: correct_name})
    COMPONENT_FIELD_CORRECTIONS = {
        "Chroma": {
            "embedding_model": "embedding",
            "embeddings": "embedding",
            "data": "ingest_data",
            "search": "search_query",
            "query": "search_query",
        },
        "Pinecone": {
            "embedding_model": "embedding",
            "embeddings": "embedding",
        },
        "Weaviate": {
            "embedding_model": "embedding",
            "embeddings": "embedding",
        },
        "FAISS": {
            "embedding_model": "embedding",
            "embeddings": "embedding",
        },
        "RecursiveCharacterTextSplitter": {
            "data_input": "data_inputs",
            "text": "data_inputs",
            "input": "data_inputs",
        },
        "SplitText": {
            "data_input": "data_inputs",
            "text": "data_inputs",
            "input": "data_inputs",
        },
        "OpenAIModel": {
            "message": "input_value",
            "prompt": "input_value",
        },
        "AnthropicModel": {
            "message": "input_value",
            "prompt": "input_value",
        },
        "ChatOutput": {
            "message": "input_value",
            "text": "input_value",
            "response": "input_value",
        },
        # Prompt Template - LLM may try to connect to variable names like context, history, question
        # These are dynamic fields created by the template, so we allow them through
        "Prompt Template": {
            # Don't correct these - they're intentional variable names
        },
        # Composio components - redirect from OAuth fields to proper data inputs
        "ComposioGmailAPIComponent": {
            "authorization_url": "input_data",
            "auth_url": "input_data",
        },
        "ComposioGoogleSheetsAPIComponent": {
            "authorization_url": "input_data",
            "auth_url": "input_data",
        },
        "ComposioSlackAPIComponent": {
            "authorization_url": "input_data",
            "auth_url": "input_data",
        },
        # Gmail component
        "Gmail": {
            "authorization_url": "input_data",
        },
        # GoogleSheets component
        "GoogleSheets": {
            "authorization_url": "input_data",
        },
        # Google Generative AI
        "GoogleGenerativeAIModel": {
            "message": "input_value",
            "prompt": "input_value",
        },
    }
    
    # Dynamic field types that accept Message connections (for Prompt Template variables)
    # These are common variable names used in prompt templates that become input fields
    PROMPT_VARIABLE_NAMES = [
        "context", "history", "question", "query", "input", "user_input", 
        "text", "data", "item", "content", "message", "user_message"
    ]
    
    # Fields that should NEVER be used as connection targets
    # Includes OAuth fields, config fields, and internal fields
    FORBIDDEN_TARGET_FIELDS = [
        # Prompt Template internal fields
        "tool_placeholder", "template", "use_double_brackets", "code",
        # OAuth/Authorization fields (Composio, APIs)
        "authorization_url", "auth_url", "redirect_uri", "callback_url",
        "api_key", "composio_api_key", "google_api_key", "openai_api_key",
        "access_token", "refresh_token", "client_id", "client_secret",
        # Config/settings fields
        "auth_mode", "connection_id", "entity_id", "action_button",
        "model", "model_name", "temperature", "max_tokens",
    ]
    
    def _correct_field_name(self, target_type: str, field_name: str) -> str:
        """Correct common LLM field name mistakes.
        
        Args:
            target_type: Target component type
            field_name: Field name from LLM
            
        Returns:
            Corrected field name
        """
        # CRITICAL: Reject forbidden fields and redirect to proper variable names
        if field_name in self.FORBIDDEN_TARGET_FIELDS:
            if target_type == "Prompt Template":
                # Redirect to a common variable name
                logger.warning(f"Forbidden field {field_name} for Prompt Template, redirecting to 'data'")
                return "data"
            else:
                logger.warning(f"Attempted to use forbidden field: {field_name}")
        
        # For Prompt Template, allow dynamic variable field names through
        if target_type == "Prompt Template" and field_name in self.PROMPT_VARIABLE_NAMES:
            logger.info(f"Allowing Prompt Template variable field: {field_name}")
            return field_name
        
        # First check component-specific corrections
        if target_type in self.COMPONENT_FIELD_CORRECTIONS:
            comp_corrections = self.COMPONENT_FIELD_CORRECTIONS[target_type]
            if field_name in comp_corrections:
                corrected = comp_corrections[field_name]
                logger.info(f"Corrected field name: {target_type}.{field_name} → {corrected}")
                return corrected
        
        # Then check generic corrections
        if field_name in self.FIELD_NAME_CORRECTIONS:
            corrected = self.FIELD_NAME_CORRECTIONS[field_name]
            logger.info(f"Corrected field name (generic): {field_name} → {corrected}")
            return corrected
        
        return field_name

    def _build_workflow_from_simplified(self, simplified: dict, component_templates: dict) -> dict:
        """Build full Langflow workflow from simplified structure using real templates.

        Args:
            simplified: Simplified workflow structure from LLM
            component_templates: Mapping of component type to template dict

        Returns:
            Complete Langflow workflow with full templates and edges
        """
        import uuid

        name = simplified.get("name", "Zord Generated Workflow")
        description = simplified.get("description", "Generated by Zord AI")
        nodes_simple = simplified.get("nodes", [])
        connections = simplified.get("connections", [])

        # Check what components the workflow has (using registry-based detection)
        has_prompt_template = any(n.get("type") == "Prompt Template" for n in nodes_simple)
        has_chat_input = any(n.get("type") == "ChatInput" for n in nodes_simple)
        
        # Use dynamic detection from registry
        search_types = self._get_search_types()
        has_web_search = any(n.get("type") in search_types for n in nodes_simple)
        has_knowledge_retrieval = any(n.get("type") == "KnowledgeRetrieval" for n in nodes_simple)
        has_memory = any(n.get("type") == "Memory" for n in nodes_simple)

        # Analyze connections to find what variables Prompt Template needs
        prompt_template_vars = set()
        for conn in connections:
            target_input = conn.get("target_input")
            # Skip forbidden fields - they will be corrected later
            if target_input in self.FORBIDDEN_TARGET_FIELDS:
                continue
            if target_input in self.PROMPT_VARIABLE_NAMES:
                # Look for the target node to see if it's a Prompt Template
                target_id = conn.get("target")
                for node_s in nodes_simple:
                    if node_s.get("id") == target_id and node_s.get("type") == "Prompt Template":
                        prompt_template_vars.add(target_input)
                        break

        # Auto-add required variables based on workflow components
        if has_prompt_template:
            # Always add question variable when ChatInput exists
            if has_chat_input and "question" not in prompt_template_vars:
                prompt_template_vars.add("question")
                logger.info("Auto-added 'question' variable for ChatInput → Prompt Template connection")
            
            # Add context variable when search/retrieval components exist
            if (has_web_search or has_knowledge_retrieval) and "context" not in prompt_template_vars:
                prompt_template_vars.add("context")
                logger.info("Auto-added 'context' variable for Search/Retrieval → Prompt Template connection")
            
            # Add history variable when Memory component exists
            if has_memory and "history" not in prompt_template_vars:
                prompt_template_vars.add("history")
                logger.info("Auto-added 'history' variable for Memory → Prompt Template connection")

        nodes: list[dict] = []
        node_map: dict[str, dict] = {}

        for node_simple in nodes_simple:
            comp_type = node_simple.get("type")
            if not comp_type:
                continue

            node_id = node_simple.get("id") or f"{comp_type}-{str(uuid.uuid4())[:8]}"
            position = node_simple.get("position", {"x": 100 + (len(nodes) * 400), "y": 100})

            orig_template = component_templates.get(comp_type)
            if not orig_template:
                logger.warning(f"Template not found for component type: {comp_type}")
                continue

            # Deep copy template to avoid modifying original
            template = copy.deepcopy(orig_template)

            # For Prompt Template, set up dynamic variable fields based on connections
            if comp_type == "Prompt Template" and prompt_template_vars:
                template_dict = template.get("template", {})
                # Build template text with variables and proper labels
                var_lines = []
                for var_name in prompt_template_vars:
                    # Create labeled variable line
                    label = var_name.replace("_", " ").title()
                    var_lines.append(f"{label}: {{{var_name}}}")
                    # Add the variable as an input field if not already present
                    if var_name not in template_dict:
                        template_dict[var_name] = {
                            "type": "str",
                            "required": True,
                            "placeholder": "",
                            "list": False,
                            "show": True,
                            "multiline": True,
                            "value": "",
                            "fileTypes": [],
                            "file_path": "",
                            "password": False,
                            "name": var_name,
                            "display_name": label,
                            "advanced": False,
                            "input_types": ["Message"],
                            "dynamic": False,
                            "info": f"Variable {{{var_name}}} to be inserted into the template.",
                            "load_from_db": False,
                            "_input_type": "MultilineInput",
                        }
                # Set the template text field with system prompt + variables
                if "template" in template_dict:
                    existing_text = template_dict["template"].get("value", "")
                    if not existing_text or existing_text == "":
                        # Build a proper system prompt with variables
                        system_prompt = "You are a helpful AI assistant. Please respond to the user's request thoughtfully and accurately.\n\n"
                        template_dict["template"]["value"] = system_prompt + "\n".join(var_lines) + "\n\nPlease provide a helpful response."
                template["template"] = template_dict
                logger.info(f"Set up Prompt Template with dynamic variables: {prompt_template_vars}")

            node = {
                "id": node_id,
                "type": "genericNode",
                "position": position,
                "data": {
                    "type": comp_type,
                    "node": template,
                    "id": node_id,
                    "display_name": template.get("display_name", comp_type),
                    "description": template.get("description", ""),
                },
                "selected": False,
                "dragging": False,
            }

            # Set selected_output for components with outputs
            outputs = template.get("outputs", [])
            if outputs and isinstance(outputs, list):
                selected_output = outputs[0].get("name")
                if selected_output:
                    node["data"]["selected_output"] = selected_output

            nodes.append(node)
            node_map[node_id] = node

        edges: list[dict] = []
        for conn in connections:
            source_id = conn.get("source")
            target_id = conn.get("target")
            if not source_id or not target_id:
                continue

            source_node = node_map.get(source_id)
            target_node = node_map.get(target_id)
            if not source_node or not target_node:
                continue

            # Get target type to apply field name corrections
            target_type = target_node["data"]["type"]
            source_type = source_node["data"]["type"]
            raw_target_input = conn.get("target_input", "input_value")
            
            # Skip edges to forbidden fields - they will be auto-added correctly later
            if raw_target_input in self.FORBIDDEN_TARGET_FIELDS:
                logger.warning(f"Skipping edge to forbidden field: {target_type}.{raw_target_input}")
                continue
            
            # Skip backwards connections - Model → Prompt Template is WRONG!
            # Data should flow: Prompt Template → Model, not the reverse
            model_types = self._get_model_types()
            if source_type in model_types and target_type == "Prompt Template":
                logger.warning(f"Skipping backwards edge: {source_type} → Prompt Template (flow should be reversed)")
                continue
            
            corrected_target_input = self._correct_field_name(target_type, raw_target_input)

            edge = self._create_edge(
                source_node,
                target_node,
                source_output=conn.get("source_output", "message"),
                target_input=corrected_target_input,
            )
            if edge:
                edges.append(edge)

        # If no edges provided, fall back to sequential connection
        if not edges and len(nodes) > 1:
            for i in range(len(nodes) - 1):
                edge = self._create_edge(nodes[i], nodes[i + 1])
                if edge:
                    edges.append(edge)

        # Post-processing: Ensure ChatInput → Prompt Template connection exists
        edges = self._ensure_prompt_template_connections(nodes, node_map, edges)

        return {
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 1},
            },
            "name": name,
            "description": description,
        }
    
    def _ensure_prompt_template_connections(self, nodes: list, node_map: dict, edges: list) -> list:
        """Ensure required connections exist, especially ChatInput → Prompt Template.
        
        Args:
            nodes: List of workflow nodes
            node_map: Mapping of node ID to node
            edges: Existing edges
            
        Returns:
            Updated edges list with any missing connections added
        """
        # Find ChatInput and Prompt Template nodes
        chat_input_node = None
        prompt_template_node = None
        
        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            if node_type == "ChatInput":
                chat_input_node = node
            elif node_type == "Prompt Template":
                prompt_template_node = node
        
        # If we have both, check if ChatInput → Prompt Template connection exists
        if chat_input_node and prompt_template_node:
            chat_input_id = chat_input_node.get("id")
            prompt_template_id = prompt_template_node.get("id")
            
            # Check if any edge connects ChatInput to Prompt Template
            has_connection = any(
                edge.get("source") == chat_input_id and edge.get("target") == prompt_template_id
                for edge in edges
            )
            
            if not has_connection:
                logger.warning(f"Missing ChatInput → Prompt Template connection, adding automatically")
                # Create the missing edge
                edge = self._create_edge(
                    chat_input_node,
                    prompt_template_node,
                    source_output="message",
                    target_input="question"  # Default variable name
                )
                if edge:
                    edges.append(edge)
                    logger.info(f"Added missing edge: ChatInput.message → Prompt Template.question")
        
        # Also ensure Search/Retrieval → Prompt Template connections
        edges = self._ensure_context_connections(nodes, prompt_template_node, edges)
        
        # Ensure Prompt Template → Model connection exists
        edges = self._ensure_prompt_to_model_connection(nodes, prompt_template_node, edges)
        
        return edges
    
    def _ensure_prompt_to_model_connection(self, nodes: list, prompt_template_node: dict | None, edges: list) -> list:
        """Ensure Prompt Template connects to a Model (not the reverse!).
        
        Args:
            nodes: List of workflow nodes
            prompt_template_node: The Prompt Template node (if exists)
            edges: Existing edges
            
        Returns:
            Updated edges list with Prompt Template → Model connection if missing
        """
        if not prompt_template_node:
            return edges
        
        prompt_template_id = prompt_template_node.get("id")
        
        # Get model types dynamically from registry
        model_types = self._get_model_types()
        
        model_node = None
        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            if node_type in model_types:
                model_node = node
                break
        
        if not model_node:
            return edges
        
        model_id = model_node.get("id")
        
        # Check if Prompt Template → Model connection exists
        has_connection = any(
            edge.get("source") == prompt_template_id and edge.get("target") == model_id
            for edge in edges
        )
        
        if not has_connection:
            logger.warning(f"Missing Prompt Template → Model connection, adding automatically")
            edge = self._create_edge(
                prompt_template_node,
                model_node,
                source_output="prompt",
                target_input="input_value"
            )
            if edge:
                edges.append(edge)
                logger.info(f"Added missing edge: Prompt Template.prompt → Model.input_value")
        
        return edges
    
    def _ensure_context_connections(self, nodes: list, prompt_template_node: dict | None, edges: list) -> list:
        """Ensure search/retrieval/memory components connect to Prompt Template properly.
        
        Args:
            nodes: List of workflow nodes
            prompt_template_node: The Prompt Template node (if exists)
            edges: Existing edges
            
        Returns:
            Updated edges list with any missing context/history connections added
        """
        if not prompt_template_node:
            return edges
        
        prompt_template_id = prompt_template_node.get("id")
        
        # Get dynamic component connections from registry
        component_connections = self._build_dynamic_component_connections()
        
        # Create a normalized lookup that handles name variations (spaces, casing)
        normalized_connections = {}
        for comp_type, conn_info in component_connections.items():
            normalized_connections[comp_type] = conn_info
            # Also add variations without spaces and with spaces
            normalized_connections[comp_type.replace(" ", "")] = conn_info
            normalized_connections[comp_type.replace("DB", " DB")] = conn_info  # AstraDB → Astra DB
        
        for node in nodes:
            node_type = node.get("data", {}).get("type", "")
            # Try exact match first, then normalized match
            conn_info = component_connections.get(node_type) or normalized_connections.get(node_type)
            if conn_info:
                node_id = node.get("id")
                output_name, target_var = conn_info
                
                # Check if this node already connects to Prompt Template
                has_connection = any(
                    edge.get("source") == node_id and edge.get("target") == prompt_template_id
                    for edge in edges
                )
                
                if not has_connection:
                    logger.warning(f"Missing {node_type} → Prompt Template connection, adding automatically")
                    edge = self._create_edge(
                        node,
                        prompt_template_node,
                        source_output=output_name,
                        target_input=target_var
                    )
                    if edge:
                        edges.append(edge)
                        logger.info(f"Added missing edge: {node_type}.{output_name} → Prompt Template.{target_var}")
        
        return edges
    
    def _build_minimal_workflow(self, simplified: dict, indexer) -> dict:
        """Build full Langflow workflow from simplified structure with real templates.
        
        Args:
            simplified: Simplified workflow with nodes, connections, name, description
            indexer: ComponentIndexer instance with loaded templates
        
        Returns:
            Complete Langflow workflow with full node templates and proper edges
        """
        name = simplified.get("name", "Zord Generated Workflow")
        description = simplified.get("description", "Generated by Zord AI")
        nodes_simple = simplified.get("nodes", [])
        connections = simplified.get("connections", [])
        
        # Build full nodes with real templates from starter projects
        nodes = []
        for node_simple in nodes_simple:
            node_type = node_simple.get("type")
            node_id = node_simple.get("id")
            position = node_simple.get("position", {"x": 0, "y": 0})
            
            # Generate minimal node structure (Langflow will add template)
            if indexer.has_component_type(node_type):
                node = {
                    "id": node_id,
                    "data": {
                        "id": node_id,
                        "type": node_type
                    },
                    "position": position,
                    "type": "genericNode"
                }
                nodes.append(node)
                logger.info(f"Added {node_type} node (minimal structure)")
            else:
                logger.warning(f"Component type {node_type} not found in index, skipping")
        
        # Build edges from connections using proper handle format
        edges = []
        for conn in connections:
            source_id = conn.get("source")
            target_id = conn.get("target")
            source_output = conn.get("source_output", "message")
            target_input = conn.get("target_input", "input_value")
            
            # Find source and target nodes to get their types
            source_node = next((n for n in nodes if n["id"] == source_id), None)
            target_node = next((n for n in nodes if n["id"] == target_id), None)
            
            if source_node and target_node:
                source_type = source_node["data"]["type"]
                target_type = target_node["data"]["type"]
                
                # Determine the field type based on target component
                # ChatOutput uses HandleInput (type: "other"), most others use MessageInput (type: "str")
                field_type = "other" if target_type == "ChatOutput" else "str"
                
                # Determine input types based on target
                if target_type == "ChatOutput":
                    input_types_str = "œDataœ,œDataFrameœ,œMessageœ"
                else:
                    input_types_str = "œMessageœ"
                
                # Build proper handle format with œ character
                source_handle = f"{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œ{source_output}œ,œoutput_typesœ:[œMessageœ]}}"
                target_handle = f"{{œfieldNameœ:œ{target_input}œ,œidœ:œ{target_id}œ,œinputTypesœ:[{input_types_str}],œtypeœ:œ{field_type}œ}}"
                
                edge = {
                    "id": f"reactflow__edge-{source_id}{source_handle}-{target_id}{target_handle}",
                    "source": source_id,
                    "target": target_id,
                    "sourceHandle": source_handle,
                    "targetHandle": target_handle,
                    "animated": False
                }
                edges.append(edge)
                logger.info(f"Added edge: {source_id}.{source_output} → {target_id}.{target_input}")
            
        workflow = {
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            },
            "name": name,
            "description": description
        }
        
        logger.info(f"Built complete workflow: {len(nodes)} nodes, {len(edges)} edges")
        return workflow
    
    async def _fetch_component_templates(self) -> dict:
        """Fetch component templates from the registry.
        
        Returns:
            Dictionary mapping categories to component templates
        """
        try:
            # Ensure registry is loaded
            if not self.registry._loaded:
                await self.registry.load_components(
                    settings_service=self.settings_service,
                    telemetry_service=self.telemetry_service
                )
                # Clear caches after registry loads to use fresh data
                self._clear_component_caches()
            
            # Get all components from registry
            all_components = self.registry.get_all_components()
            logger.info(f"Fetched {len(all_components)} component categories from registry")
            
            # The structure is: {category: {component_name: component_dict}}
            # where component_dict contains: display_name, description, template, outputs, etc.
            return all_components
        except Exception as e:
            logger.error(f"Error fetching component templates from registry: {e}", exc_info=True)
            return {}
    
    def _check_type_compatibility(
        self, 
        source_types: list[str], 
        target_types: list[str],
        source_comp: str,
        target_comp: str,
        field_name: str
    ) -> bool:
        """Check if source and target types are compatible for connection.
        
        Args:
            source_types: Output types from source component
            target_types: Input types accepted by target component
            source_comp: Source component name (for logging)
            target_comp: Target component name (for logging)
            field_name: Target field name (for logging)
        
        Returns:
            True if types are compatible
        """
        # Direct match
        if any(out_type in target_types for out_type in source_types):
            return True
        
        # Type conversion rules
        conversions = {
            "Message": ["str", "Text", "Data"],  # Message can convert to string/text/data
            "DataFrame": ["Data"],  # DataFrame can convert to Data
            "Data": ["DataFrame", "Message"],  # Data can convert to DataFrame or Message
            "str": ["Message", "Text"],  # String can become Message or Text
            "Text": ["Message", "str"],  # Text and Message are interchangeable
            "Embeddings": [],  # Embeddings only connect to Embeddings
            "LanguageModel": [],  # LanguageModel only connects to LanguageModel
            "VectorStore": [],  # VectorStore only connects to VectorStore
            "Tool": [],  # Tool only connects to Tool
        }
        
        for source_type in source_types:
            if source_type in conversions:
                convertible_types = conversions[source_type]
                if any(conv_type in target_types for conv_type in convertible_types):
                    logger.debug(
                        f"Type conversion: {source_type} → {target_types} for "
                        f"{source_comp} → {target_comp}.{field_name}"
                    )
                    return True
        
        logger.debug(
            f"Type mismatch: {source_types} not compatible with {target_types} for "
            f"{source_comp} → {target_comp}.{field_name}"
        )
        return False
    
    def _create_edge(self, source_node: dict, target_node: dict, source_output: str = "message", target_input: str = "input_value") -> dict | None:
        """Create an edge with proper Langflow handle format.
        
        Args:
            source_node: Source node dict with id, data.type, data.node
            target_node: Target node dict with id, data.type, data.node
            source_output: Output name (fallback, will be auto-detected)
            target_input: Input name (fallback, will be auto-detected)
        
        Returns:
            Edge dict with proper handles, or None if edge cannot be created
        """
        try:
            source_id = source_node["id"]
            target_id = target_node["id"]
            source_type = source_node["data"]["type"]
            target_type = target_node["data"]["type"]
            
            # Get component templates to determine proper output/input names
            source_template = source_node["data"].get("node", {})
            target_template = target_node["data"].get("node", {})
            
            # Extract ACTUAL output name from source component's outputs array
            source_outputs = source_template.get("outputs", [])
            source_output_types = ["Message"]  # Default fallback
            
            if source_outputs and isinstance(source_outputs, list) and len(source_outputs) > 0:
                # Prefer explicitly requested output when available
                matched_output = None
                if source_output:
                    matched_output = next(
                        (out for out in source_outputs if isinstance(out, dict) and out.get("name") == source_output),
                        None,
                    )

                selected_output = matched_output if matched_output else source_outputs[0]
                if isinstance(selected_output, dict):
                    source_output = selected_output.get("name", "message")
                    output_types = selected_output.get("types", ["Message"])
                    if output_types and isinstance(output_types, list):
                        source_output_types = output_types
                    logger.debug(f"Source {source_type} output: {source_output}, types: {source_output_types}")
            else:
                # No outputs defined - try to infer from base_classes
                base_classes = source_template.get("base_classes", [])
                if base_classes:
                    source_output_types = base_classes
                    # Common output field names
                    source_output = "message" if "Message" in base_classes else "data" if "Data" in base_classes or "DataFrame" in base_classes else "output"
                    logger.debug(f"Inferred source {source_type} output: {source_output} from base_classes: {base_classes}")
            
            # Extract ACTUAL input name from target component's template
            # Look for common input field patterns in order of preference
            target_template_dict = target_template.get("template", {})
            target_input_types = ["Message"]  # Default fallback

            connectable_types = [
                "HandleInput", "MessageTextInput", "MessageInput",
                "DataInput", "DataFrameInput", "FileInput",
                "MultilineInput", "StrInput"
            ]

            # Prefer explicitly requested target input if it is connectable and compatible
            requested_target_input = target_input  # Save original request for logging
            if target_input and target_input in target_template_dict:
                field_def = target_template_dict[target_input]
                if isinstance(field_def, dict):
                    input_field_type = field_def.get("_input_type", "")
                    field_input_types = field_def.get("input_types") or field_def.get("types")
                    if input_field_type in connectable_types:
                        if field_input_types and isinstance(field_input_types, list) and len(field_input_types) > 0:
                            if self._check_type_compatibility(
                                source_output_types,
                                field_input_types,
                                source_type,
                                target_type,
                                target_input,
                            ):
                                target_input_types = field_input_types
                                logger.debug(
                                    f"Using requested target input: {target_type}.{target_input} types: {target_input_types}"
                                )
                            else:
                                logger.debug(f"Requested input {target_input} incompatible, will search for alternative")
                                target_input = None
                        else:
                            # No type constraints, accept it
                            target_input_types = field_input_types or target_input_types
                            logger.debug(f"Using requested target input without type constraints: {target_type}.{target_input}")
                    else:
                        logger.debug(f"Requested input {target_input} not connectable ({input_field_type}), will search")
                        target_input = None
            elif target_input:
                # Field doesn't exist in template - but for Prompt Template, this is expected!
                # Dynamic variable fields like {context}, {history}, {question} are created by the template text
                if target_type == "Prompt Template" and target_input in self.PROMPT_VARIABLE_NAMES:
                    # For Prompt Template dynamic variables, create the edge with Message type
                    # The field will be created when we set up the template with variables
                    target_input_types = ["Message"]
                    logger.info(f"Creating edge to Prompt Template dynamic variable: {target_input}")
                    # Keep target_input as is - don't set to None!
                else:
                    logger.debug(f"Requested input {target_input} not found in {target_type} template, will search")
                    target_input = None
            
            # Priority order for input fields based on component type
            # Include ALL common input field names from Langflow components
            input_field_candidates = [
                # Common message/text inputs
                "input_value", "message", "text", "content", "input",
                # Data/DataFrame inputs
                "data", "df", "dataframe", "data_input", "ingest_data", "data_inputs", "input_data",
                # Document/vector store inputs
                "documents", "embedding", "search_query", "search_input",
                # Model/prompt inputs
                "messages", "query", "system_message", "prompt", "template", "text_input",
                # Tools and agents
                "tools", "agent",
                # Context and memory
                "context", "memory", "history",
            ]
            
            # Find the first valid CONNECTABLE input field (only if not already set)
            if not target_input:
                for field_name in input_field_candidates:
                    if field_name in target_template_dict:
                        field_def = target_template_dict[field_name]
                        if isinstance(field_def, dict):
                            # Get field type
                            input_field_type = field_def.get("_input_type", "")
                            
                            # Get input types - check multiple possible keys
                            field_input_types = field_def.get("input_types", None)
                            if not field_input_types:
                                # Try alternate keys
                                field_input_types = field_def.get("types", None)
                            
                            # Accept fields that can take input via handle
                            if input_field_type in connectable_types:
                                # Check type compatibility if input_types are defined
                                if field_input_types and isinstance(field_input_types, list) and len(field_input_types) > 0:
                                    # Enhanced type compatibility checking
                                    has_compatible_type = self._check_type_compatibility(
                                        source_output_types, 
                                        field_input_types,
                                        source_type,
                                        target_type,
                                        field_name
                                    )
                                    if has_compatible_type:
                                        target_input_types = field_input_types  # Use ACTUAL types from field
                                        target_input = field_name
                                        logger.debug(f"Target {target_type} compatible field: {target_input} ({input_field_type}), types: {target_input_types}")
                                        break
                                else:
                                    # No input_types defined - use source types as they'll be validated at runtime
                                    target_input_types = source_output_types
                                    target_input = field_name
                                    logger.debug(f"Target {target_type} accepting field: {target_input} ({input_field_type}), defaulting to source types: {target_input_types}")
                                    break

            # If no match found in candidates, scan ALL fields for any HandleInput
            if not target_input:
                logger.debug(f"No candidate found for {source_type} → {target_type}, scanning all fields...")
                for field_name, field_def in target_template_dict.items():
                    if isinstance(field_def, dict) and field_name not in ["code", "_type"]:
                        input_field_type = field_def.get("_input_type", "")
                        field_input_types = field_def.get("input_types", field_def.get("types", None))
                        
                        # Accept any field that can handle connections
                        if input_field_type in connectable_types:
                            if field_input_types and isinstance(field_input_types, list) and len(field_input_types) > 0:
                                # Check type compatibility with flexible matching
                                has_compatible_type = self._check_type_compatibility(
                                    source_output_types,
                                    field_input_types,
                                    source_type,
                                    target_type,
                                    field_name
                                )
                                
                                if has_compatible_type:
                                    target_input_types = field_input_types  # Use ACTUAL types from field
                                    target_input = field_name
                                    logger.debug(f"Found compatible input in full scan: {target_input}, types: {target_input_types}")
                                    break
                            else:
                                # No type constraints - use source types
                                target_input_types = source_output_types
                                target_input = field_name
                                logger.debug(f"Found input without type constraints: {target_input}, using source types: {target_input_types}")
                                break

            # If STILL no valid input found, this component cannot accept connections
            if not target_input:
                logger.warning(
                    f"No connectable input field found for {target_type}. "
                    f"Available fields: {list(target_template_dict.keys())[:10]}"
                )
                # Log field details for debugging
                for fname, fdef in list(target_template_dict.items())[:5]:
                    if isinstance(fdef, dict):
                        logger.debug(
                            f"  {fname}: type={fdef.get('_input_type')}, "
                            f"input_types={fdef.get('input_types')}"
                        )
                return None  # Don't create this edge
            
            # Get the ACTUAL field type from the template (critical for edge validation!)
            # The frontend compares this exact value when validating edges
            target_field_def = target_template_dict.get(target_input, {})
            target_field_type = target_field_def.get("type", "str") if isinstance(target_field_def, dict) else "str"
            
            # Build proper handle format with œ character for string handles
            # CRITICAL: No spaces after commas - Langflow parser requires exact format
            source_types_str = ",".join([f"œ{t}œ" for t in source_output_types])
            target_types_str = ",".join([f"œ{t}œ" for t in target_input_types])
            
            source_handle = f"{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œ{source_output}œ,œoutput_typesœ:[{source_types_str}]}}"
            target_handle = f"{{œfieldNameœ:œ{target_input}œ,œidœ:œ{target_id}œ,œinputTypesœ:[{target_types_str}],œtypeœ:œ{target_field_type}œ}}"
            
            # CRITICAL: Also create data objects with proper JSON structure (not string-encoded)
            # This is what Langflow frontend actually uses
            edge = {
                "id": f"reactflow__edge-{source_id}{source_handle}-{target_id}{target_handle}",
                "source": source_id,
                "target": target_id,
                "sourceHandle": source_handle,
                "targetHandle": target_handle,
                "animated": False,
                "data": {
                    "sourceHandle": {
                        "dataType": source_type,
                        "id": source_id,
                        "name": source_output,
                        "output_types": source_output_types
                    },
                    "targetHandle": {
                        "fieldName": target_input,
                        "id": target_id,
                        "inputTypes": target_input_types,
                        "type": target_field_type
                    }
                },
                "className": "",
                "selected": False
            }
            
            logger.info(
                f"✓ Created edge: {source_type}.{source_output} ({source_output_types}) → "
                f"{target_type}.{target_input} ({target_input_types})"
            )
            return edge
        except Exception as e:
            logger.error(f"Error creating edge: {e}", exc_info=True)
            return None

    async def _generate_basic_workflow(self, title: str, description: str, component_templates: dict) -> dict:
        """Generate a basic ChatInput -> LanguageModel -> ChatOutput workflow."""
        import uuid
        
        # Look for essential components
        chat_input = component_templates.get("ChatInput")
        chat_output = component_templates.get("ChatOutput") 
        
        # Look for LanguageModel (the generic one the user mentioned)
        language_model = component_templates.get("LanguageModel") or component_templates.get("OpenAIModel")
        
        if not chat_input or not chat_output or not language_model:
            logger.error("Missing essential components for basic workflow")
            logger.info(f"ChatInput: {bool(chat_input)}, ChatOutput: {bool(chat_output)}, Model: {bool(language_model)}")
            return {
                "name": title,
                "description": description,
                "data": {"nodes": [], "edges": [], "viewport": {"x": 0, "y": 0, "zoom": 1}}
            }
        
        # Generate node IDs
        input_id = f"ChatInput-{str(uuid.uuid4())[:5]}"
        model_id = f"LanguageModel-{str(uuid.uuid4())[:5]}"
        output_id = f"ChatOutput-{str(uuid.uuid4())[:5]}"
        
        model_type = "LanguageModel" if "LanguageModel" in component_templates else "OpenAIModel"
        
        # Build nodes
        nodes = [
            {
                "id": input_id,
                "type": "genericNode",
                "position": {"x": 100, "y": 200},
                "data": {
                    "type": "ChatInput",
                    "node": chat_input,
                    "id": input_id
                }
            },
            {
                "id": model_id,
                "type": "genericNode", 
                "position": {"x": 500, "y": 200},
                "data": {
                    "type": model_type,
                    "node": language_model,
                    "id": model_id
                }
            },
            {
                "id": output_id,
                "type": "genericNode",
                "position": {"x": 900, "y": 200},
                "data": {
                    "type": "ChatOutput",
                    "node": chat_output,
                    "id": output_id
                }
            }
        ]
        
        # Build edges with proper handle format
        # Note: Model input_value uses MessageInput (type: "str"), ChatOutput uses HandleInput (type: "other")
        model_input_type = "str"  # MessageInput for models
        output_input_type = "other"  # HandleInput for ChatOutput
        
        edges = [
            {
                "id": f"reactflow__edge-{input_id}{{œdataTypeœ:œChatInputœ,œidœ:œ{input_id}œ,œnameœ:œmessageœ,œoutput_typesœ:[œMessageœ]}}-{model_id}{{œfieldNameœ:œinput_valueœ,œidœ:œ{model_id}œ,œinputTypesœ:[œMessageœ],œtypeœ:œ{model_input_type}œ}}",
                "source": input_id,
                "target": model_id,
                "sourceHandle": "{œdataTypeœ:œChatInputœ,œidœ:œ" + input_id + "œ,œnameœ:œmessageœ,œoutput_typesœ:[œMessageœ]}",
                "targetHandle": "{œfieldNameœ:œinput_valueœ,œidœ:œ" + model_id + f"œ,œinputTypesœ:[œMessageœ],œtypeœ:œ{model_input_type}œ}}",
                "animated": False
            },
            {
                "id": f"reactflow__edge-{model_id}{{œdataTypeœ:œ{model_type}œ,œidœ:œ{model_id}œ,œnameœ:œtext_outputœ,œoutput_typesœ:[œMessageœ]}}-{output_id}{{œfieldNameœ:œinput_valueœ,œidœ:œ{output_id}œ,œinputTypesœ:[œDataœ,œDataFrameœ,œMessageœ],œtypeœ:œ{output_input_type}œ}}",
                "source": model_id,
                "target": output_id,
                "sourceHandle": "{œdataTypeœ:œ" + model_type + "œ,œidœ:œ" + model_id + "œ,œnameœ:œtext_outputœ,œoutput_typesœ:[œMessageœ]}",
                "targetHandle": "{œfieldNameœ:œinput_valueœ,œidœ:œ" + output_id + f"œ,œinputTypesœ:[œDataœ,œDataFrameœ,œMessageœ],œtypeœ:œ{output_input_type}œ}}",
                "animated": False
            }
        ]
        
        logger.info(f"Generated basic workflow with {len(nodes)} nodes and {len(edges)} edges")
        
        return {
            "name": title,
            "description": description,
            "data": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 1}
            }
        }
    
    async def _generate_starter_nodes(self, plan_dict: dict) -> list[dict]:
        """Generate a starter workflow with 3 nodes using REAL component templates from starter projects."""
        import uuid
        
        # Use component indexer to get real templates
        indexer = self.indexer
        
        # Generate unique node IDs
        chat_input_id = f"ChatInput-{str(uuid.uuid4())[:8]}"
        model_id = f"Model-{str(uuid.uuid4())[:8]}"
        chat_output_id = f"ChatOutput-{str(uuid.uuid4())[:8]}"
        
        # Horizontal spacing
        x_position = 100
        
        # Detect model type from plan
        steps = plan_dict.get('steps', [])
        # Always use generic Language Model component instead of specific implementations
        model_type = "LanguageModel"
        
        logger.info("Using generic LanguageModel component for better compatibility")
        
        nodes = []
        
        # Node 1: ChatInput - Use REAL template from starter projects
        # Node 1: ChatInput - Minimal structure
        if indexer.has_component_type("ChatInput"):
            nodes.append({
                "id": chat_input_id,
                "data": {
                    "type": "ChatInput",
                    "id": chat_input_id
                },
                "position": {"x": x_position, "y": 100},
                "type": "genericNode"
            })
            logger.info("Added ChatInput node (minimal structure)")
        
        x_position += 400
        
        # Node 2: Model - Minimal structure
        if indexer.has_component_type(model_type):
            nodes.append({
                "id": model_id,
                "data": {
                    "type": model_type,
                    "id": model_id
                },
                "position": {"x": x_position, "y": 100},
                "type": "genericNode"
            })
            logger.info(f"Added {model_type} node (minimal structure)")
        else:
            logger.warning(f"{model_type} not found, trying alternatives...")
            # Try to find any model
            available_models = indexer.search_components("model")
            if available_models:
                fallback_model = available_models[0]
                logger.info(f"Using fallback model: {fallback_model}")
                nodes.append({
                    "id": model_id,
                    "data": {
                        "type": fallback_model,
                        "id": model_id
                    },
                    "position": {"x": x_position, "y": 100},
                    "type": "genericNode"
                })
        
        x_position += 400
        
        # Node 3: ChatOutput - Minimal structure
        if indexer.has_component_type("ChatOutput"):
            nodes.append({
                "id": chat_output_id,
                "data": {
                    "type": "ChatOutput",
                    "id": chat_output_id
                },
                "position": {"x": x_position, "y": 100},
                "type": "genericNode"
            })
            logger.info("Added ChatOutput node (minimal structure)")
        
        logger.info(f"Generated {len(nodes)} nodes (minimal structure)")
        return nodes
    
    def _generate_starter_edges(self, nodes: list[dict]) -> list[dict]:
        """Generate basic edges connecting starter nodes."""
        edges = []
        
        # Connect ChatInput to Model (first to second node)
        if len(nodes) >= 2:
            source_id = nodes[0]["id"]
            source_type = nodes[0]["data"]["type"]
            target_id = nodes[1]["id"]
            
            # ChatInput outputs "message" which connects to Model's "input_value"
            # Format: {œdataTypeœ:œChatInputœ,œidœ:œChatInput-xxxœ,œnameœ:œmessageœ,œoutput_typesœ:[œMessageœ]}
            source_handle = f'{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œmessageœ,œoutput_typesœ:[œMessageœ]}}'
            
            # Target: Model input_value uses MessageInput (type: "str")
            target_handle = f'{{œfieldNameœ:œinput_valueœ,œidœ:œ{target_id}œ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}}'
            
            edges.append({
                "id": f"reactflow__edge-{source_id}{source_handle}-{target_id}{target_handle}",
                "source": source_id,
                "target": target_id,
                "sourceHandle": source_handle,
                "targetHandle": target_handle,
                "animated": False,
                "style": {"stroke": "#999"}
            })
        
        # Connect Model to ChatOutput (second to third node)
        if len(nodes) >= 3:
            source_id = nodes[1]["id"]
            source_type = nodes[1]["data"]["type"]
            target_id = nodes[2]["id"]
            
            # Model outputs "text_output" which connects to ChatOutput's "input_value"
            # ChatOutput uses HandleInput (type: "other") with input_types: ["Data", "DataFrame", "Message"]
            source_handle = f'{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œtext_outputœ,œoutput_typesœ:[œMessageœ]}}'
            target_handle = f'{{œfieldNameœ:œinput_valueœ,œidœ:œ{target_id}œ,œinputTypesœ:[œDataœ,œDataFrameœ,œMessageœ],œtypeœ:œotherœ}}'
            
            edges.append({
                "id": f"reactflow__edge-{source_id}{source_handle}-{target_id}{target_handle}",
                "source": source_id,
                "target": target_id,
                "sourceHandle": source_handle,
                "targetHandle": target_handle,
                "animated": False,
                "style": {"stroke": "#999"}
            })
        
        return edges
    
    def _generate_description(self, plan_dict: dict) -> str:
        """Generate workflow description from plan."""
        description = f"Generated by Zord AI\n\n"
        description += f"**{plan_dict.get('title', 'Workflow')}**\n\n"
        
        steps = plan_dict.get('steps', [])
        if steps:
            description += "**Plan:**\n"
            for i, step in enumerate(steps, 1):
                component = step.get('component', '')
                desc = step.get('description', '')
                component_info = f" ({component})" if component else ""
                description += f"{i}. {desc}{component_info}\n"
        
        data_flow = plan_dict.get('data_flow', '')
        if data_flow:
            description += f"\n**Data Flow:**\n{data_flow}\n"
        
        description += "\n**Note:** This is a starter workflow. Customize it by adding more components based on the plan above."
        
        return description

    async def modify_plan(
        self,
        plan: dict | Any,
        modification_request: str,
        conversation_history: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Modify an existing workflow plan.

        Args:
            plan: Current workflow plan (dict or Pydantic model)
            modification_request: What to change
            conversation_history: Previous conversation

        Returns:
            Dict with modified 'plan' and 'message' keys
        """
        # Convert plan to dict if it's a Pydantic model
        if hasattr(plan, 'model_dump'):
            plan_dict = plan.model_dump()
        elif hasattr(plan, 'dict'):
            plan_dict = plan.dict()
        else:
            plan_dict = plan
        
        plan_text = json.dumps(plan_dict, indent=2)
        user_message = MODIFY_PLAN_PROMPT.format(
            current_plan=plan_text,
            modification=modification_request,
        )
        
        response = await self._call_claude(
            user_message=user_message,
            conversation_history=conversation_history,
        )
        
        # Extract JSON from response
        data = self._extract_json_from_response(response)
        
        return {
            "plan": data.get("plan", {}),
            "message": data.get("message", "Plan has been modified:"),
        }
