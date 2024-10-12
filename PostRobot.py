import json
import requests


class PostRobot:
    def __init__(self, api_key=None, proxy=None, model_name="gpt-3.5-turbo"):
        """
        Initialize the PostRobot instance.
        :param api_key: API key for OpenAI.
        :param proxy: Proxy settings, if any.
        :param model_name: Model name to be used for generating responses.
        """
        self.api_key = api_key
        self.proxy = proxy
        self.model_name = model_name
        self.role = None
        self.base_url = "https://api.openai.com/v1"

    def set_role(self, role):
        """
        Set the role for the conversation if not already set.
        :param role: Role description for the system.
        """
        if self.role is None:
            self.role = {"role": "system", "content": role}

    def set_thinking_engine(self, openai_key=None, proxy=None):
        """
        Set the API key and proxy settings.
        :param openai_key: API key for OpenAI.
        :param proxy: Proxy settings, if any.
        """
        self.api_key = openai_key
        self.proxy = proxy

    def request_chatgpt(self, parameters):
        """
        Send a request to the ChatGPT API to generate a response.
        :param parameters: Parameters for the API request.
        :return: Tuple containing a success flag and the response content.
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            response = requests.post(url, headers=headers, json=parameters, proxies=proxies)
            response.raise_for_status()
            choices = response.json().get('choices', [])
            if choices:
                return True, choices[0].get('message', {}).get('content')
            return False, "No choices returned"
        except requests.exceptions.RequestException as e:
            return False, str(e)

    def get_prompt(self, sample):
        """
        Generate a prompt from the given sample.
        :param sample: Dictionary containing 'instruction' and 'input'.
        :return: Combined prompt text.
        """
        instruction = sample.get("instruction", "")
        input_text = sample.get("input", "")
        if instruction and input_text:
            return f"{instruction}\n{input_text}"
        return instruction or input_text

    def generate(self, new_message):
        """
        Generate a response from the model based on the given message.
        :param new_message: The user's message to send to the model.
        :return: Tuple containing a success flag and the model's response.
        """
        messages = [self.role] if self.role else []
        messages.append({"role": "user", "content": new_message})
        parameters = {"model": self.model_name, "messages": messages}
        return self.request_chatgpt(parameters)