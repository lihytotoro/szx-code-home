# 这个文件的意义在于：按照作者在邮件中回复的思路，进行数据处理

import pandas as pd
from tqdm import tqdm
import jsonlines
from transformers import AutoTokenizer

# 用于 tokenize 之后，检查长度要求
tokenizer = AutoTokenizer.from_pretrained("/vepfs/lihy/model/codellama/CodeLlama-7b-Instruct-hf")

# 这里，我们重新读取所有数据（72.4k 条）
df_single_chunk_0 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00000.parquet')
df_single_chunk_1 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00001.parquet')
df_single_chunk_2 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00002.parquet')
df_single_chunk_3 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00003.parquet')

max_token_len = 1024
# user_type = "repairllama"
user_type = "firefly"
target_id = 40

# 在处理 diff 函数时，我们希望 + 号是连续的、- 号也是连续的？如果不连续（对连续的段落进行计数），就看一下例子
# df_i 表示待处理的 dataframe（一共有 4 个）
# conv_begin_id 代表对话编号（主要用于 firefly）
def parse_part_of_dataframe(df_i, conv_begin_id, user_type="repairllama"):
    # global skip_cnt
    conv_id = conv_begin_id
    # 用于存储最终结果
    ans_json_list = []
    # 返回值：应当是一个包含一堆字典的列表
    for row_idx, row in tqdm(df_i.iterrows()):
        # 三要素
        diff_info = row["diff"]
        buggy_func = row["buggy_function"]
        fixed_func = row["fixed_function"]
        special_conv_flag = False
        
        # 都划分为一行一行的形式（末尾不含 \n）
        diff_lines = diff_info.splitlines()
        buggy_func_lines = buggy_func.splitlines()
        fixed_func_lines = fixed_func.splitlines()
        
        # 然后找到函数是从哪一行开始的
        # 首先将前面无用的前缀去掉（@@ 之前的部分）
        diff_start_pos = 0
        for line in diff_lines:
            if line.startswith("@@ "):
                diff_start_pos += 1
                break
            diff_start_pos += 1
        
        # 获取函数的起始行和末尾行！注意去掉了可能存在的 \n
        target_func_first_line = buggy_func_lines[0].rstrip()
        for idx in range(len(buggy_func_lines) - 1, -1, -1):
            buggy_line_i = buggy_func_lines[idx].rstrip()
            if len(buggy_line_i) > 0:
                target_func_last_line = buggy_line_i
                break
        
        # 初始化
        # 这里是 diff 行开始的位置
        first_diff_line_idx = diff_start_pos
        
        # 从 diff_start_pos 开始遍历，首先找到首次出现加减号的位置，记录这个行号，然后从这个行号向前遍历，找到第一个与函数第一行完全一致的行；向后遍历，找到第一个与函数最后一行完全一致的行
        # 找到六个三组起始位置（加减号分别可以不存在），对于不存在的情况，如果 + 不存在，说明是删除代码这一类的 bug（不需要增加？回复是空值，在 bug 位置之后添加 MASK 即可）；如果 - 不存在，说明是增加代码这一类的 bug（不需要删减？那么也不需要增加标记删减行的标注了！）
        for idx in range(diff_start_pos, len(diff_lines)):
            diff_line_i = diff_lines[idx]
            # 忽略长度为 0 的行
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[0] == "+" or diff_line_i[0] == "-":
                # 记录 diff 首次出现的行号
                first_diff_line_idx = idx
                break
            
        # 同理，我们也可以记录一下 + 或 - 末次出现的位置
        # 以 first 和 last 为边界，即视为可能产生修改的部分（一整个 chunk）
        last_diff_line_idx = len(diff_lines) - 1
        
        for idx in range(len(diff_lines) - 1, first_diff_line_idx - 1, -1):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[0] == "+" or diff_line_i[0] == "-":
                last_diff_line_idx = idx
                break
        
        # 接下来，从 first_diff 和 last_diff 向上、向下，寻找目标函数的始末位置（在 diff_lines 中的索引）
        func_begin_idx = -1
        func_end_idx = -1
        
        # 向上向下遍历，找到函数首末行号
        for idx in range(first_diff_line_idx, -1, -1):
            diff_line_i = diff_lines[idx].rstrip()
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[1:] == target_func_first_line:
                func_begin_idx = idx
                break
        for idx in range(last_diff_line_idx, len(diff_lines)):
            diff_line_i = diff_lines[idx].rstrip()
            if len(diff_line_i.strip()) == 0:
                continue
            # diff_line 中选出的行都要去掉开头的一个空格
            if diff_line_i[1:] == target_func_last_line:
                func_end_idx = idx
                break
        
        leading_white_space = int(1e6)
        # 计算空白格
        for idx in range(func_begin_idx, func_end_idx + 1):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i.strip()) == 0:
                continue
            white_space_i = len(diff_line_i[1:]) - len(diff_line_i[1:].lstrip())
            if white_space_i < leading_white_space:
                leading_white_space = white_space_i
            
        try:
            assert func_begin_idx <= first_diff_line_idx
            assert func_end_idx >= last_diff_line_idx
        except:
            special_conv_flag = True
            # with open("./tmp/diff.txt", "w", encoding="utf-8") as f1:
            #     for line in diff_lines:
            #         f1.write(line + "\n")
            # with open("./tmp/buggy.txt", "w", encoding="utf-8") as f2:
            #     for line in buggy_func_lines:
            #         f2.write(line + "\n")
            # with open("./tmp/fixed.txt", "w", encoding="utf-8") as f3:
            #     for line in fixed_func_lines:
            #         f3.write(line + "\n")
            # with open("./tmp/input.txt", "w", encoding="utf-8") as f4:
            #     f4.write(input_prompt)
            #     f4.write(input_code)
            # with open("./tmp/output.txt", "w", encoding="utf-8") as f5:
            #     f5.write(output_code)
            # raise Exception("Hey!")
        
        if special_conv_flag:
            continue
            
        ########## 确定 buggy_chunk 以及 fixed_chunk 的范围 ##########
        # 在确定 哪一行可以加入时，引入注释行丢弃策略
        output_code_list = []
        input_code_list = []
        
        # output
        for idx in range(first_diff_line_idx, last_diff_line_idx + 1):
            diff_line_i = diff_lines[idx]
            # 选取其中开头不是 - 的行
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[1:].lstrip().startswith("//"):
                continue
            if not diff_line_i[0] == "-":
                output_code_list.append(diff_line_i[leading_white_space + 1:])

        # input 预处理：如何注释？
        # 在可疑段落中，有多少行不是新添加的？
        cnt_buggy_chunk_lines = 0
        
        for idx in range(first_diff_line_idx, last_diff_line_idx + 1):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[0] == "+":
                continue
            if diff_line_i[1:].lstrip().startswith("//"):
                continue
            cnt_buggy_chunk_lines += 1

        # input 1: prefix
        for idx in range(func_begin_idx, first_diff_line_idx):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[1:].lstrip().startswith("//"):
                continue
            input_code_list.append(diff_line_i[leading_white_space + 1:])

        if cnt_buggy_chunk_lines > 0:
            input_code_list.append("// buggy code")
        for idx in range(first_diff_line_idx, last_diff_line_idx + 1):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[0] == "+":
                continue
            if diff_line_i[1:].lstrip().startswith("//"):
                continue
            truncated_deprecated_line_i = diff_line_i[leading_white_space + 1:]
            input_code_list.append("//" + truncated_deprecated_line_i)
                
        # input 4: <FILL_ME> MASK
        input_code_list.append("<FILL_ME>")
        
        # input 5: suffix
        for idx in range(last_diff_line_idx + 1, func_end_idx + 1):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i.strip()) == 0:
                continue
            if diff_line_i[1:].lstrip().startswith("//"):
                continue
            input_code_list.append(diff_line_i[leading_white_space + 1:])
                
        # 获得了填好的 IR 和 OR
        # input_prompt = "The following java function contains a buggy chunk, in which the buggy lines are commented out by double slashes. Please generate the correct code to replace the [FILL_ME] token.\n"
        input_code = "\n".join(input_code_list)
        output_code = "\n".join(output_code_list)
        
        # 在这里，验证一下 tokenize 之后长度会不会超限
        try:
            # tokenized_input = tokenizer.tokenize(input_prompt + input_code)
            tokenized_input = tokenizer.tokenize(input_code)
        except:
            with open("./temp_output.txt", "w", encoding="utf-8") as f:
                # f.write(input_prompt + input_code)
                f.write(input_code)
            exit()
        tokenized_output = tokenizer.tokenize(output_code)
        
        if len(tokenized_input) + len(tokenized_output) > max_token_len:
            continue
        
        if user_type == "repairllama":
            # 为了对比输出的 input、output 格式是否正确，挑选特定的 conv_id，对比 input、output、diff、buggy、fixed
            if conv_id == target_id:
                with open("./tmp/diff.txt", "w", encoding="utf-8") as f1:
                    for line in diff_lines:
                        f1.write(line + "\n")
                with open("./tmp/buggy.txt", "w", encoding="utf-8") as f2:
                    for line in buggy_func_lines:
                        f2.write(line + "\n")
                with open("./tmp/fixed.txt", "w", encoding="utf-8") as f3:
                    for line in fixed_func_lines:
                        f3.write(line + "\n")
                with open("./tmp/input.txt", "w", encoding="utf-8") as f4:
                    # f4.write(input_prompt)
                    f4.write(input_code)
                with open("./tmp/output.txt", "w", encoding="utf-8") as f5:
                    f5.write(output_code)
                # exit()
            # if special_conv_flag:
            #     print(func_begin_idx, func_end_idx, first_diff_line_idx, last_diff_line_idx, leading_white_space_2)
            #     raise Exception("Hey!")
            conv_id += 1
            # ans_json_list.append({"input":input_prompt + input_code, "output":output_code})
            ans_json_list.append({"input":input_code, "output":output_code})

        elif user_type == "firefly":
            # conversation = [{"human": input_prompt + input_code, "assistant": output_code}]
            conversation = [{"human": input_code, "assistant": output_code}]
            conversation_id = conv_id
            conv_id += 1
            dataset = "MegaDiff"
            
            json_sample = {"conversation_id": conversation_id, "category": "Brainstorming", "conversation": conversation, "dataset": dataset}
            ans_json_list.append(json_sample)
        
    return ans_json_list, conv_id
            
        
