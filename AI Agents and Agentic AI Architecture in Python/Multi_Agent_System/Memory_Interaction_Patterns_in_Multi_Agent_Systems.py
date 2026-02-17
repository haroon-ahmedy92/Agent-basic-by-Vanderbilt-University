# When agents work together, how they share and manage memory dramatically affects their collaboration. 
# Let’s explore different patterns for memory interaction between agents, understanding when each pattern is most useful and how to implement it.

# Message Passing: The Basic Pattern
# The simplest form of agent interaction is message passing, 
# where one agent sends a request and receives a response. This is like sending an email to a colleague - they get your message, do some work, and send back their results. You don’t see how they arrived at their answer; you just get their final response.

# Here’s how we implement basic message passing:



@register_tool()
def call_agent(action_context: ActionContext, 
               agent_name: str, 
               task: str) -> dict:
    """Basic message passing between agents."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Create fresh memory for the invoked agent
    invoked_memory = Memory()
    
    # Run agent and get result
    result_memory = agent_run(
        user_input=task,
        memory=invoked_memory
    )
    
    # Return only the final memory item
    return {
        "result": result_memory.items[-1].get("content", "No result")
    }


# Memory Reflection: Learning from the Process
# Sometimes we want the first agent to understand how the second agent reached its conclusion. 
# This is like asking a colleague to not just give you their answer, but to explain their thought process. 
# We can achieve this by copying all of the second agent’s memories back to the first agent:

@register_tool()
def call_agent_with_reflection(action_context: ActionContext, 
                             agent_name: str, 
                             task: str) -> dict:
    """Call agent and receive their full thought process."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Create fresh memory for invoked agent
    invoked_memory = Memory()
    
    # Run agent
    result_memory = agent_run(
        user_input=task,
        memory=invoked_memory
    )
    
    # Get the caller's memory
    caller_memory = action_context.get_memory()
    
    # Add all memories from invoked agent to caller
    # although we could leave off the last memory to
    # avoid duplication
    for memory_item in result_memory.items:
        caller_memory.add_memory({
            "type": f"{agent_name}_thought",  # Mark source of memory
            "content": memory_item["content"]
        })
    
    return {
        "result": result_memory.items[-1].get("content", "No result"),
        "memories_added": len(result_memory.items)
    }





# Memory Handoff: Continuing the Conversation
# Sometimes we want the second agent to pick up where the first agent left off, with full context of what’s happened so far. 
# This is like having a colleague step in to take over a project - they need to know everything that’s happened up to that point:

@register_tool()
def hand_off_to_agent(action_context: ActionContext, 
                      agent_name: str, 
                      task: str) -> dict:
    """Transfer control to another agent with shared memory."""
    agent_registry = action_context.get_agent_registry()
    agent_run = agent_registry.get_agent(agent_name)
    
    # Get the current memory to hand off
    current_memory = action_context.get_memory()
    
    # Run agent with existing memory
    result_memory = agent_run(
        user_input=task,
        memory=current_memory  # Pass the existing memory
    )
    
    return {
        "result": result_memory.items[-1].get("content", "No result"),
        "memory_id": id(result_memory)
    }



