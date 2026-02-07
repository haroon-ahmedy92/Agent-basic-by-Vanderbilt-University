import os
import json
from typing import List
from litellm import completion # Using LiteLLM for universal API support

# --- 1. TOOL DEFINITIONS (The Business Logic) ---

def list_files() -> List[str]:
    """Returns a list of files in the current directory."""
    return os.listdir(".")

def read_file(file_name: str) -> str:
    """Reads the content of a specified file."""
    try:
        with open(file_name, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: {file_name} not found."
    except Exception as e:
        return f"Error: {str(e)}"

# --- 2. FUNCTION REGISTRY ---
# Maps the string name the AI sees to the actual Python function
tool_functions = {
    "list_files": list_files,
    "read_file": read_file
}

# --- 3. TOOL SCHEMAS (The AI's "Eyes") ---
# This is what we send to the LLM so it knows WHAT it can call.
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Returns a list of files in the directory.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specified file in the directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to read, e.g., 'data.txt'"
                    }
                },
                "required": ["file_name"]
            }
        }
    }
]

# --- 4. AGENT EXECUTION LOGIC ---

def run_agent(user_prompt: str):
    # System instructions define the 'personality' and 'strategy'
    messages = [
        {
            "role": "system", 
            "content": "You are a file-manager agent. Always list files before reading them."
        },
        {
            "role": "user", 
            "content": user_prompt
        }
    ]

    # API Call: We pass the 'tools' list here
    response = completion(
        model="openai/gpt-4o", # Or any model supporting function calling
        messages=messages,
        tools=tools
    )

    # 5. HANDLING THE RESPONSE
    message = response.choices[0].message
    
    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            print(f"\n[AI Action] Calling: {tool_name}")
            print(f"[Arguments] {tool_args}")
            
            # Execute the actual Python code
            executable_func = tool_functions[tool_name]
            result = executable_func(**tool_args)
            
            print(f"[Result] {result}")
    else:
        print(f"\n[AI Response] {message.content}")

if __name__ == "__main__":
    # Example Task
    # run_agent("What is inside the requirements.txt file?")
    print("Agent script ready. Ensure OPENAI_API_KEY is set in your environment.")