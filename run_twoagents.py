import os
from agent import Agent


prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.md")
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()
agent1 = Agent(system_prompt=system_prompt, temperature=1.2)
agent2 = Agent(system_prompt=system_prompt, temperature=1.2)

if __name__ == "__main__":
    session1 = agent1.create_session()
    session2 = agent2.create_session()

    user_input = input(">>> ").strip()
    response2_text = user_input

    i = 1
    try:
        while True:
            response1_text = next(b.text for b in session1.chat(response2_text).content if b.type == "text")
            print(f"Agent1: {response1_text}")
            response2_text = next(b.text for b in session2.chat(response1_text).content if b.type == "text")
            print(f"Agent2: {response2_text}")

            i += 1
            input(f"即将进入第{i}轮，Enter继续，Ctrl+Z+Enter退出")
    except EOFError, KeyboardInterrupt:
        pass