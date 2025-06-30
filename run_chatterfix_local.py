import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))
from agent_router import route_prompt

if __name__ == "__main__":
    while True:
        prompt = input("ChatterFix 💬 > ")
        if prompt.lower() in ("exit", "quit"): break
        response = route_prompt("chatterfix", prompt)
        print(f"\n🧠 {response}\n")
# deploy ping Sun Jun 29 22:12:31 CDT 2025
# final deploy poke Sun Jun 29 22:13:39 CDT 2025
# deploy trigger Sun Jun 29 22:19:08 CDT 2025
