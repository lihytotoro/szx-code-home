# 测试一下：哪些 bug 没有被正确地提取出测试信息
import os
import json

dir_list = os.listdir(".")

dir_list = [item for item in dir_list if not item.endswith(".csv") and not item.endswith(".py") and not item.endswith(".json")]
assert len(dir_list) == 17

error_bugs = []

for dir in dir_list:
    subpath = os.path.join(".", dir)
    subdir_list = os.listdir(subpath)
    for subdir in subdir_list:
        subsubpath = os.path.join(subpath, subdir)
        files = os.listdir(subsubpath)
        if len(files) == 0:
            error_bugs.append(dir + "-" + subdir)
        elif len(files) == 3:
            continue
        else:
            raise Exception("error!")

print("number of failed bugs:", len(error_bugs))
with open("./failed_to_extract_test_info_bugs.json", "w") as f:
    error_bugs_dict = {"failed_test_info_bugs":error_bugs}
    json.dump(error_bugs_dict, f)