# 用于获取每个 bug 的 compile 和 test 所需时间，为我自己的版本提供基准
# 目前暂时只有 buggy 的版本，来自 defects4j-clean
import subprocess
import json
import os
from tqdm import tqdm
import time
import pandas as pd

target_comple_and_test_dir = "/data/lihy/defects4j-fixed-clean"
single_func_bugs_path = "../../defects4j/metadata/single_func_bugs.json"
output_time_path = "./time_compile_test/single_func_fixed_ver.csv"

with open(single_func_bugs_path, "r", encoding="utf-8") as f1:
    single_func_bugs = json.load(f1)["bug_id"]
assert len(single_func_bugs) == 483

failed_compile_bugs = []
failed_test_bugs = []
compile_time_list = []
test_time_list = []

for bug_id in tqdm(single_func_bugs):
    proj, id = bug_id.split("-")
    # 目标目录
    target_comple_and_test_path = os.path.join(target_comple_and_test_dir, proj, proj + "_" + id)
    
    cmd1 = ["defects4j", "compile"]
    cmd2 = ["defects4j", "test"]
    
    t1 = time.time()
    try:
        a = subprocess.run(cmd1, cwd=target_comple_and_test_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        # 记录 checkout 失败的所有 bug
        print("checkout failed for bug number %s in proj %s!" % (id, proj))
        failed_compile_bugs.append(proj + "_" + id)
        continue
    t2 = time.time()
    
    t3 = time.time()
    try:
        a = subprocess.run(cmd2, cwd=target_comple_and_test_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("test failed for bug number %s in proj %s!" % (id, proj))
        failed_test_bugs.append(proj + "_" + id)
        continue
    t4 = time.time()
    
    # 单位：s
    compile_time = t2 - t1
    test_time = t4 - t3
    compile_time_list.append(compile_time)
    test_time_list.append(test_time)
    
# 输出结果
df_output_time = pd.DataFrame({"bug_id":single_func_bugs, "compile_time":compile_time_list, "test_time":test_time_list})
df_output_time.to_csv(output_time_path, index=False, encoding="utf-8")

if len(failed_compile_bugs) > 0:
    print("failed compile:", failed_compile_bugs)
if len(failed_test_bugs) > 0:
    print("failed test:", failed_test_bugs)