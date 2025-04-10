import os
import json
import requests
import re
from pathlib import Path

API_KEY = os.environ["TOGETHER_API_KEY"]
OUTPUT_DIR = Path("generated")

SYSTEM_PROMPT = """
You are the expert creator of a high-performance crypto site focused on "Flash USDT". Your task is to generate a set of 10 modern HTML pages...

[Keep your full system prompt here]
"""

def validate_html(content: str) -> bool:
    """Basic HTML validation"""
    return bool(re.search(r"<!DOCTYPE html>.*</html>", content, re.DOTALL))

def generate_content():
    payload = {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Generate all files including index.html"}
        ],
        "temperature": 0.7,
        "max_tokens": 10000
    }

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload  # Use json param for automatic serialization
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def save_files(content: str):
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Improved regex pattern with lookahead
    pattern = r"<!-- FILE: (.*?) -->\s*(.*?)(?=\n<!-- FILE: |</html>\s*$)"
    files = re.findall(pattern, content, re.DOTALL)
    
    if not files:
        raise ValueError("No files detected in API response")

    for filename, html_content in files:
        file_path = OUTPUT_DIR / filename.strip()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_content = f"{html_content.strip()}\n</html>"
        
        if not validate_html(full_content):
            raise ValueError(f"Invalid HTML structure in {filename}")
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_content)
            
        print(f"Generated: {file_path}")

if __name__ == "__main__":
    try:
        print("Starting generation process...")
        content = generate_content()
        save_files(content)
        
        # Copy index.html to root
        index_src = OUTPUT_DIR / "index.html"
        if index_src.exists():
            with open(index_src, "r") as src, open("index.html", "w") as dst:
                dst.write(src.read())
            print("Copied index.html to root")
            
        print("✅ Successfully generated all files")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)
