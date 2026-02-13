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




@register_tool(tags=["invoice_processing", "categorization"])
def categorize_expenditure(action_context: ActionContext, description: str) -> str:
    """
    Categorize an invoice expenditure based on a short description.
    
    Args:
        description: A one-sentence summary of the expenditure.
        
    Returns:
        A category name from the predefined set of 20 categories.
    """
    categories = [
        "Office Supplies", "IT Equipment", "Software Licenses", "Consulting Services", 
        "Travel Expenses", "Marketing", "Training & Development", "Facilities Maintenance",
        "Utilities", "Legal Services", "Insurance", "Medical Services", "Payroll",
        "Research & Development", "Manufacturing Supplies", "Construction", "Logistics",
        "Customer Support", "Security Services", "Miscellaneous"
    ]
    
    return prompt_expert(
        action_context=action_context,
        description_of_expert="A senior financial analyst with deep expertise in corporate spending categorization.",
        prompt=f"Given the following description: '{description}', classify the expense into one of these categories:\n{categories}"
    )





    @register_tool(tags=["invoice_processing", "validation"])
def check_purchasing_rules(action_context: ActionContext, invoice_data: dict) -> dict:
    """
    Validate an invoice against company purchasing policies.
    
    Args:
        invoice_data: Extracted invoice details, including vendor, amount, and line items.
        
    Returns:
        A dictionary indicating whether the invoice is compliant, with explanations.
    """
    # Load the latest purchasing rules from disk
    rules_path = "config/purchasing_rules.txt"
    
    try:
        with open(rules_path, "r") as f:
            purchasing_rules = f.read()
    except FileNotFoundError:
        purchasing_rules = "No rules available. Assume all invoices are compliant."

    return prompt_expert(
        action_context=action_context,
        description_of_expert="A corporate procurement compliance officer with extensive knowledge of purchasing policies.",
        prompt=f"""
        Given this invoice data: {invoice_data}, check whether it complies with company purchasing rules.
        The latest purchasing rules are as follows:
        
        {purchasing_rules}
        
        Identify any violations or missing requirements. Respond with:
        - "compliant": true or false
        - "issues": A brief explanation of any problems found
        """
    )





@register_tool(tags=["invoice_processing", "validation"])
def check_purchasing_rules(action_context: ActionContext, invoice_data: dict) -> dict:
    """
    Validate an invoice against company purchasing policies, returning a structured response.
    
    Args:
        invoice_data: Extracted invoice details, including vendor, amount, and line items.
        
    Returns:
        A structured JSON response indicating whether the invoice is compliant and why.
    """
    rules_path = "config/purchasing_rules.txt"

    try:
        with open(rules_path, "r") as f:
            purchasing_rules = f.read()
    except FileNotFoundError:
        purchasing_rules = "No rules available. Assume all invoices are compliant."

    validation_schema = {
        "type": "object",
        "properties": {
            "compliant": {"type": "boolean"},
            "issues": {"type": "string"}
        }
    }

    return prompt_llm_for_json(
        action_context=action_context,
        schema=validation_schema,
        prompt=f"""
        Given this invoice data: {invoice_data}, check whether it complies with company purchasing rules.
        The latest purchasing rules are as follows:
        
        {purchasing_rules}
        
        Respond with a JSON object containing:
        - `compliant`: true if the invoice follows all policies, false otherwise.
        - `issues`: A brief explanation of any violations or missing requirements.
        """
    )






    def create_invoice_agent():
    # Create action registry with invoice tools
    action_registry = PythonActionRegistry()

    # Define invoice processing goals
    goals = [
        Goal(
            name="Persona",
            description="You are an Invoice Processing Agent, specialized in handling invoices efficiently."
        ),
        Goal(
            name="Process Invoices",
            description="""
            Your goal is to process invoices accurately. For each invoice:
            1. Extract key details such as vendor, amount, and line items.
            2. Generate a one-sentence summary of the expenditure.
            3. Categorize the expenditure using an expert.
            4. Validate the invoice against purchasing policies.
            5. Store the processed invoice with categorization and validation status.
            6. Return a summary of the invoice processing results.
            """
        )
    ]

    # Define agent environment
    environment = PythonEnvironment()

    return Agent(
        goals=goals,
        agent_language=AgentFunctionCallingActionLanguage(),
        action_registry=action_registry,
        generate_response=generate_response,
        environment=environment
    )








    THE EXECUTION OF THE Agent

    invoice_text = """
    Invoice #4567
    Date: 2025-02-01
    Vendor: Tech Solutions Inc.
    Items: 
      - Laptop - $1,200
      - External Monitor - $300
    Total: $1,500
"""

# Create an agent instance
agent = create_invoice_agent()

# Process the invoice
response = agent.run(f"Process this invoice:\n\n{invoice_text}")

print(response)



