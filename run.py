from agent import Agent


if __name__ == "__main__":
    agent = Agent(system_prompt="请用简短、自然的语言回复用户，就像人们之间日常聊天一样。")
    session = agent.create_session()

    while True:
        user_input = input(">>> ").strip()
        if not user_input:
            break
        
        response = session.chat(user_input)
        print(response)