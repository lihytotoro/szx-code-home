# 看看三种 bug 分别有多少

import json

# with open("../file_hash.json", "r") as f:
#     d = json.load(f)
    
# proj_dict = {}    
    
# for k, v in d.items():
#     proj_id = k.split("-")
#     proj = proj_id[0]
#     id = proj_id[1]
#     if proj not in proj_dict:
#         proj_dict[proj] = [id]
#     else:
#         if not id in proj_dict[proj]:
#             proj_dict[proj].append(id)

# for k, v in proj_dict.items():
#     print("%s:\t%s" % (k, len(v)))
    
# l = proj_dict["Lang"]
# for i in range(1, 66):
#     if not str(i) in l:
#         print(i)

##########

# with open("../single_function_repair.json", "r") as f:
#     d = json.load(f)

# # print(len(d))

# # total: 835 = 391 + 444

# # 483 = 255 + 228
# 注意，在作者使用 chatgpt 的实验中，2.0 版本的 single function 的 228 个 bug 中，只选了  82 个进行实验
# # 313 = 154 + 159
# # 158 = 80 + 78

# valid_bugs = []

# for k, v in d.items():
#     valid_bugs.append(k)
    
# print(len(valid_bugs))

# valid_bugs_dict = {"bug_id":valid_bugs}

# with open("../../../../../defects4j/metadata/single_func_bugs.json", "w") as fw:
#     json.dump(valid_bugs_dict, fw)
    
##########

import json

with open("../single_function_repair.json", "r") as f:
    d = json.load(f)
    
print(len(d))