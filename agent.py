import os
from anthropic import Anthropic


client = Anthropic(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/anthropic",
)


def chat_with_agent(
        user_message: str,
        *,
        pro: bool = False,
        thinking: bool = False,
        ) -> str:
    response = client.messages.create(
        messages=[
            {"role": "user", "content": [{"type": "text", "text": user_message}]}
        ],
        system="请用简短、自然的语言回复用户，就像人们之间日常聊天一样。",
        model="deepseek-v4-pro" if pro else "deepseek-v4-flash",
        thinking={"type": "enabled" if thinking else "disabled"},
        max_tokens=200,
    )
    return response
