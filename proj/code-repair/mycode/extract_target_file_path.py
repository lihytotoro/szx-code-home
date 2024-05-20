# 目的：提取所有 single chunk 类型 bug 的回填目标路径（文件）
# 修改：提取所有 single func  类型 bug 的回填目标路径
import json
import os
from tqdm import tqdm

# 分别是需要回填到的路径、各类 metadata 所在的路径，以及 大模型输出的原始路径
backfill_base_dir = "/data/lihy/defects4j-dir-2/defects4j-1"
patch_info_path = "../defects4j/framework/projects"
# 从这里获知哪些 bug 是单段落的
# single_hunk_bugs_metadata_path = "../defects4j/metadata/single_hunk_bugs.json"
single_func_bugs_metadata_path = "../defects4j/metadata/single_func_bugs.json"

save_backfill_path = "./output/single_func/backfill_paths/defects4j-dir-2/backfill_path_1.json"

# 对于指定的
def extract_target_file_path(bug_id):
    proj, id = bug_id.split("-")
    backfill_target_base_path = os.path.join(backfill_base_dir, proj, proj + "_" + id)
    
    # 然后，从原始的 src.patch 文件中（根据 proj 和 bug_id），获取应当修改的文件，以及应当修改的行数（要去掉的原始行数！）
    info_path = os.path.join(patch_info_path, proj, "patches", id + ".src.patch")
    
    with open(info_path, "r", encoding="utf-8") as f_info:
        for line in f_info.readlines():
            if line.startswith("diff"):
                # 从这里获取目标子路径
                # 示例：source/org/jfree/chart/util/ShapeUtilities.java
                target_file_subpath = line.split(" ")[2][2:]
                break
            elif line.startswith("Index"):
                target_file_subpath = line.strip().split(" ")[1]

    try:
        backfill_target_path = os.path.join(backfill_target_base_path, target_file_subpath)
    except:
        print("Failed to extract backfill path for proj %s" % bug_id)
    
    return backfill_target_path


########## main ##########

if __name__ == "__main__":
    with open(single_func_bugs_metadata_path, "r", encoding="utf-8") as fj:
        single_func_bug_id_list = json.load(fj)["bug_id"]

    assert len(single_func_bug_id_list) == 483
    
    all_backfill_target_path = {}
    
    # 开始遍历每一个项目
    for bug_id in tqdm(single_func_bug_id_list):
        proj, id = bug_id.split("-")
        # print("now extracting path for proj %s id %s" % (proj, id))
        
        # 提取出的 fixed_reply 作为将要回填的代码！
        # 在此之前相当于一直在做提取代码的工作
        backfill_target_path = extract_target_file_path(bug_id)
        
        all_backfill_target_path[bug_id] = backfill_target_path
        
    with open(save_backfill_path, "w", encoding="utf-8") as f_path:
        json.dump(all_backfill_target_path, f_path, indent=4)