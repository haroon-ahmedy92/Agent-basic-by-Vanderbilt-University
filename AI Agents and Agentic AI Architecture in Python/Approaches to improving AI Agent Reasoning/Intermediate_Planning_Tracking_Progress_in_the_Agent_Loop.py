# Tracking Progress
# In complex tasks, agents need to periodically step back and assess their progress. 
# Let’s build a capability that adds reflection and progress tracking to the end of each agent loop iteration, 
# allowing the agent to understand what it just did and plan its next steps more effectively.

# To achieve this, we introduce a track_progress function that evaluates the agent’s current state after each action. 
# This function operates similarly to our planning function but shifts the focus to assessment rather than forward planning. 
# By analyzing available tools, memory context, and completed steps, the agent can identify what has been accomplished, any blockers encountered, 
# and what should happen next. This ensures the agent maintains awareness of its trajectory rather than blindly executing actions without reflection.

# By integrating track_progress at the end of each loop iteration, we enable the agent to continuously refine its strategy. 
# Instead of relying solely on a predefined plan, the agent dynamically adapts based on real-time feedback. 
# This aligns with how human problem-solving works—we plan, act, evaluate, and adjust. With this addition, 
# our agent becomes more resilient and capable, recognizing obstacles early and making course corrections as needed, 
# and potentially leading to more efficient and intelligent execution of complex workflows.


@register_tool(tags=["prompts"])
def track_progress(action_context: ActionContext,
                   _memory: Memory,
                   action_registry: ActionRegistry) -> str:
    """Generate a progress report based on the current task, available tools, and memory context."""

    # Get tool descriptions for the prompt
    tool_descriptions = "\n".join(
        f"- {action.name}: {action.description}"
        for action in action_registry.get_actions()
    )

    # Get relevant memory content
    memory_content = "\n".join(
        f"{m['type']}: {m['content']}"
        for m in _memory.items
        if m['type'] in ['user', 'system']
    )

    # Construct the prompt as a string
    prompt = f"""Given the current task and available tools, generate a progress report.
Think through this step by step:

1. Identify the key components of the task and the intended outcome.
2. Assess the progress made so far based on available information.
3. Identify any blockers or issues preventing completion.
4. Suggest the next steps to move forward efficiently.
5. Recommend any tool usage that might help complete the task.

Write your progress report in clear, structured points.

Available tools:
{tool_descriptions}

Task context from memory:
{memory_content}

Provide a well-organized report on the current progress and next steps."""

    return prompt_llm(action_context=action_context, prompt=prompt)