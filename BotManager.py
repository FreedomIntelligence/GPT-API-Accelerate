import json
import multiprocessing
import os
from tqdm import tqdm
from PostRobot import PostRobot


class BotManager:
    def __init__(self, result_output_dir="", api_key=None, proxy=None, processes_num=50, model_name="", base_url=""):
        """
        Initialize the BotManager instance.
        :param result_output_dir: Directory to store the result output files.
        :param api_key: API key for OpenAI.
        :param proxy: Proxy settings, if any.
        :param processes_num: Number of processes to use for multiprocessing.
        :param model_name: Model name to be used for generating responses.
        :param base_url: Base URL for the API.
        """
        self.result_output_dir = result_output_dir
        self.api_key = api_key
        self.processes_num = processes_num
        self.proxy = proxy
        self.start = None
        self.end = None
        self.sample_list = []
        self.model_name = model_name
        self.base_url = base_url

    def set_api_key(self, api_file="api-key.txt", index=0):
        """
        Set the API key by reading from a file.
        :param api_file: File containing the API keys.
        :param index: Index of the API key to use.
        """
        try:
            with open(api_file, encoding="utf-8", mode="r") as fr:
                lines = fr.readlines()
                self.api_key = lines[index].strip()
        except (FileNotFoundError, IndexError) as e:
            raise ValueError(f"Error reading API key: {e}")

    def set_proxy(self, proxy_file="proxy.txt", index=-1):
        """
        Set the proxy settings by reading from a file.
        :param proxy_file: File containing proxy settings.
        :param index: Index of the proxy to use. Set to -1 for no proxy.
        """
        if index == -1:
            self.proxy = None
        else:
            try:
                with open(proxy_file, encoding="utf-8", mode="r") as fr:
                    lines = fr.readlines()
                    self.proxy = lines[index].strip()
            except (FileNotFoundError, IndexError) as e:
                raise ValueError(f"Error reading proxy: {e}")

    def set_model(self, model_file="model.txt", index=0):
        """
        Set the model name by reading from a file.
        :param model_file: File containing model names.
        :param index: Index of the model to use.
        """
        try:
            with open(model_file, encoding="utf-8", mode="r") as fr:
                lines = fr.readlines()
                self.model_name = lines[index].strip()
        except (FileNotFoundError, IndexError) as e:
            raise ValueError(f"Error reading model name: {e}")

    def set_base_url(self, base_url_file="base-url.txt", index=0):
        """
        Set the base URL by reading from a file.
        :param base_url_file: File containing base URLs.
        :param index: Index of the base URL to use.
        """
        try:
            with open(base_url_file, encoding="utf-8", mode="r") as fr:
                lines = fr.readlines()
                self.base_url = lines[index].strip()
        except (FileNotFoundError, IndexError) as e:
            raise ValueError(f"Error reading base URL: {e}")

    def set_result_output_dir(self, result_output_dir=None):
        """
        Set the directory for storing output results.
        :param result_output_dir: Directory path for storing results.
        """
        if result_output_dir is None:
            if self.end is None:
                result_output_dir = f"{self.start}_{len(self.sample_list) - self.start}/"
            else:
                result_output_dir = f"{self.start}_{self.end}/"
        self.result_output_dir = result_output_dir

        if not os.path.exists(self.result_output_dir):
            os.makedirs(self.result_output_dir)

    def merge_files(self, output_file_name=None):
        """
        Merge all individual output files into a single file.
        :param output_file_name: Name of the output file.
        """
        try:
            _, _, filenames = next(os.walk(self.result_output_dir))
            filenames = sorted(filenames, key=lambda x: int(x.split('.')[0]), reverse=True)
            generated_instructions = [
                open(os.path.join(self.result_output_dir, filename), encoding="utf-8").read()
                for filename in filenames
            ]
            texts = "\n".join(generated_instructions)

            if output_file_name is None:
                if self.end is None:
                    output_file_name = f"{self.start}_{len(self.sample_list) - self.start}.jsonl"
                else:
                    output_file_name = f"{self.start}_{self.end}.jsonl"

            with open(output_file_name, "w", encoding="utf-8") as f:
                f.write(texts)
        except Exception as e:
            raise ValueError(f"Error merging files: {e}")

    def read_sample(self, file_name, start=0, end=None, role=None):
        """
        Read samples from a file and store them in a list.
        :param file_name: Name of the input file.
        :param start: Starting index for reading samples.
        :param end: Ending index for reading samples.
        :param role: Role to assign to the PostRobot.
        """
        try:
            result = []
            with open(file_name, "r", encoding="utf-8") as fr:
                lines = fr.readlines()
                for count_number, line in enumerate(lines):
                    sample = json.loads(line.strip())
                    result.append((count_number, sample, role))

            self.start = start
            self.end = end
            self.sample_list = result[start:] if end is None else result[start:end]
        except FileNotFoundError as e:
            raise ValueError(f"Error reading samples: {e}")

    def process_sample(self, sample_tuple):
        """
        Process a single sample by generating an output and saving it.
        :param sample_tuple: Tuple containing index, sample, and role.
        :return: Index of the processed sample or -1 if already processed.
        """
        index, sample, role = sample_tuple
        output_file_path = os.path.join(self.result_output_dir, f"{index}.json")
        if os.path.exists(output_file_path):
            return -1

        try:
            sample["output"] = self.get_string(sample, role)
            with open(output_file_path, mode="w", encoding="utf-8") as fw:
                json.dump(sample, fw, ensure_ascii=False)
            return index
        except Exception as e:
            raise ValueError(f"Error processing sample {index}: {e}")

    def get_string(self, sample, role):
        """
        Generate a response string using PostRobot.
        :param sample: Sample data to generate a response for.
        :param role: Role to assign to the PostRobot.
        :return: Generated response.
        """
        robot = PostRobot(api_key=self.api_key, proxy=self.proxy, model_name=self.model_name)
        robot.base_url = self.base_url
        if role is not None:
            robot.set_role(role)
        prompt = robot.get_prompt(sample)
        _, response = robot.generate(prompt)
        return response

    def multi_process(self):
        """
        Use multiprocessing to process samples in parallel.
        """
        try:
            with multiprocessing.Pool(processes=self.processes_num) as pool:
                results = [
                    pool.apply_async(self.process_sample, args=(sample,))
                    for sample in self.sample_list
                ]
                for r in tqdm(results, desc="Processing samples", unit="sample"):
                    r.wait()
                pool.close()
                pool.join()
        except Exception as e:
            raise ValueError(f"Error during multiprocessing: {e}")

    def generate_sequences(self, api_index=0, proxy_index=-1, model_index=0, base_url_index=0,
                           input_file_name="input.jsonl", output_file_name="output.jsonl"):
        """
        Generate sequences by reading samples, processing them, and merging outputs.
        :param api_index: Index of the API key to use.
        :param proxy_index: Index of the proxy to use.
        :param model_index: Index of the model to use.
        :param base_url_index: Index of the base URL to use.
        :param input_file_name: Name of the input file containing samples.
        :param output_file_name: Name of the final merged output file.
        """
        try:
            self.set_api_key(index=api_index)
            self.set_proxy(index=proxy_index)
            self.set_model(index=model_index)
            self.set_base_url(index=base_url_index)
            self.read_sample(file_name=input_file_name)
            self.set_result_output_dir()
            self.multi_process()
            self.merge_files(output_file_name)
        except ValueError as e:
            raise ValueError(f"Error generating sequences: {e}")
