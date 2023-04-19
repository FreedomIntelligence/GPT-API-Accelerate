import json
from retrying import retry
import requests


class PostRobot:
    def __init__(self):
        self.api_key = None
        self.proxy = None
        self.model_name = "gpt-3.5-turbo"
        self.role = None

    def set_role(self, role):
        if self.role is None:
            self.role = {
                "role": "system",
                "content": role,
            }

    def set_thinking_engine(self, openai_key=None, proxy=None):
        self.set_openai_key(openai_key)
        self.set_proxy(proxy)

    def set_openai_key(self, apikey):
        self.api_key = apikey

    def set_proxy(self, proxy):
        self.proxy = proxy

    @retry(wait_fixed=10000, stop_max_attempt_number=3)
    def request_chatgpt(self, parameters):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.proxy is None:
            raw_response = requests.post(url, headers=headers, json=parameters)
            response = json.loads(raw_response.content.decode("utf-8"))["choices"][0][
                "message"
            ]
        else:
            proxies = {"http": self.proxy, "https": self.proxy}
            raw_response = requests.post(
                url, headers=headers, json=parameters, proxies=proxies
            )
            response = json.loads(raw_response.content.decode("utf-8"))["choices"][0][
                "message"
            ]
        return response

    def get_prompt(self, sample):
        text = ""
        if len(sample["instruction"]) > 0 and len(sample["input"]) > 0:
            text = sample["instruction"] + "\n" + sample["input"]
        elif len(sample["instruction"]) > 0 and len(sample["input"]) == 0:
            text = sample["instruction"]
        elif len(sample["instruction"]) == 0 and len(sample["input"]) > 0:
            text = sample["input"]
        return text

    def generate(self, new_message):
        messages = []
        if self.role is not None:
            messages.append(self.role)
        messages.append({"role": "user", "content": new_message})
        parameters = {
            "model": self.model_name,
            "messages": messages
        }
        response = self.request_chatgpt(parameters)
        return response["content"]
