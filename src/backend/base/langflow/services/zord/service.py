"""Zord AI Service - Claude-powered workflow architect."""

from __future__ import annotations

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


class ZordAIService:
    """Service for Zord AI workflow design using Claude."""

    def __init__(self):
        """Initialize Zord AI Service with Claude client."""
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
        self.max_tokens = 4096
        
        # Initialize ChromaDB semantic indexer
        try:
            self.indexer = get_chroma_indexer()
            stats = self.indexer.get_stats()
            logger.info(f"Zord AI initialized with ChromaDB indexer: {stats}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB indexer: {e}")
            logger.error("Please run initialize_chroma.py to set up the collection")
            raise

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
            # Build system prompt with available components
            component_types = self.indexer.get_all_component_types()
            available_components = "\n".join([f"- {comp}" for comp in component_types])
            
            # Enhance system prompt with real available components
            enhanced_system_prompt = SYSTEM_PROMPT + "\n\n## AVAILABLE COMPONENTS IN REPOSITORY\n\nThese are the ONLY components you can use (extracted from actual Langflow LFX components):\n" + available_components + "\n\n**CRITICAL**: Only use components from the list above. Do not invent or hallucinate component names."
            
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
            component_templates = {}
            for category, components in all_component_categories.items():
                if isinstance(components, dict):
                    for comp_name, comp_template in components.items():
                        component_templates[comp_name] = comp_template
            
            logger.info(f"Loaded {len(component_templates)} component definitions from {len(all_component_categories)} categories")
            
            # If no components in plan, fallback to basic workflow
            if not components_list or len(components_list) == 0:
                logger.info("No components in plan, generating basic chat workflow")
                workflow = await self._generate_basic_workflow(plan_title, plan_description, component_templates)
                return {
                    "json": workflow,
                    "message": "I've created a basic chat workflow! You can customize it by adding more components.",
                }
            
            # Build nodes from plan components  
            nodes = []
            node_id_map = {}
            used_components = set()  # Track used component types to avoid duplicates
            
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
                        
                        # Skip legacy components - prefer modern ones
                        is_legacy = tmpl.get("legacy", False)
                        if is_legacy:
                            # Check if there's a modern replacement
                            replacements = tmpl.get("replacement", [])
                            if replacements:
                                logger.info(f"Skipping legacy component '{name}', looking for replacement: {replacements}")
                                continue
                        
                        tmpl_desc = tmpl.get("description", "").lower()
                        tmpl_display = tmpl.get("display_name", "").lower()
                        
                        if (search_query in tmpl_desc or 
                            name.lower() in search_query or 
                            search_query in tmpl_display or
                            comp_name.lower() in name.lower()):
                            # Prefer non-legacy matches
                            if best_match is None or (is_legacy and not best_match.get("legacy", False)):
                                best_match = tmpl
                                best_match_name = name
                    
                    if best_match:
                        template = best_match
                        matched_name = best_match_name
                        logger.info(f"Fuzzy matched '{comp_name}' to '{matched_name}'")
                
                if not template:
                    logger.warning(f"No template found for component: {comp_name} (type: {comp_type})")
                    continue
                
                # Check for duplicates - skip if we already have this component type
                if matched_name in used_components:
                    logger.info(f"Skipping duplicate component: {matched_name}")
                    continue
                
                used_components.add(matched_name)
                
                # Generate unique node ID with component type
                import uuid
                node_id = f"{matched_name}-{str(uuid.uuid4())[:5]}"
                node_id_map[comp_name] = node_id
                
                # Build node with Langflow's expected structure
                node = {
                    "id": node_id,
                    "type": "genericNode",
                    "position": {"x": 150 + (len(nodes) * 400), "y": 250},  # Horizontal layout
                    "data": {
                        "type": matched_name,  # Component type name
                        "node": template,  # Full component template from Langflow
                        "id": node_id
                    }
                }
                nodes.append(node)
                logger.info(f"Added node {len(nodes)}: {matched_name} (id: {node_id}, legacy: {template.get('legacy', False)})")
            
            # Build edges - automatically connect nodes in sequence
            edges = []
            
            # Try to use connections from plan first
            connections = plan_dict.get("connections", [])
            if connections and len(connections) > 0:
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
                                logger.info(f"Connected (from plan): {source_node['data']['type']} -> {target_node['data']['type']}")
            
            # If no connections or insufficient edges, auto-connect ALL nodes in sequence
            if len(edges) < len(nodes) - 1:
                logger.info(f"Auto-connecting {len(nodes)} nodes in sequence (plan had {len(edges)} edges)")
                edges.clear()  # Start fresh
                
                for i in range(len(nodes) - 1):
                    source_node = nodes[i]
                    target_node = nodes[i + 1]
                    edge = self._create_edge(source_node, target_node)
                    if edge:
                        edges.append(edge)
                        logger.info(f"Auto-connected: {source_node['data']['type']} -> {target_node['data']['type']}")
            
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
            
            logger.info(f"Built complete workflow: {len(nodes)} nodes, {len(edges)} edges")
            return {
                "json": workflow,
                "message": f"Successfully generated workflow with {len(nodes)} components"
            }
            
        except Exception as e:
            logger.error(f"Error in workflow generation: {e}", exc_info=True)
            
            return {
                "json": {"error": str(e)},
                "message": f"Failed to generate workflow: {str(e)}. Please check the logs for details.",
            }
    
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
                
                # Build proper handle format with œ character (using default Message type for minimal workflow)
                source_handle = f"{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œ{source_output}œ,œoutput_typesœ:[œMessageœ]}}"
                target_handle = f"{{œfieldNameœ:œ{target_input}œ,œidœ:œ{target_id}œ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}}"
                
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
        """Fetch component templates from Langflow's component system."""
        try:
            from lfx.interface.components import get_and_cache_all_types_dict
            from langflow.services.deps import get_settings_service
            
            # Get settings service
            settings_service = get_settings_service()
            
            # Get all component templates - this returns the full component dict
            all_types = await get_and_cache_all_types_dict(settings_service)
            logger.info(f"Fetched {len(all_types)} component categories")
            
            # The structure is: {category: {component_name: component_dict}}
            # where component_dict contains: display_name, description, template, outputs, etc.
            return all_types
        except Exception as e:
            logger.error(f"Error fetching component templates: {e}", exc_info=True)
            return {}
    
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
                first_output = source_outputs[0]
                if isinstance(first_output, dict):
                    # Use the actual 'name' field, not 'display_name'
                    source_output = first_output.get("name", "message")
                    # Get actual output types from the component definition
                    output_types = first_output.get("types", ["Message"])
                    if output_types and isinstance(output_types, list):
                        source_output_types = output_types
                    logger.debug(f"Source {source_type} output: {source_output}, types: {source_output_types}")
            
            # Extract ACTUAL input name from target component's template
            # Look for common input field patterns in order of preference
            target_template_dict = target_template.get("template", {})
            target_input_types = ["Message"]  # Default fallback
            
            # Priority order for input fields
            input_field_candidates = [
                "input_value", "message", "text", "content",
                "ingest_data", "data_input", "data", "documents",
                "messages", "query", "system_message", "prompt"
            ]
            
            # Find the first valid CONNECTABLE input field
            target_input = None
            for field_name in input_field_candidates:
                if field_name in target_template_dict:
                    field_def = target_template_dict[field_name]
                    if isinstance(field_def, dict):
                        # Get field type
                        input_field_type = field_def.get("_input_type", "")
                        
                        # Get input types - must NOT be empty
                        field_input_types = field_def.get("input_types", None)
                        
                        # CRITICAL CHECKS:
                        # 1. Must be HandleInput OR MessageTextInput
                        # 2. Must have non-empty input_types array
                        # 3. input_types must contain compatible types
                        
                        if field_input_types and isinstance(field_input_types, list) and len(field_input_types) > 0:
                            # Check if it's a connectable field type
                            if input_field_type in ["HandleInput", "MessageTextInput", "MessageInput"]:
                                # Check type compatibility: at least one output type must match one input type
                                has_compatible_type = any(out_type in field_input_types for out_type in source_output_types)
                                
                                if has_compatible_type:
                                    target_input_types = field_input_types
                                    target_input = field_name
                                    logger.debug(f"Target {target_type} compatible field: {target_input} ({input_field_type}), types: {target_input_types}")
                                    break
                                else:
                                    logger.debug(f"Skipping {field_name}: no type match. Output: {source_output_types}, Input: {field_input_types}")
                            else:
                                logger.debug(f"Skipping {field_name}: wrong type {input_field_type}")
                        else:
                            logger.debug(f"Skipping {field_name}: empty or no input_types")

            # If no match found in candidates, scan ALL fields for any HandleInput
            if not target_input:
                logger.debug(f"No candidate found, scanning all fields for HandleInput...")
                for field_name, field_def in target_template_dict.items():
                    if isinstance(field_def, dict) and field_name not in ["code", "_type"]:
                        input_field_type = field_def.get("_input_type", "")
                        field_input_types = field_def.get("input_types", None)
                        
                        # Only HandleInput, MessageTextInput, or MessageInput with non-empty input_types
                        if input_field_type in ["HandleInput", "MessageTextInput", "MessageInput"]:
                            if field_input_types and isinstance(field_input_types, list) and len(field_input_types) > 0:
                                # Check type compatibility
                                has_compatible_type = any(out_type in field_input_types for out_type in source_output_types)
                                
                                if has_compatible_type:
                                    target_input_types = field_input_types
                                    target_input = field_name
                                    logger.debug(f"Found compatible input: {target_input}, types: {target_input_types}")
                                    break
                                else:
                                    logger.debug(f"Skipping {field_name}: no type match in full scan")

            # If STILL no valid input found, this component cannot accept connections
            if not target_input:
                logger.warning(f"No connectable input field found for {target_type}. Component does not accept connections.")
                logger.warning(f"Available fields: {list(target_template_dict.keys())}")
                return None  # Don't create this edge
            
            # Convert types list to proper format for handles
            source_types_str = ", ".join([f"œ{t}œ" for t in source_output_types])
            target_types_str = ", ".join([f"œ{t}œ" for t in target_input_types])
            
            # Build proper handle format with œ character
            source_handle = f"{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œ{source_output}œ,œoutput_typesœ:[{source_types_str}]}}"
            target_handle = f"{{œfieldNameœ:œ{target_input}œ,œidœ:œ{target_id}œ,œinputTypesœ:[{target_types_str}],œtypeœ:œstrœ}}"
            
            edge = {
                "id": f"reactflow__edge-{source_id}{source_handle}-{target_id}{target_handle}",
                "source": source_id,
                "target": target_id,
                "sourceHandle": source_handle,
                "targetHandle": target_handle,
                "animated": False
            }
            
            logger.info(f"Created edge: {source_type}.{source_output} -> {target_type}.{target_input}")
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
        edges = [
            {
                "id": f"reactflow__edge-{input_id}{{œdataTypeœ:œChatInputœ,œidœ:œ{input_id}œ,œnameœ:œmessageœ,œoutput_typesœ:[œMessageœ]}}-{model_id}{{œfieldNameœ:œinput_valueœ,œidœ:œ{model_id}œ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}}",
                "source": input_id,
                "target": model_id,
                "sourceHandle": "{œdataTypeœ:œChatInputœ,œidœ:œ" + input_id + "œ,œnameœ:œmessageœ,œoutput_typesœ:[œMessageœ]}",
                "targetHandle": "{œfieldNameœ:œinput_valueœ,œidœ:œ" + model_id + "œ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}",
                "animated": False
            },
            {
                "id": f"reactflow__edge-{model_id}{{œdataTypeœ:œ{model_type}œ,œidœ:œ{model_id}œ,œnameœ:œtext_outputœ,œoutput_typesœ:[œMessageœ]}}-{output_id}{{œfieldNameœ:œinput_valueœ,œidœ:œ{output_id}œ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}}",
                "source": model_id,
                "target": output_id,
                "sourceHandle": "{œdataTypeœ:œ" + model_type + "œ,œidœ:œ" + model_id + "œ,œnameœ:œtext_outputœ,œoutput_typesœ:[œMessageœ]}",
                "targetHandle": "{œfieldNameœ:œinput_valueœ,œidœ:œ" + output_id + "œ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}",
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
        model_type = "OpenAIModel"  # default
        
        for step in steps:
            component = step.get('component', '').lower()
            if 'openai' in component:
                model_type = "OpenAIModel"
                break
            elif 'anthropic' in component or 'claude' in component:
                model_type = "AnthropicModel"
                break
            elif 'google' in component or 'gemini' in component:
                model_type = "GoogleGenerativeAIModel"
                break
        
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
            
            # Target: {œfieldNameœ:œinput_valueœ,œidœ:œOpenAIModel-xxxœ,œinputTypesœ:[œMessageœ],œtypeœ:œstrœ}
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
            source_handle = f'{{œdataTypeœ:œ{source_type}œ,œidœ:œ{source_id}œ,œnameœ:œtext_outputœ,œoutput_typesœ:[œMessageœ]}}'
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
