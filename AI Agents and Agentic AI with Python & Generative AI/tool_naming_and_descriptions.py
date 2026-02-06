import os
import json

class ToolRegistry:
    """A simple registry to hold tool logic and their AI-readable descriptions."""
    
    def __init__(self):
        self.tools = {}
        self.schemas = []

    def register_tool(self, name, schema, func):
        self.tools[name] = func
        self.schemas.append(schema)

# --- 1. TOOL IMPLEMENTATIONS (The Logic) ---

def list_python_files():
    """Returns a list of all Python files in the src/ directory."""
    # Ensure directory exists for the example
    if not os.path.exists("src"):
        return []
    return [f for f in os.listdir("src") if f.endswith(".py")]

def read_file(file_path):
    """Reads the content of a specified file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_doc_file(file_name, content):
    """Writes documentation to the docs/ directory."""
    if not os.path.exists("docs"):
        os.makedirs("docs")
    
    path = os.path.join("docs", file_name)
    with open(path, "w") as f:
        f.write(content)
    return f"Successfully wrote documentation to {path}"

# --- 2. TOOL SCHEMAS (The 'Brain' for the AI) ---

# Schema for reading files
READ_FILE_SCHEMA = {
    "tool_name": "read_file",
    "description": "Reads the content of a specified Python file from the src directory.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The relative path to the file, e.g., 'src/main.py'"
            }
        },
        "required": ["file_path"]
    }
}

# Schema for writing documentation
WRITE_DOC_SCHEMA = {
    "tool_name": "write_doc_file",
    "description": "Writes generated documentation to a file in the docs/ folder.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_name": { "type": "string", "description": "The name of the doc file (e.g., 'main_docs.md')" },
            "content": { "type": "string", "description": "The markdown content of the documentation." }
        },
        "required": ["file_name", "content"]
    }
}

# --- 3. EXECUTION EXAMPLE ---

if __name__ == "__main__":
    # Initialize Registry
    registry = ToolRegistry()
    registry.register_tool("read_file", READ_FILE_SCHEMA, read_file)
    registry.register_tool("write_doc_file", WRITE_DOC_SCHEMA, write_doc_file)

    print("--- Tool Schemas Loaded for AI ---")
    print(json.dumps(registry.schemas, indent=2))

    # Example of what an Agent might output (Mock AI Response)
    mock_ai_call = {
        "tool_name": "read_file",
        "args": {
            "file_path": "src/app.py"
        }
    }

    print("\n--- Executing Tool Based on AI Selection ---")
    selected_tool = mock_ai_call["tool_name"]
    arguments = mock_ai_call["args"]

    if selected_tool in registry.tools:
        # We unpack the dictionary arguments into the function
        result = registry.tools[selected_tool](**arguments)
        print(f"Result: {result}")