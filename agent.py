import os
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def chat_with_agent(
        user_message: str,
        *,
        pro: bool = False,
        thinking: bool = False,
        ) -> str:
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "请用简短、自然的语言回复用户，就像人们之间日常聊天一样。",
            },
            {"role": "user", "content": user_message},
        ],
        model="deepseek-v4-pro" if pro else "deepseek-v4-flash",
        extra_body={"thinking": {"type": "enabled" if thinking else "disabled"}},
        max_tokens=200,
    )
    return response
