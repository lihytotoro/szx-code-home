# 经过测试，知道了 megadiff 的处理方式
# 我们需要将 buggy_func 中出错的部分从 diff 中识别出来，然后将 bug 的部分全部注释掉（因为保证是一段，所以可以放心注释）
# 目标：直接构建形如 dummy_data 的 jsonl
import pandas as pd
from tqdm import tqdm
import jsonlines
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("/vepfs/lihy/model/codellama/CodeLlama-7b-Instruct-hf")

df_single_chunk_0 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00000-single_chunk.parquet')
df_single_chunk_1 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00001-single_chunk.parquet')
df_single_chunk_2 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00002-single_chunk.parquet')
df_single_chunk_3 = pd.read_parquet('/vepfs/lihy/dataset/megadiff-single-function/train-00003-single_chunk.parquet')

# 12609, 12802, 12722, 12563 共 5w 多条
# df_single_chunk_0 = df_0[df_0["is_single_chunk"] == True]
# df_single_chunk_1 = df_1[df_1["is_single_chunk"] == True]
# df_single_chunk_2 = df_2[df_2["is_single_chunk"] == True]
# df_single_chunk_3 = df_3[df_3["is_single_chunk"] == True]

max_token_len = 1023
user_type = "repairllama"
target_id = 40

skip_cnt = 0

