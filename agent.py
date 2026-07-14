import os
from openai import OpenAI, omit


class Session:
    def __init__(self, agent: Agent, system_prompt=None, temperature=omit):
        """
        初始化会话。

        Parameters:
            agent (Agent): 智能体对象。
            system_prompt (str, optional): 系统提示。
            temperature (float, optional): 温度参数。
        """
        self.agent = agent
        self.messages = []
        if system_prompt is not None:
            self.messages.append({"role": "system", "content": system_prompt})
        self.temperature = temperature

    def chat(self, user_message, pro=False, thinking=False):
        """
        与助手进行对话。

        Parameters:
            user_message (str): 用户消息。
            pro (bool, default=False): 是否使用 Pro 模型。
            thinking (bool, default=False): 是否启用思考。
        Returns:
            openai.types.chat.ChatCompletion: 助手回复。
        """
        self.messages.append({"role": "user", "content": user_message})

        response = self.agent.client.chat.completions.create(
            messages=self.messages,
            model="deepseek-v4-pro" if pro else "deepseek-v4-flash",
            temperature=self.temperature,
            extra_body={"thinking": {"type": "enabled" if thinking else "disabled"}},
        )

        self.messages.append(response.choices[0].message)

        return response


class Agent:
    def __init__(self, system_prompt=None, temperature=omit, api_key=None, base_url="https://api.deepseek.com"):
        """
        初始化智能体。

        Parameters:
            system_prompt (str, optional): 系统提示。
            temperature (float, optional): 温度参数。
            api_key (str, optional): Deepseek API 密钥。
            base_url (str, optional): Deepseek API 基础 URL。
        """
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key or os.environ.get("DEEPSEEK_API_KEY"), base_url=base_url)
        self.sessions = []

    def create_session(self):
        """
        创建会话。

        Returns:
            Session: 会话对象。
        """
        session = Session(
            agent=self,
            system_prompt=self.system_prompt,
            temperature=self.temperature,
        )
        self.sessions.append(session)
        return session