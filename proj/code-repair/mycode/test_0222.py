# 看一下三种类别的 bug 都有多少正确了
import pandas as pd
import json

single_line_path = "../defects4j/metadata/single_line_bugs.json"
single_hunk_path = "../defects4j/metadata/single_hunk_bugs.json"
single_func_path = "../defects4j/metadata/single_func_bugs.json"

outcome_path = "./output/single_func/output_csv/maxlen=1024_epoch=2_without_comment_without_initial_prompt/test_output_final_copy_author_ver_epoch=2.csv"

with open(single_f_path, "r", encoding="utf-8") as f:
    bugs = json.load(f)["bug_id"]
    print(len(bugs))
    
df = pd.read_csv(outcome_path, index_col=False)
out_bug_id = df["bug_id"].tolist()
out_fin_ou = df["final_outcome"].tolist()

tp, tf, ce = 0, 0, 0
for bug_id in bugs:
    if bug_id in out_bug_id:
        ou = out_fin_ou[out_bug_id.index(bug_id)]
        if ou == "test passed":
            tp += 1
        elif ou == "test failed":
            tf += 1
        elif ou == "test error":
            tf += 1
        else:
            ce += 1
print(tp, tf, ce)