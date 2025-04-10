import os
from together import Together
from pathlib import Path

SYSTEM_PROMPT = """You are an expert crypto content writer creating SEO-optimized HTML about Flash USDT..."""

def generate_html():
    client = Together(api_key=os.getenv('TOGETHER_API_KEY'))
    
    response = client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Generate all 10 HTML files"}
        ]
    )
    
    content = response.choices[0].message.content
    Path("generated").mkdir(exist_ok=True)
    
    current_file = None
    for line in content.split('\n'):
        if line.startswith('<!-- FILE: '):
            if current_file:
                current_file.close()
            filename = line.split(' ')[2].strip('-->')
            current_file = open(filename, 'w')
        elif current_file:
            current_file.write(line + '\n')
    
    if current_file:
        current_file.close()

if __name__ == "__main__":
    generate_html()
