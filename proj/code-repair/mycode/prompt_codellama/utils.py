# 这里，我们按照论文里的说法，选取多项内容，共同构建 prompt，输入到 code-llama 大模型中
# 如何处理 system user assistant 的关系呢？
# system: Does this program have a bug?\nIf it contains a bug, please give a corrected version of the program\n
# user: 初次询问时，输入各项信息
import json
import os
import pandas as pd

single_line_code_path = "../clean_dataset/clean_LLM_repair/Defects4j/single_function_single_line_repair.json"
single_hunk_code_path = "../clean_dataset/clean_LLM_repair/Defects4j/single_function_single_hunk_repair.json"
single_func_code_path = "../clean_dataset/clean_LLM_repair/Defects4j/single_function_repair.json"

# 这里记录了所有测试信息储存的根目录
test_info_path = "../retrieve_test_info/output"

# 记录了哪些 bug 属于这一类
single_line_metadata_path = "../../defects4j/metadata/single_line_bugs.json"
single_hunk_metadata_path = "../../defects4j/metadata/single_hunk_bugs.json"
single_func_metadata_path = "../../defects4j/metadata/single_func_bugs.json"

output_reply_path = "./output"

########## 获取代码信息 ##########

# 用于获取代码相关的各项数据
def clean_parse_d4j_single_line(code_path):
    # 打开 json 文件，里面记录了每个 bug 的 prefix、suffix、buggy、fix、start、end 六项信息，最终获取的 result 是一个字典
    with open(code_path, "r") as f:
        result = json.load(f)
    # 记录清洗完成的数据
    cleaned_result = {}
    # k 是 bug 编号（Chart-1），v 是对应的内容（也是一个字典）
    for k, v in result.items():
        # 将 buggy 版本的代码按照行切分开？
        lines = v['buggy'].splitlines()
        # 这个是计算第一行左边的空白格有多少？因为原始数据不包含 \t 所以可以这样计算
        # 重新梳理一遍：这个参数的意思是——第一行缩进的空格数（应该是所有行缩进值的最小值）
        # 这样做的好处？省 token，而回填的时候需要记住应该补足多少缩进
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 按照空格数计算
        # if k == "Chart-10":
        #     print(leading_white_space)
        # cleaned_result 里面要分别记录清洗完成的数据？这里为什么把 leading white space 数目的空格给去掉了？
        cleaned_result[k] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        # 接下来，获取前缀部分，同理，去掉不需要的多余空格
        lines = v["prefix"].splitlines()
        cleaned_result[k]["prefix"] = "\n".join([line[leading_white_space:] for line in lines])
        # 同理处理后缀
        lines = v["suffix"].splitlines()
        cleaned_result[k]["suffix"] = "\n".join([line[leading_white_space:] for line in lines])
        # 最后，同理处理 golden truth 部分
        lines = v['fix'].splitlines()
        # 这里的 leading_white_space 要重新计算？为啥？因为修复过后有可能变更缩进情况？
        leading_white_space_2 = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k]["fix"] = "\n".join([line[leading_white_space_2:] for line in lines])

        # 这里为什么重新获取了 buggy_line？看一下返回值：是 cleaned_result 这个字典！
        # removeprefix：移除指定前缀？
        # removesuffix：移除指定后缀？
        # 首先，移除前缀正确的部分；接下来，移除后缀正确的部分；最后，将剩余的 \n 去掉，就得到了 buggy 的代码行
        buggy_line = cleaned_result[k]["buggy"] \
            .removeprefix(cleaned_result[k]["prefix"]).removesuffix(
            cleaned_result[k]["suffix"]).replace("\n", "")
            
        # 将含有 bug 的一行存进字典中，键名为 buggy_line
        cleaned_result[k]["buggy_line"] = buggy_line
        
        # 函数的起始和末尾在原文件中的行数（左闭右闭）
        cleaned_result[k]["func_start_idx"] = int(v["start"])
        cleaned_result[k]["func_end_idx"] = int(v["end"])
        
        # 我认为应当记录两个缩进数据
        cleaned_result[k]["buggy_white_space"] = leading_white_space
        cleaned_result[k]["fixed_white_space"] = leading_white_space_2

    # 这个字典中包含了所有 158 个 bug 的各项信息
    return cleaned_result

