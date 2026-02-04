# The Agent Loop
while iterations < max_iterations:

    # 1. Construct prompt: Combine agent rules with memory
    prompt = agent_rules + memory

    # 2. Generate response from LLM
    print("Agent thinking...")
    response = generate_response(prompt)
    print(f"Agent response: {response}")

    # 3. Parse response to determine action
    action = parse_action(response)

    result = "Action executed"

    if action["tool_name"] == "list_files":
        result = {"result":list_files()}
    elif action["tool_name"] == "read_file":
        result = {"result":read_file(action["args"]["file_name"])}
    elif action["tool_name"] == "error":
        result = {"error":action["args"]["message"]}
    elif action["tool_name"] == "terminate":
        print(action["args"]["message"])
        break
    else:
        result = {"error":"Unknown action: "+action["tool_name"]}

    print(f"Action result: {result}")

    # 5. Update memory with response and results
    memory.extend([
        {"role": "assistant", "content": response},
        {"role": "user", "content": json.dumps(result)}
    ])

    # 6. Check termination condition
    if action["tool_name"] == "terminate":
        break

    iterations += 1





## CONSTRUCTING THE AGENT PROMPT CONSTRUCTING 

prompt = agent_rules + memory

agent_rules = [{
    "role": "system",
    "content": """
You are an AI agent that can perform tasks by using available tools.

Available tools:
- list_files() -> List[str]: List all files in the current directory.
- read_file(file_name: str) -> str: Read the content of a file.
- terminate(message: str): End the agent loop and print a summary to the user.

If a user asks about files, list them before reading.

Every response MUST have an action.
Respond in this format:

```action
{
    "tool_name": "insert tool_name",
    "args": {...fill in any required arguments here...}
}


memory = [
    {"role": "user", "content": "What files are in this directory?"},
    {"role": "assistant", "content": "```action\n{\"tool_name\":\"list_files\",\"args\":{}}\n```"},
    {"role": "user", "content": "[\"file1.txt\", \"file2.txt\"]"}
]

"""
}]