js_list_0, conv_end_id_0 = parse_part_of_dataframe(df_single_chunk_0, 1, user_type=user_type)
print("passed 1!")
js_list_1, conv_end_id_1 = parse_part_of_dataframe(df_single_chunk_1, conv_end_id_0, user_type=user_type)
print("passed 2!")
js_list_2, conv_end_id_2 = parse_part_of_dataframe(df_single_chunk_2, conv_end_id_1, user_type=user_type)
print("passed 3!")
js_list_3, conv_end_id_3 = parse_part_of_dataframe(df_single_chunk_3, conv_end_id_2, user_type=user_type)
print("passed 4!")

if user_type == "repairllama":
    # sf: single function
    with jsonlines.open("./output/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_repairllama.jsonl", "w") as f_jsonl:
        for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
            for js_sample in js_list:
                f_jsonl.write(js_sample)
    # with jsonlines.open("../../github-proj/Firefly/data/finetuning_conversation_data.jsonl_1024", "w") as f_jsonl:
    #     for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
    #         for js_sample in js_list:
    #             f_jsonl.write(js_sample)
elif user_type == "firefly":
    with jsonlines.open("./output/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_firefly.jsonl", "w") as f_jsonl:
        for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
            for js_sample in js_list:
                f_jsonl.write(js_sample)
    with jsonlines.open("../../github-proj/Firefly/data/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_firefly.jsonl", "w") as f_jsonl:
        for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
            for js_sample in js_list:
                f_jsonl.write(js_sample)
else:
    print("unknown user_type!")
            
print("finish writing into jsonl file!")
# print("special samples cnt:", skip_cnt)