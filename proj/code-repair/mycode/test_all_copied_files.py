# 测试所有 483 个文件能不能读取！
import json

backfill_path_path = "./output/single_func/backfill_path_6.json"

with open(backfill_path_path, "r", encoding="utf-8") as fb:
    backfill_path = json.load(fb)

# 逐个测试读取
for bug_id, target_path in backfill_path.items():
    print("reading proj %s" % bug_id)
    with open(target_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
print(len(backfill_path))