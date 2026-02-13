import os
import json
from dotenv import load_dotenv
from litellm import completion

# Simple mock classes for demonstration
class Prompt:
    def __init__(self, messages):
        self.messages = messages

class ActionContext:
    def __init__(self, llm_func):
        self.llm_func = llm_func
    
    def get(self, key):
        if key == "llm":
            return self.llm_func
        return None

class Goal:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class PythonActionRegistry:
    def __init__(self):
        self.actions = {}

class PythonEnvironment:
    def __init__(self):
        pass

class AgentFunctionCallingActionLanguage:
    def __init__(self):
        pass

class Agent:
    def __init__(self, goals, agent_language, action_registry, generate_response, environment):
        self.goals = goals
        self.agent_language = agent_language
        self.action_registry = action_registry
        self.generate_response = generate_response
        self.environment = environment
    
    def run(self, prompt):
        # Simple implementation that processes invoice using our tools
        context = ActionContext(self.generate_response)
        
        # Extract invoice data using JSON
        schema = {
            "type": "object",
            "properties": {
                "vendor": {"type": "string"},
                "amount": {"type": "number"},
                "items": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"}
            }
        }
        
        extracted_data = prompt_llm_for_json(
            context, 
            schema, 
            f"Extract key details and create a summary from this invoice:\n{prompt}"
        )
        
        # Categorize the expenditure
        category = categorize_expenditure(context, extracted_data.get('summary', 'Invoice processing'))
        
        # Check purchasing rules (simplified)
        invoice_data = {
            "vendor": extracted_data.get('vendor'),
            "amount": extracted_data.get('amount'),
            "items": extracted_data.get('items', [])
        }
        
        try:
            compliance = check_purchasing_rules(context, invoice_data)
        except:
            compliance = {"compliant": True, "issues": "No specific rules to check"}
        
        return {
            "extracted_data": extracted_data,
            "category": category,
            "compliance": compliance,
            "status": "processed"
        }

def register_tool(tags=None):
    def decorator(func):
        return func
    return decorator

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set.")





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



def create_simple_llm_function():
    def generate_response_func(prompt: Prompt):
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=prompt.messages,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    return generate_response_func






def create_invoice_agent():
    action_registry = PythonActionRegistry()

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

    environment = PythonEnvironment()

    return Agent(
        goals=goals,
        agent_language=AgentFunctionCallingActionLanguage(),
        action_registry=action_registry,
        generate_response=create_simple_llm_function(),
        environment=environment
    )









# THE EXECUTION - Both simplified demo and agent demo
if __name__ == "__main__":
    # Create a simple context for testing individual functions
    llm_func = create_simple_llm_function()
    context = ActionContext(llm_func)
    
    print("=== Testing Individual Functions ===")
    # Demo: Test the JSON generation function
    print("Testing JSON Generation...")
    schema = {
        "type": "object",
        "properties": {
            "vendor": {"type": "string"},
            "amount": {"type": "number"},
            "category": {"type": "string"}
        }
    }
    
    invoice_text = """
    Invoice #4567
    Date: 2025-02-01
    Vendor: Tech Solutions Inc.
    Items: 
      - Laptop - $1,200
      - External Monitor - $300
    Total: $1,500
    """
    
    try:
        result = prompt_llm_for_json(
            context, 
            schema, 
            f"Extract key information from this invoice:\n{invoice_text}"
        )
        print("JSON Result:")
        print(json.dumps(result, indent=2))
        
        # Demo: Test categorization
        print("\nTesting Categorization...")
        category = categorize_expenditure(context, "Purchase of computer equipment for office use")
        print(f"Category: {category}")
        
        # Demo: Test full agent
        print("\n" + "="*50)
        print("=== Testing Full Invoice Agent ===")
        print("="*50)
        
        agent = create_invoice_agent()
        response = agent.run(f"Process this invoice:\n\n{invoice_text}")
        
        print("\nFINAL AGENT RESPONSE:")
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"Error running demo: {e}")
        print("Make sure you have GROQ_API_KEY set in your .env file")



