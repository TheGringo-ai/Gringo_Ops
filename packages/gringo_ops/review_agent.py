import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def review_file(filepath):

    """Placeholder docstring for review_file."""    with open(filepath, 'r') as f:
        code = f.read()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional Python code reviewer."},
            {"role": "user", "content": f"Review this code:\n\n{code}"}
        ]
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    review_file("FredFix/core/agent.py")
