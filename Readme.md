# 📌GPT-API-Accelerate

The "GPT-API-Accelerate" project provides a set of Python classes for accelerating the process of generating responses to prompts using the OpenAI GPT-3.5 API. It includes the following classes:

`BotManager`: A class for processing a list of input samples and generating responses using the PostRobot class in parallel.

`PostRobot`: A class for generating responses to prompts using the OpenAI GPT-3.5 API.

`demo_main`: It is a simple demo to run this project.

-------
# 🚀Update
📢[version 0.0.2] Now, we support to use the third-party API if you have. Just add the url into base-url.txt to replace the official url.

📢[version 0.0.1] We release GPT-API-Accelerate.

# 📖 How to run this project?

1. pip install -r requirements.txt
2. type your chatgpt api key into api-key.txt
3. type your proxy ip and port into proxy.txt if you want to use it.
4. have an input jsonl file with the instruction and input (input.jsonl is an example).
5. run the demo_main.py is ok if you do not have any special needs.
6. refer to the following guideline to build your process. 

Note: You may notice the result from ChatGPT is saved file by file. It is necessary for multiple processes and also convenient for resuming. It means even if the program shut down by errors or other unexpected reasons, you can restart it again and easily continue to generate the answer by ChatGPT without any other operation because the target file will be skipped if it has already been processed. 

# 📋 Detail of each class

## BotManager Class

The BotManager class is used to generate responses for a list of input samples using an API key and a proxy server. It supports parallel processing of multiple samples, and allows you to customize the output directory and file names.

**Usage**

To use the BotManager class, first create an instance of the class:
```python
bot_manager = BotManager()
```
**Set API Key**

To set the API key, call the set_api_key method with the path to the file containing the API key and the index of the API key to use (if there are multiple keys in the file):
```python
bot_manager.set_api_key(api_file="api-key.txt", index=0)
```

**Set Proxy Server**

To set the proxy server, call the set_proxy method with the path to the file containing the proxy server information and the index of the proxy server to use (if there are multiple servers in the file):
```python
bot_manager.set_proxy(proxy_file="proxy.txt", index=0)
```
If you don't want to use a proxy server, you can set the index parameter to -1:
```python
bot_manager.set_proxy(index=-1)
```

**Set Model Name**

To set the model name, call the set_model method with the path to the file containing the model name and the index of the model name to use (if there are multiple model names in the file):
```python
bot_manager.set_model(api_file="model.txt", index=0)
```

**Set Base URL**

To set the base URL, call the set_model method with the path to the file containing the base URL and the index of the base URL to use (if there are multiple base URLs in the file):
```python
bot_manager.set_base_url(api_file="base-url.txt", index=0)
```

**Read Input Samples**

To read the input samples from a file, call the read_sample method with the path to the file and the start and end indices of the samples to read (if you don't specify an end index, all samples from the start index to the end of the file will be read):
```python
bot_manager.read_sample(file_name="input.jsonl", start=0, end=200)
```
You can also specify a role for the samples by passing it as the role parameter:
```python
bot_manager.read_sample(file_name="input.jsonl", start=0, end=200, role="You are a good translator.")
```
**Set Output Directory**

To set the output directory for the generated responses, call the set_result_output_dir method with the path to the output directory:
```python
bot_manager.set_result_output_dir(result_output_dir="output/")
```
If you don't specify an output directory, the default directory name will be the starting sample number and the total number of samples.

**Generate Responses**

To generate responses for the input samples and output them to a file, call the generate_sequences method with the path to the output file:
```python
bot_manager.generate_sequences(api_index=0, proxy_index=-1, input_file_name="input.jsonl", output_file_name="output.jsonl")
```
You can also specify which API key and proxy server to use by passing their indices as the api_index and proxy_index parameters, respectively.

**Merge Output Files**

To merge all of the output files into a single file, call the merge_files method with the path to the output file:
```python
bot_manager.merge_files(output_file_name="output.jsonl")

```
If you don't specify an output file name, the default name will be the starting sample number and the total number of samples.

**Process Samples in Parallel**

To process all of the samples in parallel, call the multi_process method:
```python
bot_manager.multi_process()
```

