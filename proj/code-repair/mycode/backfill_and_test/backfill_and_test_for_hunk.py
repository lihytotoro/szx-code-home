# 对于 313（308）个 bug，回填 output 到正确的文件中，回填之后直接开始测试
# 在第一次回填时记得复制原来的文件，后面加一个 copied 的后缀
# 之后每次操作文件都针对原始文件名，这样才能通过编译
# 应该是编译一次测试一次？
# 我认为应当分 10 次测试分别生成 10 个 df

import pandas as pd
import subprocess
import json
import jsonlines
import os
from tqdm import tqdm
import shutil
import time
from func_timeout import func_timeout, FunctionTimedOut

# 分别是需要回填到的路径、各类 metadata 所在的路径，以及 大模型输出的原始路径
backfill_base_dir = "/data/lihy/defects4j"
patch_info_path = "../defects4j/framework/projects"
# 以下是主要依赖的三个文件
target_file_path_path = "./output/single_hunk/backfill_path.json"
input_infos_path = "./output/single_hunk/defects4j_single_chunk_repairllama.jsonl"
output_patches_path = "./output/single_hunk/defects4j_single_chunk_repairllama_test_output_epoch=5_maxlen=1024.jsonl"

# 复写相关的 output 目录，仍然予以保留，方便查看回填是否正确
rewrite_path = "./output/single_hunk"

beam_size = 10

# 第一步！
# 定义回填函数：将指定的代码填入项目的指定位置！
# patch_idx = 0 时，记得将原始文件复制出来
# patch_idx > 0 时，读取原始文件，然后作为拼接生成新文件的对象
def backfill_code(proj, id, patch, patch_idx, target_path, cleaned_result):
    bug_id = proj + "-" + id
    
    # 然后，从原始的 src.patch 文件中（根据 proj 和 bug_id），获取应当修改的文件，以及应当修改的行数（要去掉的原始行数！）
    info_path = os.path.join(patch_info_path, proj, "patches", id + ".src.patch")
    
    info_lines = []
    with open(info_path, "r", encoding="utf-8") as f_info:
        for line in f_info.readlines():
            info_lines.append(line)
    
    # 获取前后缀信息、whitespace 数目
    prefix = cleaned_result["prefix"].splitlines()
    suffix = cleaned_result["suffix"].splitlines()
    buggy_hunk = cleaned_result["buggy_chunk"]
    function_start_idx = cleaned_result["func_start_idx"]
    function_end_idx   = cleaned_result["func_end_idx"]
    whitespace = cleaned_result["buggy_white_space"]

    patch_lines = patch.splitlines()
    
    # 然后，向目标位置回填代码！
    # 获取目标文件的名称！
    target_file_name = target_path.split("/")[-1]
    copied_target_file_name = target_file_name.removesuffix(".java") + "_copied" + ".java"
    
    # 复制一份原始文件，以备后续借用
    ########## 注意！！原始文件之前测试时修改过了，这里我们需要借用之前 copy 出来的
    if patch_idx == 0:
        copied_target_file_subsubpath = os.path.join(rewrite_path, proj)
        copied_target_file_subpath = os.path.join(rewrite_path, proj, id)
        copied_target_file_path = os.path.join(rewrite_path, proj, id, copied_target_file_name)
        if not os.path.exists(copied_target_file_subsubpath):
            os.mkdir(copied_target_file_subsubpath)
        if not os.path.exists(copied_target_file_subpath):
            os.mkdir(copied_target_file_subpath)
        ########## 从哪里 copy？
        shutil.copy(target_path, copied_target_file_path)
        # shutil.copy(temporary_target_path, copied_target_file_path)
    else:
        copied_target_file_path = os.path.join(rewrite_path, proj, id, copied_target_file_name)
        
    # 用省事一点的方法，一个读取一个写入！
    buffer_before_func = []
    buffer_after_func = []
    buffer_middle_func = []
    
    with open(copied_target_file_path, "r", encoding="utf-8") as fr:
        cnt_fr = 1
        for line in fr.readlines():
            if cnt_fr < function_start_idx:
                buffer_before_func.append(line)
            elif cnt_fr > function_end_idx:
                buffer_after_func.append(line)
            else:
                buffer_middle_func.append(line)
            cnt_fr += 1

    ########## 下面看一下如何写入到对应位置 ##########
    # 接下来，开始按照 before -> target_code -> after 的顺序，写入新文件中！
    # 注意：修改后的代码，应当舍弃第一个 \n 之前的部分？
    # 打开同一个文件路径，相当于直接覆盖！
    with open(target_path, "w", encoding="utf-8") as fw:
        for line in buffer_before_func:
            fw.write(line)
        # 这里的处理不对，忘记写入前缀和后缀了！
        for line in prefix:
            fw.write(whitespace * " " + line + "\n")
        for line in patch_lines:
            fw.write(whitespace * " " + line + "\n")
        for line in suffix:
            fw.write(whitespace * " " + line + "\n")
        for line in buffer_after_func:
            fw.write(line)
    
    # rewrite 部分
    # 注意：对于 hunk 和 func，需要另开目录存储文件
    if patch_idx == 0:
        rewrite_fixed_file_only_func(proj, id, target_file_name, prefix, patch_lines, suffix, whitespace)
        rewrite_buggy_file_only_func(proj, id, target_file_name, buffer_middle_func)
        rewrite_buggy_info(proj, id, info_lines)
        rewrite_fixed_model_reply(proj, id, patch_lines)
        rewrite_prompt_info(proj, id, prefix, buggy_hunk, suffix)

