import json
import requests


class PostRobot:
    def __init__(self):
        self.api_key = None
        self.proxy = None
        self.model_name = "gpt-3.5-turbo"
        self.role = None
        self.base_url = "https://api.chatanywhere.cn/v1"

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

    def request_chatgpt(self, parameters):
        url = self.base_url+"/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.proxy is None:
            raw_response = requests.post(url, headers=headers, json=parameters)
            response = json.loads(raw_response.content.decode("utf-8"))
            try:
                content = response["choices"][0]["message"]["content"]
                flag = True
            except:
                content = response["error"]["code"]
                flag = False
            return flag, content
        else:
            proxies = {"http": self.proxy, "https": self.proxy}
            raw_response = requests.post(
                url, headers=headers, json=parameters, proxies=proxies
            )
            response = json.loads(raw_response.content.decode("utf-8"))
            try:
                content = response["choices"][0]["message"]["content"]
                flag = True
            except:
                content = response["error"]["code"]
                flag = False
            return flag, content

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
        flag, response = self.request_chatgpt(parameters)
        return flag, response
