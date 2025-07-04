


import os
from openai import OpenAI

def review(target="FredFix/core/agent.py", supervised=False):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
    
    client = OpenAI(api_key=api_key)

    if not os.path.exists(target):
        print(f"❌ File not found: {target}")
        return

    print(f"🔍 Reviewing {target} with GPT-4...")
    
    with open(target, "r") as f:
        code = f.read()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior Python code reviewer. Be clear and concise."},
            {"role": "user", "content": f"Please review the following code:\n\n{code}"}
        ]
    )

    feedback = response.choices[0].message.content
    print("✅ GPT-4 Review:\n")
    print(feedback)

    if supervised:
        confirm = input("\nWould you like to save this review to gpt_review.log? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Review not saved.")
            return

    with open("gpt_review.log", "w") as log_file:
        log_file.write(feedback)
        print("💾 Review saved to gpt_review.log")