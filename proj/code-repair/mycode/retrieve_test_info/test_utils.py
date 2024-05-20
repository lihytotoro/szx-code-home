# 测试一下，utils 中所写的获取三种测试相关信息的函数是否能用
from utils import retrieve_test_err_info, retrieve_test_func_name_and_trigger_codes
import os
import json
import pandas as pd

# 第一个路径是各个项目信息所在的目录，第二个路径是编译后的项目所在路径
base_projects_info_path = "../../defects4j/framework/projects"
base_projects_path = "/data/lihy/defects4j"

test_info_output_path = "./output"

single_func_index_path = "../../defects4j/metadata/single_func_bugs.json"
single_hunk_index_path = "../../defects4j/metadata/single_hunk_bugs.json"
single_line_index_path = "../../defects4j/metadata/single_line_bugs.json"

# 测试所有的 835 个 active bugs 嘛？不需要
# 现阶段，只需要考虑 1.2~2.0 版本的所有 SF、SH、SL bug
with open(single_func_index_path, "r", encoding="utf-8") as f_sfunc:
    single_func_bug_ids = json.load(f_sfunc)["bug_id"]
with open(single_hunk_index_path, "r", encoding="utf-8") as f_shunk:
    single_hunk_bug_ids = json.load(f_shunk)["bug_id"]
with open(single_line_index_path, "r", encoding="utf-8") as f_sline:
    single_line_bug_ids = json.load(f_sline)["bug_id"]
    
# 经测试，SL、SH、SF 三种类型的 bug 确实满足互相包含关系
def extract_test_info(proj_info_path, proj_path):
    # 记录 flag_1 出错的所有项目！
    # 事实上，编译都通过了？
    f1b_proj = []
    f1b_id   = []
    f1b_path = []
    f1b_real_row_id = []
    f1b_trig_row_id = []
    
    cnt_bugs, cnt_f1b_bugs, cnt_f1p_bugs, cnt_skipped_bugs = 0, 0, 0, 0
    
    # 记录多个 trigger_test 的情况
    mtt_proj = []
    mtt_id   = []
    mtt_cnt_tests = []
    
    for bug_id in single_func_bug_ids:
        proj, id = bug_id.split("-")
        # 暂时的，用于节省测试时间
        # if proj in ["Chart", "Cli", "Closure", "Codec", "Collections", "Compress", "Csv", "Gson", \
        #             "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath", "Lang", "Math"]:
        #     continue
        # 这是出现问题的 bug，后面去考虑如何提取
        if bug_id in ["Cli-40", "Compress-28", "Compress-44", "Gson-16", "Jsoup-68", "Jsoup-85", "Lang-57", \
                    "Math-25", "Math-34", "Math-45", "Math-50", "Math-86", "Mockito-8"]:
            print("bug %s skipped temporarily!" % bug_id)
            cnt_skipped_bugs += 1
            continue
        cnt_bugs += 1
        # error: 不能 split？
        # print("bug_id:", bug_id)
        test_info_output_subpath = os.path.join(test_info_output_path, proj)
        if not os.path.exists(test_info_output_subpath):
            os.mkdir(test_info_output_subpath)
        test_info_output_subsubpath = os.path.join(test_info_output_subpath, id)
        if not os.path.exists(test_info_output_subsubpath):
            os.mkdir(test_info_output_subsubpath)
        # 在该路径下（subsubpath），储存该 bug 对应的三种测试信息
        # 应该做什么？根据 proj_info_path, proj_path, proj, id，获取信息
        trigger_func_name, trigger_codes, cnt_trigger_tests, flag_1, \
            test_file_absol_path, now_row_id, trigger_row_id = retrieve_test_func_name_and_trigger_codes(proj, id, proj_info_path, proj_path)
            
        # multi triggered tests:    
        if cnt_trigger_tests > 1:
            mtt_proj.append(proj)
            mtt_id.append(id)
            mtt_cnt_tests.append(cnt_trigger_tests)
        
        if flag_1:
            cnt_f1p_bugs += 1
            with open(os.path.join(test_info_output_subsubpath, "trigger_func_name.txt"), "w") as f_func:
                f_func.write(trigger_func_name + "\n")
            if not trigger_codes is None:
                with open(os.path.join(test_info_output_subsubpath, "trigger_codes.txt"), "w") as f_codes:
                    for code_line in trigger_codes:
                        f_codes.write(code_line + "\n")
        else:
            cnt_f1b_bugs += 1
            # 能看到还是有一些 flag_1 为 False 的案例，说明获取目标代码行的时候有问题？
            # 使用倒数后三个返回值
            f1b_proj.append(proj)
            f1b_id.append(id)
            f1b_path.append(test_file_absol_path)
            f1b_real_row_id.append(now_row_id)
            f1b_trig_row_id.append(trigger_row_id)
            
        # 接下来，获取报错信息
        test_err_info, flag_2 = retrieve_test_err_info(proj, id, proj_info_path)
        if flag_2:
            with open(os.path.join(test_info_output_subsubpath, "test_err_info.txt"), "w") as f_info:
                for info_line in test_err_info:
                    f_info.write(info_line + "\n")
    
    # 在所有循环结束后，记录各项信息：
    print("bug number:", cnt_bugs)
    print("f1p bug number:", cnt_f1p_bugs)
    print("f1b bug number:", cnt_f1b_bugs)
    print("skipped bugs:", cnt_skipped_bugs)
    
    df_f1b = pd.DataFrame({"proj_name":f1b_proj, "bug_id":f1b_id, "absol_path":f1b_path, "now_cursor":f1b_real_row_id, "trigger_cursor":f1b_trig_row_id})
    df_f1b.to_csv(os.path.join(test_info_output_path, "f1b_info.csv"), index=True, encoding="utf-8")
    
    # 另外，还需要输出一下 有多个 trigger_test 的情况
    df_mtt = pd.DataFrame({"proj_name":mtt_proj, "bug_id":mtt_id, "cnt_triggered_tests":mtt_cnt_tests})
    df_mtt.to_csv(os.path.join(test_info_output_path, "mtt_info.csv"), index=True, encoding="utf-8")
                    
# 执行 test_utils 函数
if __name__ == "__main__":
    extract_test_info(base_projects_info_path, base_projects_path)