# 重新思考一下为什么要写这些文件！

# 1. 写入修改之后的函数
def rewrite_fixed_file_only_func(proj, id, target_file_name, prefix, patch_lines, suffix, whitespace):
    fixed_func_rewrite_final_path = os.path.join(rewrite_path, proj, id, target_file_name.removesuffix(".java") + "_fixed_func.java")
    with open(fixed_func_rewrite_final_path, "w", encoding="utf-8") as f_fixed_file_rewrite:
        for line in prefix:
            f_fixed_file_rewrite.write(whitespace * " " + line + "\n")
        for line in patch_lines:
            f_fixed_file_rewrite.write(whitespace * " " + line + "\n")
        for line in suffix:
            f_fixed_file_rewrite.write(whitespace * " " + line + "\n")

# 2. 写入修改之前的函数       
def rewrite_buggy_file_only_func(proj, id, target_file_name, buffer_middle_func):
    buggy_func_rewrite_final_path = os.path.join(rewrite_path, proj, id, target_file_name.removesuffix(".java") + "_buggy_func.java")
    with open(buggy_func_rewrite_final_path, "w", encoding="utf-8") as f_buggy_file_rewrite:
        for line in buffer_middle_func:
            f_buggy_file_rewrite.write(line)

# 3. 写入 src.patch 文件
def rewrite_buggy_info(proj, id, info_lines):
    info_file_rewrite_final_path = os.path.join(rewrite_path, proj, id, id + ".src.patch")
    with open(info_file_rewrite_final_path, "w", encoding="utf-8") as f_info_file_rewrite:
        for line in info_lines:
            f_info_file_rewrite.write(line)

# 4. 写入 fixed_model_reply(模型回复)
def rewrite_fixed_model_reply(proj, id, patch_lines):
    patch_rewrite_final_path = os.path.join(rewrite_path, proj, id, "patch_lines.txt")
    with open(patch_rewrite_final_path, "w", encoding="utf-8") as f_patch_rewrite:
        for line in patch_lines:
            f_patch_rewrite.write(line)
            
# 5. 写入完整的 prompt 信息
def rewrite_prompt_info(proj, id, prefix, buggy_hunk, suffix):
    prompt_info_rewrite_final_path = os.path.join(rewrite_path, proj, id, "prompt_info.txt")
    with open(prompt_info_rewrite_final_path, "w", encoding="utf-8") as f_prompt_info_rewrite:
        f_prompt_info_rewrite.write("prefix:" + "\n")
        for line in prefix:
            f_prompt_info_rewrite.write(line + "\n")
        
        f_prompt_info_rewrite.write("\n")
        
        f_prompt_info_rewrite.write("buggy_hunk:" + "\n")
        f_prompt_info_rewrite.write(buggy_hunk + "\n")
        
        f_prompt_info_rewrite.write("\n")
        
        f_prompt_info_rewrite.write("suffix:" + "\n")
        for line in suffix:
            f_prompt_info_rewrite.write(line + "\n")


########## test ##########

