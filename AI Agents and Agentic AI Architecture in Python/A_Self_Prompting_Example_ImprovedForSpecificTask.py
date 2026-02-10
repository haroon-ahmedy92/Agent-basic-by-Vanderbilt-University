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



@register_tool(tags=["document_processing", "invoices"])
def extract_invoice_data(action_context: ActionContext, document_text: str) -> dict:
    """
    Extract standardized invoice data from document text. This tool enforces a consistent
    schema for invoice data extraction across all documents.
    
    Args:
        document_text: The text content of the invoice to process
        
    Returns:
        A dictionary containing extracted invoice data in a standardized format
    """
    # Define a fixed schema for invoice data
    invoice_schema = {
        "type": "object",
        "required": ["invoice_number", "date", "amount"],  # These fields must be present
        "properties": {
            "invoice_number": {"type": "string"},
            "date": {"type": "string", "format": "date"},
            "amount": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "currency": {"type": "string"}
                },
                "required": ["value", "currency"]
            },
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "tax_id": {"type": "string"},
                    "address": {"type": "string"}
                },
                "required": ["name"]
            },
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"}
                    },
                    "required": ["description", "total"]
                }
            }
        }
    }

    # Create a focused prompt that guides the LLM in invoice extraction
    extraction_prompt = f"""
    Extract invoice information from the following document text. 
    Focus on identifying:
    - Invoice number (usually labeled as 'Invoice #', 'Reference', etc.)
    - Date (any dates labeled as 'Invoice Date', 'Issue Date', etc.)
    - Amount (total amount due, including currency)
    - Vendor information (company name, tax ID if present, address)
    - Line items (individual charges and their details)

    Document text:
    {document_text}
    """
    
    # Use our general extraction tool with the specialized schema and prompt
    return prompt_llm_for_json(
        action_context=action_context,
        schema=invoice_schema,
        prompt=extraction_prompt
    )