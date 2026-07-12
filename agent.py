import os
from anthropic import Anthropic, omit


class Session:
    def __init__(self, agent: Agent, pro=False, thinking=False, system_prompt=omit, max_tokens=1000, temperature=omit):
        """
        初始化会话。

        Parameters:
            agent (Agent): 智能体对象。
            pro (bool, default=False): 是否使用 Pro 模型。
            thinking (bool, default=False): 是否启用思考。
            system_prompt (str, optional): 系统提示。
            max_tokens (int, optional): 最大令牌数。
            temperature (float, optional): 温度参数。
        """
        self.agent = agent
        self.messages = []
        self.system_prompt = system_prompt
        self.pro = pro
        self.temperature = temperature
        self.thinking = thinking
        self.max_tokens = max_tokens

    def chat(self, user_message):
        """
        与助手进行对话。
        
        Parameters:
            user_message (str): 用户消息。
        Returns:
            str: 助手回复。
        """
        self.messages.append({"role": "user", "content": [{"type": "text", "text": user_message}]})
        
        response = self.agent.client.messages.create(
            messages=self.messages,
            system=self.system_prompt,
            model="deepseek-v4-pro" if self.pro else "deepseek-v4-flash",
            thinking={"type": "enabled" if self.thinking else "disabled"},
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        
        assistant_text = response.content[0].text
        self.messages.append({"role": "assistant", "content": [{"type": "text", "text": assistant_text}]})
        
        return response

class Agent:
    def __init__(self, system_prompt=omit, temperature=omit, api_key=None, base_url="https://api.deepseek.com/anthropic"):
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
        self.client = Anthropic(api_key=api_key or os.environ.get("DEEPSEEK_API_KEY"), base_url=base_url)
        self.sessions = []

    def create_session(self, pro=False, thinking=False, max_tokens=1000, temperature=omit):
        """
        创建会话。

        Parameters:
            pro (bool, default=False): 是否使用 Pro 模型。
            thinking (bool, default=False): 是否启用思考。
            max_tokens (int, optional): 最大令牌数。
        Returns:
            Session: 会话对象。
        """
        session = Session(
            agent=self,
            pro=pro,
            thinking=thinking,
            system_prompt=self.system_prompt,
            max_tokens=max_tokens,
            temperature=self.temperature,
        )
        self.sessions.append(session)
        return session
