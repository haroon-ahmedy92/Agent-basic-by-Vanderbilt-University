from litellm import completion
from typing import List, Dict
import os

# API key should be set in environment variable GROQ_API_KEY

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