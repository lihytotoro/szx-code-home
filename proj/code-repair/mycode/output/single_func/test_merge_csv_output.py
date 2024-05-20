import pandas as pd

final_csvs = ["./output_csv/maxlen=1024_epoch=1_without_comment_without_initial_prompt/test_output_final.csv", "./output_csv/maxlen=1024_epoch=2_without_comment_without_initial_prompt/test_output_final_copy_author_ver_epoch=2.csv"]

final_dfs = []

for final_csv in final_csvs:
    final_dfs.append(pd.read_csv(final_csv))
    
bug_ids = final_dfs[0]["bug_id"].tolist()
outcomes = []

for bug_id in bug_ids:
    tp, tf, cf = 0, 0, 0
    for final_df in final_dfs:
        tmp_df = final_df[final_df["bug_id"] == bug_id]
        if len(tmp_df) == 0:
            print(bug_id)
            continue
        else:
            outcome = tmp_df.iloc[0, 1]
        if outcome == "test passed":
            tp += 1
        elif outcome in ["test failed", "time out", "test error"]:
            tf += 1
        elif outcome == "compile error":
            cf += 1
        else:
            print(outcome)
            raise Exception("Hey!")
    if tp > 0:
        outcomes.append("test passed")
    elif tf > 0:
        outcomes.append("test failed")
    else:
        outcomes.append("compile error")
        
df_ans = pd.DataFrame({"bug_id":bug_ids, "outcome":outcomes})
df_ans.to_csv("./test_merge_3.csv", index=False)