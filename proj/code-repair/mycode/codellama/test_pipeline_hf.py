# 模仿 code/train.py，基于错误版本的代码进行纠错！
# TODO: 有的错误实际上看起来是找出来了，但是输出的时候不完整，可能是 max_token_len 等参数的问题
import torch
from transformers import pipeline, AutoTokenizer
import os
import json
from tqdm import tqdm
import time

# os.environ['CUDA_VISIBLE_DEVICES'] = "0,1"

# starchat 路径
model_path = "/data/lihy/codellama/CodeLlama-7b-Instruct-hf"
# model_path = "/data/lihy/starchat-beta"

# 这个 pipeline 是用来干嘛的？
pipe = pipeline("text-generation", model=model_path, torch_dtype=torch.float16, device_map="auto")
# 获取预训练的 tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

buggy_text = '''def bitcount(n):
    count = 0
    while n:
        n ^= n - 1
        count += 1
    return count'''

# prompt_template = "<|system|>\n<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
query = "Does this program have a bug? How to fix it ?\nIf it contains a bug, please give a corrected version of the program\n" + buggy_text
prompt = query

outputs = pipe(prompt, max_new_tokens=2048, do_sample=True, temperature=0.2, top_k=30, top_p=0.95, eos_token_id=tokenizer.eos_token_id)

print("---------- output ----------")
print(outputs[0]['generated_text'])

exit()

# 分别读取 src.patch 文件！
# text 是指项目名称
for path, text in tqdm(zip(path_list, text_list)):
    if text in ["Chart", "Cli", "Closure", "Codec", "Collections", "Compress", "Csv", "Gson", "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath"]:
        print("Skipping project %s" % text)
        continue
    # 某个含有 bug 的项目
    print("processing path", path)
    
    src_file_list = os.listdir(path)
    src_code_list = [src_file[:-10] for src_file in src_file_list if src_file.endswith(".src.patch")]
    src_path_list = [(path + src_file) for src_file in src_file_list if src_file.endswith(".src.patch")]
    
    for src_path, src_code in zip(src_path_list, src_code_list):
        if text == "Lang":
            val_src_code = int(src_code)
            if (val_src_code > 0 and val_src_code < 3) or (val_src_code > 9 and val_src_code < 25):
                print("\tin project Lang, skipping bug number", src_code)
                continue
        print("\tprocessing file", src_path)
        # 读取 src.patch 文件，提取所有不带 - 号的行
        buggy_text = ""
        with open(src_path, 'r') as f:
            lines = f.readlines()
            # 确定一下，是否是单函数的情况？
            # 这里直接先粗暴地用 diff 的数目进行统计
            cnt_diff = 0
            for line in lines:
                if line.startswith("diff"):
                    cnt_diff += 1
            if cnt_diff > 1:
                # 获取有用的相对路径
                wrong_src_path = src_path[len(base_file_path):]
                print("\tbug with more than one change to fix:", wrong_src_path)
                multi_change_bugs.append(wrong_src_path)
                continue
            
            # 也可以统计有多少个函数？
            # TODO: 统计文件路径、函数名称，以此确定这些 bug 是否都出现在同一个地方
            
            # 首先确定有 @@ 行的 idx
            atat_idx = 0
            while not lines[atat_idx].startswith("@@"):
                atat_idx += 1
            # 舍弃前面的行，第5行进行特殊处理
            other_lines = lines[atat_idx+1:]
            start_line = lines[atat_idx]
            # 注意，这一句不一定能 split 出这么多部分#
            # 以及！有 @@ 的不一定是第 4 行
            try:
                first_buggy_line = start_line.split("@@")
                if len(first_buggy_line) >= 2:
                    first_buggy_line = first_buggy_line[2]
                else:
                    first_buggy_line = ""
                if first_buggy_line != "\n":
                    buggy_text += first_buggy_line[1:]
                for line in other_lines:
                    if line[0] == "-":
                        continue
                    else:
                        buggy_text += line[1:]
            except:
                # 输出错误文件信息
                print("\tin except:", src_path)
                trigger_exception_bugs.append(src_path[len(base_file_path):])
                    
        # We use a variant of ChatML to format each message
        prompt_template = "<|system|>\n<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
        query = "Does this program have a bug? How to fix it ?\nIf it contains a bug, please give a corrected version of the program\n" + buggy_text
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
        target_filename = src_code + ".src.patch"
        save_path = output_path + text + "/" + src_code + ".json"
        # 除了需要记录平均生成速度，还需要记录这一条所需时间、token 数目、char 数目
        ans_dict = {target_filename: outputs[0]['generated_text'], 'tokens_per_sec': tokens_per_sec, 'chars_per_sec': chars_per_sec, \
                'tokens_num':len(tokens), 'chars_num':chars_num, 'duration':duration}
        
        # 这里我感觉需要改一下，不是把所有程序的回答合并到一起，而是分别输出到不同的目录下不同的文件中
        with open(save_path, 'w') as fjs:
            json.dump(ans_dict, fjs)

# 这两个是最终报告中应当输出的结果
# token 总数 / 总时长
avg_token_speed = total_tokens / total_time
# char 总数 / 总时长
avg_char_speed = total_chars / total_time

total_ans_dict = {'avg_token_speed': avg_token_speed, 'avg_char_speed': avg_char_speed}
total_save_path = output_path + "total_result.json"

multi_change_path = output_path + "multi_change.txt"
trigger_exception_path = output_path + "triggrt_exception.txt"

with open(total_save_path, "w") as fjt:
    json.dump(total_ans_dict, fjt)

# 将未能处理的文件路径 以及 引起错误的文件路径记录下来
with open(multi_change_path, "w") as fmc:
    for mcb in multi_change_bugs:
        fmc.write(mcb + "\n")
        
with open(trigger_exception_path, "w") as fte:
    for teb in trigger_exception_bugs:
        fte.write(teb + "\n")