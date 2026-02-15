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



@register_tool()
def create_and_consult_expert(action_context: ActionContext, 
                             expertise_domain: str,
                             problem_description: str) -> str:
    """
    Dynamically create and consult an expert persona based on the specific domain and problem.
    
    Args:
        expertise_domain: The specific domain of expertise needed
        problem_description: Detailed description of the problem to be solved
        
    Returns:
        The expert's insights and recommendations
    """
    # Step 1: Dynamically generate a persona description
    persona_description_prompt = f"""
    Create a detailed description of an expert in {expertise_domain} who would be 
    ideally suited to address the following problem:
    
    {problem_description}
    
    Your description should include:
    - The expert's background and experience
    - Their specific areas of specialization within {expertise_domain}
    - Their approach to problem-solving
    - The unique perspective they bring to this type of challenge
    """
    
    generate_response = action_context.get("llm")
    persona_description = generate_response(Prompt(messages=[
        {"role": "user", "content": persona_description_prompt}
    ]))
    
    # Step 2: Generate a specialized consultation prompt
    consultation_prompt_generator = f"""
    Create a detailed consultation prompt for an expert in {expertise_domain} 
    addressing the following problem:
    
    {problem_description}
    
    The prompt should guide the expert to provide comprehensive insights and
    actionable recommendations specific to this problem.
    """
    
    consultation_prompt = generate_response(Prompt(messages=[
        {"role": "user", "content": consultation_prompt_generator}
    ]))
    
    # Step 3: Consult the dynamically created persona
    return prompt_expert(
        action_context=action_context,
        description_of_expert=persona_description,
        prompt=consultation_prompt
    )



    