# 对于特定的某一个 bug 运行编译测试
# 在这里我们应当加入超时检测！
def run_test_for_single_bug(proj, id, pth):
    cmd1 = ["defects4j", "compile"]
    cmd2 = ["defects4j", "test"]

    # 编译！
    tc1 = time.time()
    stdout_1, stderr_1, retcode_1 = get_run_result(cmd1, pth)
    tc2 = time.time()
    tc = tc2 - tc1
    
    # 判断是否编译通过了！
    flag_compile = True
    if retcode_1 != 0:
        flag_compile = False
    else:
        for line in stderr_1.split("\n"):
            if len(line) > 0:
                if not line.endswith("OK"):
                    flag_compile = False
    
    # 编译就没有通过的情况！
    if not flag_compile:
        return "compile error", tc, -1
    
    # 编译通过之后，继续运行测试！
    tt1 = time.time()
    stdout_2, stderr_2, retcode_2 = get_run_result(cmd2, pth)
    tt2 = time.time()
    tt = tt2 - tt1
    
    flag_test = True
    if retcode_2 != 0:
        flag_test = False
    else:
        for line in stderr_2.split("\n"):
            if len(line) > 0:
                if not line.endswith("OK"):
                    flag_test = False
                
    # 如果仍然通过，那么看一下 fail 的数目   
    if flag_test:
        stdout_lines = stdout_2.split("\n")
        cnt_failing_tests = int(stdout_lines[0].split(" ")[-1])
        if cnt_failing_tests == 0:
            return "test passed", tc, tt
        else:
            return "test failed", tc, tt
    else:
        return "test error", tc, tt
    
def get_run_result(cmd, cwd):
    # 这里为什么会出错呢？
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 获取标准输出信息
    stdout = result.stdout.decode('utf-8')
    # 获取错误输出信息
    stderr = result.stderr.decode('utf-8')
    # 获取返回值
    retcode = result.returncode
    return stdout, stderr, int(retcode)

########## main ##########

if __name__ == "__main__":
    input_infos_all = {}
    output_patches_all = {}
    
    with jsonlines.open(input_infos_path, "r") as reader_in:
        for obj in reader_in:
            bug_id = obj["bug_id"]
            input_infos_all[bug_id] = obj
    with jsonlines.open(output_patches_path, "r") as reader_out:
        for obj in reader_out:
            bug_id = obj["bug_id"]
            output_patches_all[bug_id] = obj
            
    with open(target_file_path_path, "r", encoding="utf-8") as f_paths:
        target_paths_dict = json.load(f_paths)
        
    assert len(input_infos_all) == 313
    assert len(output_patches_all) == 308
    assert len(target_paths_dict) == 313
    
    # 开始遍历每一个项目
    # 新问题：为什么会超时呢？
    for patch_idx in range(6, beam_size):
        # 用于记录本轮次的运行结果
        bug_id_list = []
        test_output_list = []
        compile_time_list = []
        test_time_list = []
        for bug_id, output_patches in tqdm(output_patches_all.items()):
            proj, id = bug_id.split("-")
            cleaned_result = input_infos_all[bug_id]

            print("now backfilling for bug %s" % bug_id)
            
            # 获取候选补丁
            patch = output_patches["output"][str(patch_idx)]["output_patch"]
            
            # 获取回填路径
            target_path = target_paths_dict[bug_id]
            
            # 提取出的 fixed_reply 作为将要回填的代码！
            # 在此之前相当于一直在做提取代码的工作
            backfill_code(proj, id, patch, patch_idx, target_path, cleaned_result)
            
            # 在完成了回填之后，我们需要进行编译测试！
            print("now running test for bug %s" % bug_id)
            proj_checkout_pth = os.path.join(backfill_base_dir, proj, proj + "_" + id)
            
            ########## time out ##########
            try:
                # 超时时间初步设置为 150s
                ret_sym, t_compile, t_test = func_timeout(150, run_test_for_single_bug, args=(proj, id, proj_checkout_pth, ))
            except FunctionTimedOut as e:
                print(e)
                ret_sym = "time out"
                t_compile = -1
                t_test = -1
            
            bug_id_list.append(bug_id)
            test_output_list.append(ret_sym)
            compile_time_list.append(t_compile)
            test_time_list.append(t_test)
            
        save_output_path = os.path.join(rewrite_path, "output_csv", "test_output_" + str(patch_idx) + ".csv")
        df_test_output_i = pd.DataFrame({"bug_id":bug_id_list, "test_output":test_output_list, \
                            "compile_time":compile_time_list, "test_time":test_time_list})
        df_test_output_i.to_csv(save_output_path, index=False, encoding="utf-8")