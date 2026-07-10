from agent import chat_with_agent


if __name__ == "__main__":
    user_input = input(">>> ").strip()
    if user_input:
        response = chat_with_agent(user_input)
        print(response)