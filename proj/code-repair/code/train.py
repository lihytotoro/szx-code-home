import torch
from transformers import pipeline, AutoTokenizer
import os
import json
from tqdm import tqdm
import time

# os.environ['CUDA_VISIBLE_DEVICES'] = "1"

# starchat 路径
model_path = "/data/lihy/starchat-beta"
# buggy programs
file_path = "../QuixBugs/python_programs/"

# text_list = os.listdir(file_path)

# 这个 pipeline 是用来干嘛的？
pipe = pipeline("text-generation", model=model_path, torch_dtype=torch.bfloat16, device_map="auto")
# 获取预训练的 tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 列出目标目录下有哪些文件（bug file）
text_list = os.listdir(file_path)
result = []
total_tokens = 0
total_chars = 0
total_time = 0

# 遍历每一个错误程序？
for txt in tqdm(text_list):
    with open(file_path + txt, 'r') as f:
        text = f.read()
    # We use a variant of ChatML to format each message
    prompt_template = "<|system|>\n<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
    query = "Does this program have a bug? How to fix it ?\nIf it contains a bug, please give a corrected version of the program\n" + text
    prompt = prompt_template.format(query=query)
    # We use a special token with ID 49155 to denote ends of a turn
    
    start_time = time.time()
    # 记录 pipe 给出回应需要多长时间
    outputs = pipe(prompt, max_new_tokens=2048, do_sample=True, temperature=0.2, top_k=30, top_p=0.95,  eos_token_id=49155)
    end_time = time.time()
    
    duration = end_time - start_time
    total_time += duration
    
    # 将 output 中生成的 generated_text 转换成 token 格式
    tokens = tokenizer.tokenize(outputs[0]['generated_text'])
    total_tokens += len(tokens)
    chars_num = sum(len(word) for word in outputs[0]['generated_text'].split())
    total_chars += chars_num
    tokens_per_sec = len(tokens) / duration
    chars_per_sec = chars_num / duration
    
    # 最终，result 中返回的结果是一个字典，文件名-整体的问答文本；tokens_per_sec-平均每秒生成多少个token；chars_per_sec-平均每秒生成多少个char
    result.append({txt: outputs[0]['generated_text'], 'tokens_per_sec': tokens_per_sec, 'chars_per_sec': chars_per_sec})

# 这两个是最终报告中应当输出的结果
# token 总数 / 总时长
avg_token_speed = total_tokens / total_time
# char 总数 / 总时长
avg_char_speed = total_chars / total_time

result.append({'avg_token_speed': avg_token_speed, 'avg_char_speed': avg_char_speed})

json.dump(result, open('../output/result_quixbugs.json', 'w'))