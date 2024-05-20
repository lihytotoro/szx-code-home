# 此函数用于
# 1. 尝试对于每一个 bug 编译项目，然后回填 chatglm 生成之后的代码！
# 2. 测试代码的正确性，即：看看如何模拟命令行 defects4j compile 和 test 的输入！

# 0508 new: 多进程化，统一编译 10 哥项目的 4830 个 bug？

# TODO: 目前先逐一将程序编译出来？注意编译到 data/lihy 目录下，1G 大约 30 个项目？

import os
import time
from sentry_sdk import continue_trace
from tqdm import tqdm
import subprocess
import pandas as pd
import json
import argparse
from multiprocessing import Pool

# 准备按照类似的原理，编译每个项目下的每个 bug 到一个目录下
# 示例：defects4j checkout -p proj -v {id}b -w /data/lihy/defects4j/proj/proj_id_buggy
#################
def checkout_and_compile_d4j_for_some_bugs(base_checkout_dir, bugs_list):
    for bug in tqdm(bugs_list):
        '''
        bug 的格式：
        {"subdir_id":subdir_idx, "bug_id":bug_id}
        其中，subdir_idx 一般来说为 0~9，bug_id 为 Proj-id 形式
        '''
        subdir_id = bug["subdir_id"]
        if subdir_id is not None:
            type(subdir_id) == int
            subdir = f"defects4j-{subdir_id}"
        else:
            subdir = 'defects4j_buggy_clean'
        checkout_dir = os.path.join(base_checkout_dir, subdir)
        
        print(f"Checkout dir:{checkout_dir}")
        
        bug_id = bug["bug_id"]
        proj, id = bug_id.split("-")

        # print(f"\tnow checking out for proj {proj}\tbug number {id}")
        
        ver = id + "f"
        proj_dir = os.path.join(checkout_dir, proj)
        if not os.path.exists(proj_dir):
            os.mkdir(proj_dir)
        pth = os.path.join(checkout_dir, proj, proj + "_" + id)
        
        if os.path.exists(pth):
            print("bug has been checked out: %s" % bug_id)
            continue
        
        cmd1 = ["defects4j", "checkout", "-p", proj, "-v", ver, "-w", pth]
        try:
            a = subprocess.run(cmd1, cwd = "../defects4j")
        except:
            # 记录 checkout 失败的所有 bug
            print("checkout failed for bug number %s in proj %s!" % (id, proj))
            raise Exception("Hey 1!")
        
        # checkout 出来之后，还要编译一下
        cmd2 = ["defects4j", "compile"]
            
        try:
            b = subprocess.run(cmd2, cwd = pth)
        except:
            print("compile failed for bug number %s in proj %s!" % (id, proj))
            raise Exception("Hey 2!")
            

def run_process(batch_args):
    base_checkout_dir, bugs_list = batch_args['base_checkout_dir'], batch_args['bugs_list']
    checkout_and_compile_d4j_for_some_bugs(base_checkout_dir=base_checkout_dir, bugs_list=bugs_list)
    

# 0519 更新: 之前没有处理 buggy_clean 目录
def checkout_and_compile_d4j_all_bugs(base_checkout_dir, subdir_idxs, single_func_bugs, process_num, bugs_per_process, bugs_start_idx):
    '''
    '''
    all_target_bugs = []
    
    if subdir_idxs is not None:
        for subdir_idx in subdir_idxs:
            for bug_id in single_func_bugs:
                all_target_bugs.append({"subdir_id":subdir_idx, "bug_id":bug_id})
        assert len(all_target_bugs) == 4830
    else:
        for bug_id in single_func_bugs:
            all_target_bugs.append({"subdir_id":None, "bug_id":bug_id})
        assert len(all_target_bugs) == 483
    
    total_bugs_cnt = process_num * bugs_per_process
    bugs_end_idx = min(len(all_target_bugs), bugs_start_idx + total_bugs_cnt)
    target_bugs = all_target_bugs[bugs_start_idx:bugs_end_idx]
    
    # 每个进程真实分到的文件数
    if len(target_bugs) % process_num == 0:
        real_bugs_per_process = len(target_bugs) // process_num
    else:
        real_bugs_per_process = len(target_bugs) // process_num + 1
        
    batch_args = []
    
    # 根据进程编号，分别分配文件列表
    for process_idx in range(process_num):
        start_idx = bugs_start_idx + process_idx * real_bugs_per_process
        end_idx = min(bugs_end_idx, bugs_start_idx + (process_idx + 1) * real_bugs_per_process)
        allocated_bugs = all_target_bugs[start_idx:end_idx]
        batch_args.append({"base_checkout_dir":base_checkout_dir, "bugs_list":allocated_bugs})
    
    with Pool(process_num) as pool:
        pool.map(run_process, batch_args)


def get_args():
    parser = argparse.ArgumentParser()
    # 总共开多少进程进行处理
    parser.add_argument("--process_num", type=int, default=1, help="")
    # 每个进程负责多少条 bug 的 checkout 和编译
    parser.add_argument("--bugs_per_process", type=int, default=1, help="")
    # 从哪个序号开始属于这些进程的目标
    parser.add_argument("--bugs_start_idx", type=int, default=0, help="")
    
    parser.add_argument("--base_checkout_dir", type=str, default="/home/lihaoyu/szx/test_suites/defects4j", help="")
    parser.add_argument("--single_func_bugs_path", type=str, default="/home/lihaoyu/szx/proj/code-repair/defects4j/metadata/single_func_bugs.json", help="")
    
    # 0519 new: for buggy_clean dir
    parser.add_argument("--checkout_buggy_clean", action="store_true", default=False, help="whether to checkout for buggy_clean dir.")
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    
    with open(args.single_func_bugs_path, "r", encoding="utf-8") as f:
        single_func_bugs = json.load(f)['bug_id']
        assert len(single_func_bugs) == 483
    
    if not args.checkout_buggy_clean:
        subdir_idxs = [0,1,2,3,4,5,6,7,8,9]
    else:
        subdir_idxs = None
    
    checkout_and_compile_d4j_all_bugs(base_checkout_dir=args.base_checkout_dir, 
                                      subdir_idxs=subdir_idxs, 
                                      single_func_bugs=single_func_bugs, 
                                      process_num=args.process_num, 
                                      bugs_per_process=args.bugs_per_process, 
                                      bugs_start_idx=args.bugs_start_idx)
    