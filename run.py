from agent import chat_with_agent


def main():
    user_input = input(">>> ").strip()
    if user_input:
        response = chat_with_agent(user_input)
        print(response)


if __name__ == "__main__":
    main()
