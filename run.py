import os
from agent import Agent


prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.md")
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()
agent = Agent(system_prompt=system_prompt, temperature=1.5)

if __name__ == "__main__":
    session = agent.create_session()

    while True:
        user_input = input(">>> ").strip()
        if not user_input:
            break
        
        response = session.chat(user_input)
        print(response)