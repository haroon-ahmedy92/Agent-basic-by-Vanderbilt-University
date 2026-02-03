import os
import re
from litellm import completion


os.environ["GROQ_API_KEY"] = "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"

MODEL = "groq/llama-3.3-70b-versatile"
SYSTEM_PROMPT = """
You are a senior Python developer.
Always return valid Python code inside triple backticks.
Do not include explanations outside the code block unless explicitly asked.
"""

def call_llm(messages):
    response = completion(
        model=MODEL,
        messages=messages,
        temperature=0.2
    )
    return response["choices"][0]["message"]["content"]

def extract_code(text):
    """Extracts Python code from triple backticks."""
    match = re.search(r"```(?:python)?(.*?)```", text, re.DOTALL)
    if not match:
        return text.strip()  # Fallback: return raw text if backticks missing
    return match.group(1).strip()

def step_1_generate_function(user_request):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Write a basic Python function for: {user_request}"}
    ]
    response = call_llm(messages)
    code = extract_code(response)
    print("\n=== STEP 1: BASIC FUNCTION ===\n")
    print(code)
    return code  

def step_2_add_documentation(code):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Add docstrings and edge cases to this code:\n\n```python\n{code}\n```"}
    ]
    response = call_llm(messages)
    documented_code = extract_code(response)
    print("\n=== STEP 2: DOCUMENTED FUNCTION ===\n")
    print(documented_code)
    return documented_code

def step_3_add_tests(documented_code):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Add unittest cases for this function:\n\n{documented_code}"}
    ]
    
    response = call_llm(messages)
    final_code = extract_code(response)
    print("\n=== STEP 3: FUNCTION + TESTS ===\n")
    print(final_code)
    return final_code

def save_to_file(code, filename="generated_function.py"):
    with open(filename, "w") as f:
        f.write(code)
    print(f"\n✅ Final code saved to {filename}")

def main():
    user_request = input("What Python function do you want to create?\n> ")

    basic_code = step_1_generate_function(user_request)
    documented_code = step_2_add_documentation(basic_code)
    final_version = step_3_add_tests(documented_code)

    save_to_file(final_version)

if __name__ == "__main__":
    main()



