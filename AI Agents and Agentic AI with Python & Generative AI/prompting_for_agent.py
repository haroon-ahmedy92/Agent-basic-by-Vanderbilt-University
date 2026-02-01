from litellm import completion
from typing import List, Dict
import os

os.environ['GROQ_API_KEY'] = "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"

def generate_response(messages: List[Dict]) -> str:
    """Call LLM to get response"""
    response = completion(
        model="groq/llama-3.3-70b-versatile", 
        messages= messages,
    )
    return response.choices[0].message.content


messages = [
    {"role": "system", "content": "You are an expert software engineer that prefers functional programming."},
    {"role": "user", "content": "Write a function to swap the keys and values in a dictionary."}
]

response = generate_response(messages)
print(response)