def clean_parse_d4j_single_hunk(code_path):
    with open(code_path, "r") as f:
        result = json.load(f)
    # 同样，开一个字典记录 dataset 的信息
    cleaned_result = {}
    # k 是 bug 的编号（proj-id），v 是对应的各项代码（buggy、fix、start、end、prefix、suffix）
    for k, v in result.items():
        # 首先获取 buggy 版本的完整代码，按照 \n 分割
        lines = v['buggy'].splitlines()
        # 计算出所有行需要去除的多余空格数目（节省 token）
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 在 cleaned_result 里加入 buggy 部分！
        cleaned_result[k] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        lines = v["prefix"].splitlines()
        cleaned_result[k]["prefix"] = "\n".join([line[leading_white_space:] for line in lines])
        lines = v["suffix"].splitlines()
        cleaned_result[k]["suffix"] = "\n".join([line[leading_white_space:] for line in lines])
        lines = v['fix'].splitlines()
        leading_white_space_2 = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k]["fix"] = "\n".join([line[leading_white_space_2:] for line in lines])
        
        # 注意：这里搞定 fix 项（也就是 golden truth 之后，没有进行后续处理，因为不存在单行的 buggy line）
        # 是否应该处理出类似的 single hunk？
        buggy_hunk = cleaned_result[k]["buggy"] \
            .removeprefix(cleaned_result[k]["prefix"]).removesuffix(
            cleaned_result[k]["suffix"])
        buggy_hunk = buggy_hunk.removeprefix("\n").removesuffix("\n")
        cleaned_result[k]["buggy_hunk"] = buggy_hunk
        
        # 函数的起始和末尾在原文件中的行数（左闭右闭）
        cleaned_result[k]["func_start_idx"] = int(v["start"])
        cleaned_result[k]["func_end_idx"] = int(v["end"])
        
        # 我认为应当记录两个缩进数据
        cleaned_result[k]["buggy_white_space"] = leading_white_space
        cleaned_result[k]["fixed_white_space"] = leading_white_space_2
        
    return cleaned_result

