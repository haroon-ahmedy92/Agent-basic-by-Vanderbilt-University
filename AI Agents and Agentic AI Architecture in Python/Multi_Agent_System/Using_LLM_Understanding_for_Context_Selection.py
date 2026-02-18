# Selective Memory Sharing: Using LLM Understanding for Context Selection
# Sometimes we want an agent to intelligently choose which parts of its memory to share with another agent. 
# Instead of using rigid rules, we can leverage the LLM’s understanding of context to select the most relevant memories for the task at hand.

# Let’s implement a version of memory sharing that uses the LLM to analyze and select relevant memories with self-prompting:


@register_tool()
def prompt_llm_for_json(action_context: ActionContext, schema: dict, prompt: str):
    """
    Have the LLM generate JSON in response to a prompt. Always use this tool when you need structured data out of the LLM.
    This function takes a JSON schema that specifies the structure of the expected JSON response.
    
    Args:
        schema: JSON schema defining the expected structure
        prompt: The prompt to send to the LLM
        
    Returns:
        A dictionary matching the provided schema with extracted information
    """
    generate_response = action_context.get("llm")
    
    # Try up to 3 times to get valid JSON
    for i in range(3):
        try:
            # Send prompt with schema instruction and get response
            response = generate_response(Prompt(messages=[
                {"role": "system", 
                 "content": f"You MUST produce output that adheres to the following JSON schema:\n\n{json.dumps(schema, indent=4)}. Output your JSON in a ```json markdown block."},
                {"role": "user", "content": prompt}
            ]))

            # Check if the response has json inside of a markdown code block
            if "```json" in response:
                # Search from the front and then the back
                start = response.find("```json")
                end = response.rfind("```")
                response = response[start+7:end].strip()

            # Parse and validate the JSON response
            return json.loads(response)
            
        except Exception as e:
            if i == 2:  # On last try, raise the error
                raise e
            print(f"Error generating response: {e}")
            print("Retrying...")



@register_tool(description="Delegate a task to another agent with selected context")
def call_agent_with_selected_context(action_context: ActionContext,
                                   agent_name: str,
                                   task: str) -> dict:
    """Call agent with LLM-selected relevant memories."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Get current memory and add IDs
    current_memory = action_context.get_memory()
    memory_with_ids = []
    for idx, item in enumerate(current_memory.items):
        memory_with_ids.append({
            **item,
            "memory_id": f"mem_{idx}"
        })
    
    # Create schema for memory selection
    selection_schema = {
        "type": "object",
        "properties": {
            "selected_memories": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "ID of a memory to include"
                }
            },
            "reasoning": {
                "type": "string",
                "description": "Explanation of why these memories were selected"
            }
        },
        "required": ["selected_memories", "reasoning"]
    }
    
    # Format memories for LLM review
    memory_text = "\n".join([
        f"Memory {m['memory_id']}: {m['content']}" 
        for m in memory_with_ids
    ])
    
    # Ask LLM to select relevant memories
    selection_prompt = f"""Review these memories and select the ones relevant for this task:

Task: {task}

Available Memories:
{memory_text}

Select memories that provide important context or information for this specific task.
Explain your selection process."""

    # Self-prompting magic to find the most relevant memories
    selection = prompt_llm_for_json(
        action_context=action_context,
        schema=selection_schema,
        prompt=selection_prompt
    )
    
    # Create filtered memory from selection
    filtered_memory = Memory()
    selected_ids = set(selection["selected_memories"])
    for item in memory_with_ids:
        if item["memory_id"] in selected_ids:
            # Remove the temporary memory_id before adding
            item_copy = item.copy()
            del item_copy["memory_id"]
            filtered_memory.add_memory(item_copy)
    
    # Run the agent with selected memories
    result_memory = agent_run(
        user_input=task,
        memory=filtered_memory
    )
    
    # Add results and selection reasoning to original memory
    current_memory.add_memory({
        "type": "system",
        "content": f"Memory selection reasoning: {selection['reasoning']}"
    })
    
    for memory_item in result_memory.items:
        current_memory.add_memory(memory_item)
    
    return {
        "result": result_memory.items[-1].get("content", "No result"),
        "shared_memories": len(filtered_memory.items),
        "selection_reasoning": selection["reasoning"]
    }

