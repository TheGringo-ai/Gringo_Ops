from core.agent_router import route_prompt

if __name__ == "__main__":
    while True:
        prompt = input("ChatterFix 💬 > ")
        if prompt.lower() in ("exit", "quit"): break
        response = route_prompt("chatterfix", prompt)
        print(f"\n🧠 {response}\n")