# 在处理 diff 函数时，我们希望 + 号是连续的、- 号也是连续的？如果不连续（对连续的段落进行计数），就看一下例子
def parse_part_of_dataframe(df_i, conv_begin_id, user_type="repairllama"):
    global skip_cnt
    conv_id = conv_begin_id
    ans_json_list = []
    # 返回值：应当是一个包含一堆字典的列表
    for row_idx, row in tqdm(df_i.iterrows()):
        diff_info = row["diff"]
        buggy_func = row["buggy_function"]
        fixed_func = row["fixed_function"]
        
        # 都划分为一行一行的形式
        diff_lines = diff_info.splitlines()
        buggy_func_lines = buggy_func.splitlines()
        fixed_func_lines = fixed_func.splitlines()
        
        # 然后找到函数是从哪一行开始的
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
        first_diff_line_idx = diff_start_pos
        
        # 从 diff_start_pos 开始遍历，首先找到首次出现加减号的位置，记录这个行号，然后从这个行号向前遍历，找到第一个与函数第一行完全一致的行；向后遍历，找到第一个与函数最后一行完全一致的行
        # 找到六个三组起始位置（加减号分别可以不存在），对于不存在的情况，如果 + 不存在，说明是删除代码这一类的 bug（不需要增加？回复是空值，在 bug 位置之后添加 MASK 即可）；如果 - 不存在，说明是增加代码这一类的 bug（不需要删减？那么也不需要增加标记删减行的标注了！）
        for idx in range(diff_start_pos, len(diff_lines)):
            diff_line_i = diff_lines[idx]
            if len(diff_line_i) == 0:
                continue
            if diff_line_i[0] == "+" or diff_line_i[0] == "-":
                # 记录 diff 首次出现的行号
                first_diff_line_idx = idx
                break
        
        func_begin_idx = -1
        func_end_idx = -1
        
        # 向上向下遍历，找到函数首末行号
        for idx in range(first_diff_line_idx, -1, -1):
            diff_line_i = diff_lines[idx].rstrip()
            if len(diff_line_i) == 0:
                continue
            if diff_line_i[1:] == target_func_first_line:
                func_begin_idx = idx
                # 这里计算一下空白格数量，用于后面构造对话数据时，降低序列长度
                leading_white_space = len(diff_line_i[1:]) - len(diff_line_i[1:].lstrip())
                break
        for idx in range(first_diff_line_idx, len(diff_lines)):
            diff_line_i = diff_lines[idx].rstrip()
            if len(diff_line_i) == 0:
                continue
            # print(diff_line_i[1:])
            # print(target_func_last_line)
            # print(len(diff_line_i[1:]))
            # print(len(target_func_last_line))
            # print()
            if diff_line_i[1:] == target_func_last_line:
                func_end_idx = idx
                break
            
        # 然后，找出 + 和 - 的起始和终止位置（可能没有）
        add_begin_idx, add_end_idx = -1, -1
        minus_begin_idx, minus_end_idx = -1, -1
        # 第一次出现的是 + 号
        if diff_lines[first_diff_line_idx].startswith("+"):
            add_begin_idx = first_diff_line_idx
            for idx in range(first_diff_line_idx + 1, len(diff_lines)):
                diff_line_i = diff_lines[idx]
                if not diff_line_i.startswith("+"):
                    add_end_idx = idx - 1
                    break
            if add_end_idx == -1:
                add_end_idx = len(diff_lines) - 1
            minus_flag = False
            for idx in range(add_end_idx + 1, len(diff_lines)):
                if minus_flag and not diff_lines[idx].startswith("-"):
                    minus_end_idx = idx - 1
                    break
                if not minus_flag and diff_lines[idx].startswith("-"):
                    minus_flag = True
                    minus_begin_idx = idx
            if minus_flag and minus_end_idx == -1:
                minus_end_idx = len(diff_lines) - 1
            # 重要假设！！！假定两块代码是挨着的
            if minus_begin_idx > 0:
                assert minus_begin_idx == add_end_idx + 1
        # 第一次出现的是 - 号
        elif diff_lines[first_diff_line_idx].startswith("-"):
            minus_begin_idx = first_diff_line_idx
            for idx in range(first_diff_line_idx + 1, len(diff_lines)):
                diff_line_i = diff_lines[idx]
                if not diff_line_i.startswith("-"):
                    minus_end_idx = idx - 1
                    break
            if minus_end_idx == -1:
                minus_end_idx = len(diff_lines) - 1
            add_flag = False
            for idx in range(minus_end_idx + 1, len(diff_lines)):
                if add_flag and not diff_lines[idx].startswith("+"):
                    add_end_idx = idx - 1
                    break
                if not add_flag and diff_lines[idx].startswith("+"):
                    add_flag = True
                    add_begin_idx = idx
            if add_flag and add_end_idx == -1:
                add_end_idx = len(diff_lines) - 1
            if add_begin_idx > 0:
                assert add_begin_idx == minus_end_idx + 1
        else:
            # 什么情况？
            # print(first_diff_line_idx)
            raise Exception("Hey 1!")
        
        # 现在，三组期末位置都找完了，assert 一下
        if add_begin_idx > 0:
            if add_end_idx > func_end_idx:
                continue
            
            assert func_begin_idx <= add_begin_idx
            # #
            # with open("./diff.txt", "w", encoding="utf-8") as f1:
            #     for line in diff_lines:
            #         f1.write(line + "\n")
            # with open("./buggy.txt", "w", encoding="utf-8") as f2:
            #     for line in buggy_func_lines:
            #         f2.write(line + "\n")
            # with open("./fixed.txt", "w", encoding="utf-8") as f3:
            #     for line in fixed_func_lines:
            #         f3.write(line + "\n")
            # #
            # print(minus_begin_idx, minus_end_idx, add_begin_idx, add_end_idx)
            # print(buggy_func_lines[-1])            
            assert add_begin_idx <= add_end_idx
            # #
            # with open("./diff.txt", "w", encoding="utf-8") as f1:
            #     for line in diff_lines:
            #         f1.write(line + "\n")
            # with open("./buggy.txt", "w", encoding="utf-8") as f2:
            #     for line in buggy_func_lines:
            #         f2.write(line + "\n")
            # with open("./fixed.txt", "w", encoding="utf-8") as f3:
            #     for line in fixed_func_lines:
            #         f3.write(line + "\n")
            # #
            # print(func_begin_idx, func_end_idx, minus_begin_idx, minus_end_idx, add_begin_idx, add_end_idx)
            assert add_end_idx <= func_end_idx
        if minus_begin_idx > 0:
            # 特殊情况直接舍弃
            if minus_end_idx > func_end_idx:
                continue
                
            assert func_begin_idx <= minus_begin_idx
            assert minus_begin_idx <= minus_end_idx
            assert minus_end_idx <= func_end_idx
            
        # 现在得到了这个样本的六个序号，开始从 json 内层数据构造
        # 复现 repairllama 的结果时，只构造 input 和 output
        # 注意，第一次写这部分逻辑的时候似乎忘记将 bug 部分（- 号）给注释掉了
        output_code_list = []
        input_code_list = []
        
        # 在没有 - 的情况下，将 <MASK> 添加到 + 出现的行号后面
        if add_begin_idx > 0:
            for idx in range(add_begin_idx, add_end_idx + 1):
                diff_line_i = diff_lines[idx]
                output_code_list.append(diff_line_i[leading_white_space + 1:])
                
        # 接下来分两种情况处理 input：有 - 和 没有 -
        if minus_begin_idx > 0:
            for idx in range(func_begin_idx, minus_begin_idx):
                diff_line_i = diff_lines[idx]
                if not diff_line_i.startswith("+"):
                    input_code_list.append(diff_line_i[leading_white_space + 1:])
                    
            # buggy code 注释标识
            assert diff_lines[minus_begin_idx].startswith("-")
            
            # 0114 修改：如何确定注释之前的空白数量？应当比较所有行，取空白最少的
            leading_white_space_2 = int(1e6)
            leading_white_space_2_str = ""
            
            for idx in range(minus_begin_idx, minus_end_idx + 1):
                # if conv_id == 5216:
                #     print("diff_lines_i:")
                #     print(diff_lines[idx])
                #     print(len(diff_lines[idx]))
                truncated_deprecated_line_i = diff_lines[idx][leading_white_space + 1:]

                # if conv_id == 5216:
                #     print("truncated_deprecated_line_i:")
                #     print(truncated_deprecated_line_i)
                #     print(len(truncated_deprecated_line_i))
                #     print("")

                if len(truncated_deprecated_line_i.strip()) == 0:
                    continue

                whitespace_i = len(truncated_deprecated_line_i) - len(truncated_deprecated_line_i.lstrip())
                whitespace_str_i = truncated_deprecated_line_i[0:whitespace_i]
                if whitespace_i < leading_white_space_2:
                    leading_white_space_2 = whitespace_i
                    leading_white_space_2_str = whitespace_str_i
            
            # 如果因为各种原因，找 whitespace_2 失败了
            if leading_white_space_2 > 10000:
                input_code_list.append("// buggy code")
                for idx in range(minus_begin_idx, minus_end_idx + 1):
                    truncated_deprecated_line_i = diff_lines[idx][leading_white_space + 1:]
                    input_code_list.append("// " + truncated_deprecated_line_i)
                print("special conv id:", conv_id)
                skip_cnt += 1
            else:
                input_code_list.append(leading_white_space_2_str + "// buggy code")                
                # 这里逐行将 - 行注释掉
                for idx in range(minus_begin_idx, minus_end_idx + 1):
                    truncated_deprecated_line_i = diff_lines[idx][leading_white_space + 1:]
                    try:
                        input_code_list.append(leading_white_space_2_str + "// " + truncated_deprecated_line_i[leading_white_space_2:])
                    except:
                        # print(minus_begin_idx, minus_end_idx)
                        # print("")
                        # print(leading_white_space, leading_white_space_2)
                        # print("")
                        raise Exception("HEY!")
                        # with open("./tmp/check_diff.txt", "w") as f_check_1:
                        #     for line in diff_lines:
                        #         f_check_1.write(line + "\n")
                        # with open("./tmp/check_buggy.txt", "w", encoding="utf-8") as f_check_2:
                        #     for line in buggy_func_lines:
                        #         f_check_2.write(line + "\n")
                        # with open("./tmp/check_fixed.txt", "w", encoding="utf-8") as f_check_3:
                        #     for line in fixed_func_lines:
                        #         f_check_3.write(line + "\n")
                    
            
            input_code_list.append("[FILL_ME]")
            for idx in range(minus_end_idx + 1, func_end_idx + 1):
                diff_line_i = diff_lines[idx]
                if not diff_line_i.startswith("+"):
                    input_code_list.append(diff_line_i[leading_white_space + 1:])
        else:
            for idx in range(func_begin_idx, add_begin_idx):
                diff_line_i = diff_lines[idx]
                assert not diff_line_i[1:].startswith("+")
                input_code_list.append(diff_line_i[leading_white_space + 1:])
            input_code_list.append("[FILL_ME]")
            for idx in range(add_end_idx + 1, func_end_idx + 1):
                diff_line_i = diff_lines[idx]
                assert not diff_line_i[1:].startswith("+")
                input_code_list.append(diff_line_i[leading_white_space + 1:])
                
        # 获得了填好的 IR 和 OR
        input_prompt = "The following java function contains a buggy chunk, in which the buggy lines(if exists) are commented out by double slashes. Please provide the correct code at the [FILL_ME] location.\n"
        input_code = "\n".join(input_code_list)
        output_code = "\n".join(output_code_list)
        
        # 在这里，验证一下 tokenize 之后长度会不会超限
        try:
            tokenized_input = tokenizer.tokenize(input_prompt + input_code)
        except:
            with open("./temp_output.txt", "w", encoding="utf-8") as f:
                f.write(input_prompt + input_code)
            exit()
        tokenized_output = tokenizer.tokenize(output_code)
        
        if len(tokenized_input) > max_token_len or len(tokenized_output) > max_token_len:
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
                    f4.write(input_prompt)
                    f4.write(input_code)
                with open("./tmp/output.txt", "w", encoding="utf-8") as f5:
                    f5.write(output_code)
            conv_id += 1
            ans_json_list.append({"input":input_prompt + input_code, "output":output_code})

        elif user_type == "firefly":
            conversation = [{"human": input_prompt + input_code, "assistant": output_code}]
            conversation_id = conv_id
            conv_id += 1
            dataset = "MegaDiff"
            
            json_sample = {"conversation_id": conversation_id, "category": "Brainstorming", "conversation": conversation, "dataset": dataset}
            ans_json_list.append(json_sample)
        
    return ans_json_list, conv_id
            
        
