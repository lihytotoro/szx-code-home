# 将 jsonl 又转回了 parquet？为了方便训练！
import json
import jsonlines
import pandas as pd

input_list = []
output_list = []

# 新版本数据
# 这次是完全不含 comment 和 空行 的版本，共 48946 条
load_path = "./output/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_repairllama.jsonl"
save_path = "/vepfs/lihy/dataset/megadiff-single-function/train_maxlen_1024_wo_comment_wo_initial_prompt.parquet"

with open(load_path, "r+", encoding="utf-8") as f:
    for item in jsonlines.Reader(f):
        input_text = item["input"]
        output_text = item["output"]
        input_list.append(input_text)
        output_list.append(output_text)
        
print(len(input_list), len(output_list))

df = pd.DataFrame({"input":input_list, "output":output_list})

df.to_parquet(save_path, index=False)