def clean_parse_d4j_single_func(code_path):
    # 这里仍然是照抄作者的写法
    with open(code_path, "r") as f:
        result = json.load(f)
        
    # 记录结果
    cleaned_result = {}
    # k 为 bug 的编号（proj-id）
    # v 为 bug 对应的各种代码
    for k, v in result.items():
        lines = v['buggy'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 仍然同理记录了 buggy
        cleaned_result[k] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        lines = v['fix'].splitlines()
        leading_white_space_2 = len(lines[0]) - len(lines[0].lstrip())
        # 同理记录了 fix
        cleaned_result[k]["fix"] = "\n".join([line[leading_white_space_2:] for line in lines])
        
        # 对于 single_func 来讲，没有 prefix 以及 suffix，代码是整个函数作为整体输入到模型中的
        # 函数的起始和末尾在原文件中的行数（左闭右闭）
        cleaned_result[k]["func_start_idx"] = int(v["start"])
        cleaned_result[k]["func_end_idx"] = int(v["end"])
        
        # 我认为应当记录两个缩进数据
        cleaned_result[k]["buggy_white_space"] = leading_white_space
        cleaned_result[k]["fixed_white_space"] = leading_white_space_2
                
    return cleaned_result

########## 获取测试信息 ##########

def clean_parse_d4j_test_info_single_line(test_info_path, metadata_path):
    # 首先根据 metadata，获取 158 个目标 bug 各是哪些
    with open(metadata_path, "r", encoding="utf-8") as f_meta:
        single_line_bug_id_list = json.load(f_meta)["bug_id"]
    for special_bugs in ["Cli-40", "Lang-57", "Math-34", "Mockito-8"]:
        single_line_bug_id_list.remove(special_bugs)
    assert len(single_line_bug_id_list) == 154
    
    # 然后，根据 test_info_path 以及每个 bug 的编号（子路径），获取三项信息
    cleaned_result = {}
    
    # 遍历
    for bug_id in single_line_bug_id_list:
        proj, id = bug_id.split("-")
        test_info_total_path = os.path.join(test_info_path, proj, id)
        with open(os.path.join(test_info_total_path, "trigger_func_name.txt"), "r", encoding="utf-8") as f_func:
            lines = f_func.readlines()
            # 函数名这一项信息应该只能是单行
            assert len(lines) == 1
            test_func_name = lines[0].strip()
            cleaned_result[bug_id] = {"test_func_name":test_func_name}
        # 这个应该是 prompt_len 过长的罪魁祸首
        with open(os.path.join(test_info_total_path, "test_err_info.txt"), "r", encoding="utf-8") as f_err:
            # 因为写入的时候是 \n 分割的，因此直接逐行添加就可以了
            cnt_err_info_line = 0
            err_info = ""
            for line in f_err.readlines():
                err_info += line
                cnt_err_info_line += 1
                if cnt_err_info_line >= 2:
                    break
            # 去掉最后一位的 \n
            err_info = err_info[:-1]
            cleaned_result[bug_id]["err_info"] = err_info
        with open(os.path.join(test_info_total_path, "trigger_codes.txt"), "r", encoding="utf-8") as f_codes:
            trigger_codes = ""
            for line in f_codes.readlines():
                trigger_codes += line
            trigger_codes = trigger_codes[:-1]
            cleaned_result[bug_id]["trigger_codes"] = trigger_codes
            
    return cleaned_result, single_line_bug_id_list

def clean_parse_d4j_test_info_single_hunk(test_info_path, metadata_path):
    # 首先根据 metadata，获取 304 个目标 bug 各是哪些
    with open(metadata_path, "r", encoding="utf-8") as f_meta:
        single_hunk_bug_id_list = json.load(f_meta)["bug_id"]
    for special_bugs in ["Cli-40", "Compress-44", "Gson-16", "Jsoup-68", "Lang-57", "Math-34", "Math-45", "Math-50", "Mockito-8"]:
        single_hunk_bug_id_list.remove(special_bugs)
    assert len(single_hunk_bug_id_list) == 304
    
    # 然后，根据 test_info_path 以及每个 bug 的编号（子路径），获取三项信息
    cleaned_result = {}
    
    # 遍历
    for bug_id in single_hunk_bug_id_list:
        proj, id = bug_id.split("-")
        test_info_total_path = os.path.join(test_info_path, proj, id)
        with open(os.path.join(test_info_total_path, "trigger_func_name.txt"), "r", encoding="utf-8") as f_func:
            lines = f_func.readlines()
            # 函数名这一项信息应该只能是单行
            assert len(lines) == 1
            test_func_name = lines[0].strip()
            cleaned_result[bug_id] = {"test_func_name":test_func_name}
        # 这个应该是 prompt_len 过长的罪魁祸首
        with open(os.path.join(test_info_total_path, "test_err_info.txt"), "r", encoding="utf-8") as f_err:
            # 因为写入的时候是 \n 分割的，因此直接逐行添加就可以了
            cnt_err_info_line = 0
            err_info = ""
            for line in f_err.readlines():
                err_info += line
                cnt_err_info_line += 1
                if cnt_err_info_line >= 2:
                    break
            # 去掉最后一位的 \n
            err_info = err_info[:-1]
            cleaned_result[bug_id]["err_info"] = err_info
        with open(os.path.join(test_info_total_path, "trigger_codes.txt"), "r", encoding="utf-8") as f_codes:
            trigger_codes = ""
            for line in f_codes.readlines():
                trigger_codes += line
            trigger_codes = trigger_codes[:-1]
            cleaned_result[bug_id]["trigger_codes"] = trigger_codes
            
    return cleaned_result, single_hunk_bug_id_list

# single func 情况：
def clean_parse_d4j_test_info_single_func(test_info_path, metadata_path):
    # 首先根据 metadata，获取 158 个目标 bug 各是哪些
    with open(metadata_path, "r", encoding="utf-8") as f_meta:
        single_func_bug_id_list = json.load(f_meta)["bug_id"]
    # 剔除无法正常获取信息的 bug
    for special_bugs in ["Cli-40", "Compress-28", "Compress-44", "Gson-16", "Jsoup-68", "Jsoup-85", "Lang-57", \
                            "Math-25", "Math-34", "Math-45", "Math-50", "Math-86", "Mockito-8"]:
        single_func_bug_id_list.remove(special_bugs)
    assert len(single_func_bug_id_list) == 470
    
    # 然后，根据 test_info_path 以及每个 bug 的编号（子路径），获取三项信息
    cleaned_result = {}
    
    # 遍历
    for bug_id in single_func_bug_id_list:
        proj, id = bug_id.split("-")
        test_info_total_path = os.path.join(test_info_path, proj, id)
        with open(os.path.join(test_info_total_path, "trigger_func_name.txt"), "r", encoding="utf-8") as f_func:
            lines = f_func.readlines()
            # 函数名这一项信息应该只能是单行
            assert len(lines) == 1
            test_func_name = lines[0].strip()
            cleaned_result[bug_id] = {"test_func_name":test_func_name}
        # 这个应该是 prompt_len 过长的罪魁祸首
        with open(os.path.join(test_info_total_path, "test_err_info.txt"), "r", encoding="utf-8") as f_err:
            # 因为写入的时候是 \n 分割的，因此直接逐行添加就可以了
            cnt_err_info_line = 0
            err_info = ""
            for line in f_err.readlines():
                err_info += line
                cnt_err_info_line += 1
                if cnt_err_info_line >= 2:
                    break
            # 去掉最后一位的 \n
            err_info = err_info[:-1]
            cleaned_result[bug_id]["err_info"] = err_info
        with open(os.path.join(test_info_total_path, "trigger_codes.txt"), "r", encoding="utf-8") as f_codes:
            trigger_codes = ""
            for line in f_codes.readlines():
                trigger_codes += line
            trigger_codes = trigger_codes[:-1]
            cleaned_result[bug_id]["trigger_codes"] = trigger_codes
            
    return cleaned_result, single_func_bug_id_list

########## 构建 prompt ##########

# 构建 prompt 的函数（论文中所说的 few-shot example）
def construct_initial_prompt(prefix, suffix, buggy_patch, failing_test_func, failing_test_line, test_error_info, buggy_type="line"):
    # 首先我们先来进行单行 bug 的修复
    prompt = ""
    if buggy_type == "line":
        buggy_code_prompt = "The following code contains a buggy line that has been removed."
        final_request_prompt = "Please provide the correct line at the INFILL location."
    elif buggy_type == "hunk":
        buggy_code_prompt = "The following code contains a buggy hunk that has been removed."
        final_request_prompt = "Please provide the correct hunk at the INFILL location."
    elif buggy_type == "func":
        buggy_code_prompt = "The following code contains a bug."
        final_request_prompt = "Please provide the correct version of the buggy function."
    else:
        raise Exception("Wrong Buggy Type!")
    
    if buggy_type == "line":
        buggy_line_or_hunk_prompt = "This was the original buggy line which was removed by the INFILL location:"
    if buggy_type == "hunk":
        buggy_line_or_hunk_prompt = "This was the original buggy hunk which was removed by the INFILL location:"
    
    failing_test_func_prompt = "The code fails on this test:"
    failing_test_line_prompt = "on this test line:"
    test_error_prompt = "with the following test error:"
    
    # infill 标志
    infill_symbol = ">>> [INFILL] <<<"
    
    if buggy_type in ["line", "hunk"]:
        prompt_content_list = [buggy_code_prompt, prefix, infill_symbol, suffix, buggy_line_or_hunk_prompt, buggy_patch, \
                            failing_test_func_prompt, failing_test_func, failing_test_line_prompt, failing_test_line, \
                                test_error_prompt, test_error_info, final_request_prompt]
    else:
        assert buggy_type == "func"
        prompt_content_list = [buggy_code_prompt, buggy_patch, \
                            failing_test_func_prompt, failing_test_func, failing_test_line_prompt, failing_test_line, \
                                test_error_prompt, test_error_info, final_request_prompt]
    
    prompt = "\n".join(prompt_content_list)
    
    return prompt

if __name__ == "__main__":
    # # 首先，拿到原始 bug 数据
    # cleaned_single_line_code_result = clean_parse_d4j_single_line(single_line_code_path)
    # # 158
    # assert len(cleaned_single_line_code_result) == 158
    
    # print("finished getting original buggy code!")
    
    # ########## ++++++++++ ##########
    
    # # 第二步，分三项，拿到测试结果
    # cleaned_single_line_test_result, single_line_bug_id_list = clean_parse_d4j_test_info_single_line(test_info_path, single_line_metadata_path)
    # assert len(cleaned_single_line_test_result) == 154
    
    # print("finished getting original test info!")
    pass