js_list_0, conv_end_id_0 = parse_part_of_dataframe(df_single_chunk_0, 1)
print("passed 1!")
js_list_1, conv_end_id_1 = parse_part_of_dataframe(df_single_chunk_1, conv_end_id_0)
print("passed 2!")
js_list_2, conv_end_id_2 = parse_part_of_dataframe(df_single_chunk_2, conv_end_id_1)
print("passed 3!")
js_list_3, conv_end_id_3 = parse_part_of_dataframe(df_single_chunk_3, conv_end_id_2)
print("passed 4!")

if user_type == "repairllama":
    with jsonlines.open("./output/finetuning_conversation_data_1024_repairllama.jsonl", "w") as f_jsonl:
        for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
            for js_sample in js_list:
                f_jsonl.write(js_sample)
    # with jsonlines.open("../../github-proj/Firefly/data/finetuning_conversation_data.jsonl_1024", "w") as f_jsonl:
    #     for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
    #         for js_sample in js_list:
    #             f_jsonl.write(js_sample)
elif user_type == "firefly":
    with jsonlines.open("./finetuning_conversation_data_1024.jsonl", "w") as f_jsonl:
        for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
            for js_sample in js_list:
                f_jsonl.write(js_sample)
    with jsonlines.open("../../github-proj/Firefly/data/finetuning_conversation_data.jsonl_1024", "w") as f_jsonl:
        for js_list in [js_list_0, js_list_1, js_list_2, js_list_3]:
            for js_sample in js_list:
                f_jsonl.write(js_sample)
else:
    print("unknown user_type!")
            
print("finish writing into jsonl file!")
print("special samples cnt:", skip_cnt)