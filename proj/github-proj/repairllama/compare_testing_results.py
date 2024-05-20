# 用于对比我的实验结果与作者的结果的区别！
import jsonlines
import pandas as pd

author_best_output_patches_path = "./results/defects4j/repairllama/lora/RepairLLaMA_defects4j_f2f_bugs_results_ir2_or2.jsonl"
author_best_output_stat_path = "./output_compare/author_ir4_or2.csv"

my_best_output_stat_path = "./output_compare/test_output_final_copy_author_ver_epoch=2.csv"

compare_csv_output_path = "./output_compare/output/compare_au_my.csv"
target_worse_my_output_path = "./output_compare/output/target_worse_my.csv"
target_worse_au_output_path = "./output_compare/output/target_worse_au.csv"

def generating_author_result(author_output_patches_path, author_output_stat_path):
    bug_ids = []
    outcome = []
    tp_cnt = []
    tf_cnt = []
    cf_cnt = []

    with jsonlines.open(author_output_patches_path, "r") as reader:
        for obj in reader:
            bug_ids.append(obj["bug_id"])
            output_list = obj["test_results"]
            assert len(output_list) == 10
            
            # 一共有五种可能得测试结果，目前暂时将后面三种视为同一类别的！看看是哪些 bug 能通过！
            tp, tf, cf = 0, 0, 0
            for output in output_list:
                if output == "Compile fail":
                    cf += 1
                elif output == "Test fail":
                    tf += 1
                else:
                    assert output in ["Plausible", "Line Match", "AST match", "Line match"]
                    tp += 1
            assert (tp + tf + cf) == 10
            tp_cnt.append(tp)
            tf_cnt.append(tf)
            cf_cnt.append(cf)
            if tp > 0:
                outcome.append("test passed")
            elif tf > 0:
                outcome.append("test failed")
            else:
                outcome.append("compile error")

    # ['Compile fail', 'Test fail', 'Plausible', 'Line match', 'AST match']

    df_author = pd.DataFrame({"bug_id":bug_ids, "outcome":outcome, "tp_cnt":tp_cnt, "tf_cnt":tf_cnt, "cf_cnt":cf_cnt})
    df_author.to_csv(author_output_stat_path, index=False, encoding="utf-8")

def compare_au_my(df_au, df_my):
    au_bug_ids = set(df_au["bug_id"].tolist())
    my_bug_ids = set(df_my["bug_id"].tolist())
    
    common_bug_ids = my_bug_ids & au_bug_ids
    # 472: ir4*or2 vs mine
    # print(len(common_bug_ids))
    
    ans_bug_ids = []
    ans_au_results = []
    ans_my_results = []
    
    for bug_id in common_bug_ids:
        ans_bug_ids.append(bug_id)
        au_res = df_au[df_au["bug_id"] == bug_id].iloc[0, 1]
        my_res = df_my[df_my["bug_id"] == bug_id].iloc[0, 1]
        ans_au_results.append(au_res)
        ans_my_results.append(my_res)
    
    return ans_bug_ids, ans_au_results, ans_my_results
    
    # set1 = au_bug_ids - my_bug_ids
    # set2 = my_bug_ids - au_bug_ids
    # print("set1:", set1)
    # print("set2:", set2)


# 初步实验结果：
# my_res 多出来 2 个： Math-90, Closure-91
# aut_res 多出来 8 个：{'Collections-27', 'Chart-23', 'Closure-170', 'Cli-2', 'JxPath-14', 'Closure-132', 'Gson-10', 'Gson-2'}，其中只有 Gson-10 是通过了测试的，说明区别主要还是在共有部分

if __name__ == "__main__":
    # generating_author_result(author_best_output_patches_path, author_best_output_stat_path)
    df_au = pd.read_csv(author_best_output_stat_path)
    df_my = pd.read_csv(my_best_output_stat_path)
    ans_bug_ids, ans_au_results, ans_my_results = compare_au_my(df_au, df_my)
    df_compare = pd.DataFrame({"bug_id":ans_bug_ids, "au_result":ans_au_results, "my_result":ans_my_results})
    # df_compare.to_csv(compare_csv_output_path, index=False, encoding="utf-8")
    
    # 从 df_compare 中，继续提取 author 版本是 test passed 而 my 是 failed 或 error 的那些 bug
    df_diff_1 = df_compare[(df_compare["au_result"] == "test passed") & (df_compare["my_result"] != "test passed")]
    df_diff_2 = df_compare[(df_compare["my_result"] == "test passed") & (df_compare["au_result"] != "test passed")]
    # 48 个这样的 bug, 43 + 5
    # 20 个我比 author 好的
    # print(len(df_diff_1), len(df_diff_2))
    
    # 尝试将我比作者表现差的 bug 输出出来，看看情况
    target_worse_bugs = df_diff_1["bug_id"].tolist()
    df_target_worse_my = df_my[df_my["bug_id"].isin(target_worse_bugs)]
    df_target_worse_au = df_au[df_au["bug_id"].isin(target_worse_bugs)]
    # 48
    print(len(df_target_worse_my))
    df_target_worse_my.to_csv(target_worse_my_output_path, index=False, encoding="utf-8")
    df_target_worse_au.to_csv(target_worse_au_output_path, index=False, encoding="utf-8")
    