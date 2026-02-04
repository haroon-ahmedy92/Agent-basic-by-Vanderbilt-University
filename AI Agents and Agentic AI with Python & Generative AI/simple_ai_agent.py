import json
import re

# ==========================================
# 1. TOOL DEFINITIONS (The Agent's "Hands")
# ==========================================
def list_files():
    return ["report.pdf", "data.csv", "notes.txt"]

def read_file(file_name):
    files = {"notes.txt": "Meeting minutes: Project is on track."}
    return files.get(file_name, "Error: File not found.")

# ==========================================
# 2. THE AGENT CLASS (The Agent's "Brain")
# ==========================================
class SimpleAgent:
    def __init__(self, max_iterations=5):
        self.max_iterations = max_iterations
        self.iterations = 0
        self.memory = []
        self.system_rules = {
            "role": "system",
            "content": (
                "You are a file assistant. Use tools to answer questions.\n"
                "Tools: list_files(), read_file(file_name), terminate(message).\n"
                "Response Format: Always wrap your JSON action in ```action code blocks."
            )
        }

    def parse_action(self, response: str):
        """Extracts the JSON action from markdown code blocks."""
        try:
            # Matches content inside ```action { ... } ```
            match = re.search(r"```action\s*(\{.*?\})\s*```", response, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return {"tool_name": "error", "args": {"message": "Invalid format. Use ```action {json} ```"}}
        except json.JSONDecodeError:
            return {"tool_name": "error", "args": {"message": "Response was not valid JSON."}}

    def execute_tool(self, action):
        """Routes the LLM action to the actual Python function."""
        name = action.get("tool_name")
        args = action.get("args", {})

        if name == "list_files":
            return {"result": list_files()}
        elif name == "read_file":
            return {"result": read_file(args.get("file_name"))}
        elif name == "terminate":
            return "STOP"
        else:
            return {"error": f"Tool '{name}' not found."}

    def run(self, user_query):
        print(f"🚀 Task: {user_query}")
        self.memory.append({"role": "user", "content": user_query})

        while self.iterations < self.max_iterations:
            self.iterations += 1
            
            # Step 1: Think (Combine rules + history)
            prompt = [self.system_rules] + self.memory
            print(f"\n[Iteration {self.iterations}] Thinking...")
            
            # MOCK LLM CALL (Replace with actual LLM API call)
            # In a real scenario, this 'response' comes from GPT/Gemini
            response = '```action {"tool_name": "list_files", "args": {}} ```' if self.iterations == 1 else \
                       '```action {"tool_name": "terminate", "args": {"message": "I found the files."}} ```'
            
            # Step 2: Parse
            action = self.parse_action(response)
            print(f"🤖 Action: {action['tool_name']}")

            # Step 3: Execute & Check Termination
            result = self.execute_tool(action)
            
            if result == "STOP":
                print(f"🏁 Finished: {action['args'].get('message')}")
                break

            # Step 4: Remember
            self.memory.append({"role": "assistant", "content": response})
            self.memory.append({"role": "user", "content": json.dumps(result)})
            print(f"🔧 Result: {result}")

# ==========================================
# 3. EXECUTION
# ==========================================
if __name__ == "__main__":
    agent = SimpleAgent()
    agent.run("What files are in this directory?")