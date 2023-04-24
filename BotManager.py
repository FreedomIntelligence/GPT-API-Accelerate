import json
import multiprocessing
import os
from tqdm import tqdm

from PostRobot import PostRobot


class BotManager:
    def __init__(self):
        self.result_output_dir = ""
        self.api_key = None
        self.processes_num = 50
        self.proxy = None
        self.start = None
        self.end = None
        self.sample_list = []

    def set_api_key(self, api_file="api-key.txt", index=0):
        with open(api_file, encoding="utf-8", mode="r") as fr:
            lines = fr.readlines()
            api_key = lines[index].strip()
            self.api_key = api_key

    def set_proxy(self, proxy_file="proxy.txt", index=-1):
        if index == -1:
            self.proxy = None
        else:
            with open(proxy_file, encoding="utf-8", mode="r") as fr:
                lines = fr.readlines()
                proxy = lines[index].strip()
                self.proxy = proxy

    def set_result_output_dir(self, result_output_dir=None):
        if result_output_dir is None:
            if self.end is None:
                result_output_dir = str(self.start) + "_" + str(len(self.sample_list) - self.start) + "/"
            else:
                result_output_dir = str(self.start) + "_" + str(self.end) + "/"
        self.result_output_dir = result_output_dir
        if os.path.exists(self.result_output_dir):
            pass
        else:
            os.mkdir(self.result_output_dir)

    def merge_files(self, output_file_name=None):
        _, _, filenames = [i for i in os.walk(self.result_output_dir)][0]
        filenames = sorted(filenames, key=lambda x: int(x.split('.')[0]), reverse=True)
        generated_instructions = [open(os.path.join(self.result_output_dir, filename), encoding="utf-8").read() for
                                  filename
                                  in filenames]
        texts = "".join(generated_instructions)
        if output_file_name is None:
            if self.end is None:
                output_file_name = str(self.start) + "_" + str(len(self.sample_list) - self.start) + ".jsonl"
            else:
                output_file_name = str(self.start) + "_" + str(self.end) + ".jsonl"
        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(texts+"\n")

    def read_sample(self, file_name, start=0, end=None, role=None):
        result = []
        with open(file_name, "r", encoding="utf-8") as fr:
            lines = fr.readlines()
            count_number = 0
            for line in lines:
                line = line.strip()
                sample = json.loads(line)
                result.append((count_number, sample, role))
                count_number += 1
        self.start = start
        self.end = end
        if end is None:
            self.sample_list = result[start:]
        else:
            self.sample_list = result[start:end]

    def process_sample(self, sample_list):
        index = sample_list[0]
        sample = sample_list[1]
        role = sample_list[2]
        if os.path.exists(self.result_output_dir + str(index) + ".json"):
            return -1
        sample["output"] = self.get_string(sample, role)
        with open(self.result_output_dir + str(index) + ".json", mode="w", encoding="utf-8") as fw:
            json.dump(sample, fw, ensure_ascii=False)
        return index

    def get_string(self, sample, role):
        robot = PostRobot()
        robot.set_thinking_engine(self.api_key, self.proxy)
        if role is not None:
            robot.set_role(role)
        prompt = robot.get_prompt(sample)
        response = robot.generate(prompt)
        return response

    def multi_process(self):
        with multiprocessing.Pool(processes=self.processes_num) as pool:
            results = [
                pool.apply_async(self.process_sample, args=(sample,))
                for sample in self.sample_list
            ]
            for r in tqdm(results, desc="Processing samples", unit="sample"):
                r.wait()
            result_list = [r.get() for r in results]
            pool.close()
            pool.join()

    def generate_sequences(self, api_index=0, proxy_index=-1, input_file_name="input.jsonl",
                           output_file_name="output.jsonl"):
        bot_manager = BotManager()
        bot_manager.set_api_key(index=api_index)
        bot_manager.set_proxy(index=proxy_index)
        bot_manager.read_sample(file_name=input_file_name)
        bot_manager.set_result_output_dir()
        bot_manager.multi_process()
        bot_manager.merge_files(output_file_name)
