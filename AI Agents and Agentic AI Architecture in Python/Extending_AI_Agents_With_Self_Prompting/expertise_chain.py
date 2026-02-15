@register_tool()
def prompt_expert(action_context: ActionContext, description_of_expert: str, prompt: str) -> str:
    """
    Generate a response from an expert persona.
    
    The expert's background and specialization should be thoroughly described to ensure
    responses align with their expertise. The prompt should be focused on topics within
    their domain of knowledge.
    
    Args:
        description_of_expert: Detailed description of the expert's background and expertise
        prompt: The specific question or task for the expert
        
    Returns:
        The expert's response
    """
    generate_response = action_context.get("llm")
    response = generate_response(Prompt(messages=[
        {"role": "system", 
         "content": f"Act as the following expert and respond accordingly: {description_of_expert}"},
        {"role": "user", "content": prompt}
    ]))
    return response





def develop_feature(action_context: ActionContext, feature_request: str) -> dict:
    """
    Process a feature request through a chain of expert personas.
    """
    # Step 1: Product expert defines requirements
    requirements = prompt_expert(
        action_context,
        "product manager expert",
        f"Convert this feature request into detailed requirements: {feature_request}"
    )
    
    # Step 2: Architecture expert designs the solution
    architecture = prompt_expert(
        action_context,
        "software architect expert",
        f"Design an architecture for these requirements: {requirements}"
    )
    
    # Step 3: Developer expert implements the code
    implementation = prompt_expert(
        action_context,
        "senior developer expert",
        f"Implement code for this architecture: {architecture}"
    )
    
    # Step 4: QA expert creates test cases
    tests = prompt_expert(
        action_context,
        "QA engineer expert",
        f"Create test cases for this implementation: {implementation}"
    )
    
    # Step 5: Documentation expert creates documentation
    documentation = prompt_expert(
        action_context,
        "technical writer expert",
        f"Document this implementation: {implementation}"
    )
    
    return {
        "requirements": requirements,
        "architecture": architecture,
        "implementation": implementation,
        "tests": tests,
        "documentation": documentation
    }