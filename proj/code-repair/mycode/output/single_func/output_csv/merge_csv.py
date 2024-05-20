# 用于合并各次测试的结果，给出测试的最终结果
import pandas as pd
import os

output_dir = "./maxlen=1024_epoch=1_without_comment_without_initial_prompt"
output_paths = ["test_output_0.csv", "test_output_1.csv", "test_output_2.csv", "test_output_3.csv", "test_output_4.csv", \
                "test_output_5.csv", "test_output_6.csv", "test_output_7.csv", "test_output_8.csv", "test_output_9.csv"]

# final_csv_path = "./test_output_final.csv"
final_csv_path = "test_output_final.csv"

bug_ids = []
final_outcome = []
test_pass_cnt = []
test_fail_cnt = []
comp_fail_cnt = []
time_out_cnt = []

for idx in range(len(output_paths)):
    # output_path = output_paths[idx]
    output_path = os.path.join(output_dir, output_paths[idx])
    if not os.path.exists(output_path):
        print("skipping path %s!" % (output_paths[idx]))
        continue
    df_i = pd.read_csv(output_path, encoding="utf-8")
    
    if idx == 0:
        bug_ids = df_i["bug_id"].tolist()
        final_outcome = ["" for i in range(len(bug_ids))]
        test_pass_cnt = [0 for i in range(len(bug_ids))]
        test_fail_cnt = [0 for i in range(len(bug_ids))]
        comp_fail_cnt = [0 for i in range(len(bug_ids))]
        time_out_cnt = [0 for i in range(len(bug_ids))]
    
    for _, row in df_i.iterrows():
        bug_id, test_output = row["bug_id"], row["test_output"]
        if test_output == "test passed":
            test_pass_cnt[bug_ids.index(bug_id)] += 1
        elif test_output == "test failed":
            test_fail_cnt[bug_ids.index(bug_id)] += 1
        elif test_output == "compile error":
            comp_fail_cnt[bug_ids.index(bug_id)] += 1
        elif test_output == "time out":
            time_out_cnt[bug_ids.index(bug_id)] += 1
        else:
            print(test_output)
            test_fail_cnt[bug_ids.index(bug_id)] += 1
            # raise Exception("Hey!")

# 汇总结果
for idx in range(len(bug_ids)):
    tp_cnt, tf_cnt, cf_cnt, to_cnt = test_pass_cnt[idx], test_fail_cnt[idx], comp_fail_cnt[idx], time_out_cnt[idx]
    # assert (tp_cnt + tf_cnt + cf_cnt + to_cnt) == len(output_paths)
    if tp_cnt > 0:
        final_outcome[idx] = "test passed"
        continue
    if tf_cnt > 0:
        final_outcome[idx] = "test failed"
        continue
    if cf_cnt > 0:
        final_outcome[idx] = "compile error"
        continue
    final_outcome[idx] = "time out"
    
df_merge = pd.DataFrame({"bug_id":bug_ids, "final_outcome":final_outcome, "test_pass_cnt":test_pass_cnt, \
    "test_fail_cnt":test_fail_cnt, "comp_fail_cnt":comp_fail_cnt, "time_out_cnt":time_out_cnt})
df_merge.to_csv(os.path.join(output_dir, final_csv_path), index=False, encoding="utf-8")