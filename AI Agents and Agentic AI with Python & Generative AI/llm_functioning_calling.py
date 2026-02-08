# Important!!!
#
# <---- Set your 'GROQ_API_KEY' as a secret over there with the "key" icon
#
#

import json
import os
from dotenv import load_dotenv
from typing import List

from litellm import completion

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")


def list_files() -> List[str]:
    """List files in the current directory."""
    return os.listdir(".")

def read_file(file_name: str) -> str:
    """Read a file's contents."""
    try:
        with open(file_name, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: {file_name} not found."
    except Exception as e:
        return f"Error: {str(e)}"


tool_functions = {
    "list_files": list_files,
    "read_file": read_file
}

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
                "properties": {"file_name": {"type": "string"}},
                "required": ["file_name"]
            }
        }
    }
]

# Our rules are simplified since we don't have to worry about getting a specific output format
agent_rules = [{
    "role": "system",
    "content": """
You are an AI agent that can perform tasks by using available tools.

If a user asks about files, documents, or content, first list the files before reading them.
"""
}]

user_task = input("What would you like me to do? ")

memory = [{"role": "user", "content": user_task}]

messages = agent_rules + memory

response = completion(
    model="groq/llama-3.3-70b-versatile",
    messages=messages,
    tools=tools,
    max_tokens=1024
)

# Extract the tool call from the response, note we don't have to parse now!
if not response.choices[0].message.tool_calls:
    print("No tool calls in response. Model output:")
    print(response.choices[0].message.content)
else:
    tool = response.choices[0].message.tool_calls[0]
    tool_name = tool.function.name
    # Handle both None and empty string cases
    tool_args_str = tool.function.arguments
    if tool_args_str is None or tool_args_str == "" or tool_args_str == "null":
        tool_args = {}
    else:
        tool_args = json.loads(tool_args_str)
        # Handle case where JSON parses to None
        if tool_args is None:
            tool_args = {}
    result = tool_functions[tool_name](**tool_args)

    print(f"Tool Name: {tool_name}")
    print(f"Tool Arguments: {tool_args}")
    print(f"Result: {result}")
    print(f"Result: {result}")