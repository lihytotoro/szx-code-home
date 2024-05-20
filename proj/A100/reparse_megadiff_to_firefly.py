import jsonlines

conv_id = 1
ans_json_list = []

with jsonlines.open("./output/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_firefly.jsonl", "r") as reader:
    for obj in reader:
        input_code = obj["input"]
        output_code = obj["output"]
        
        conversation = [{"human": input_code, "assistant": output_code}]
        conversation_id = conv_id
        conv_id += 1
        dataset = "MegaDiff"
        
        json_sample = {"conversation_id": conversation_id, "category": "Brainstorming", "conversation": conversation, "dataset": dataset}
        
        ans_json_list.append(json_sample)
        
with jsonlines.open("../../github-proj/Firefly/data/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_firefly.jsonl", "w") as writer:
    for js_sample in ans_json_list:
        writer.write(js_sample)
with jsonlines.open("./output/finetuning_conversation_data_total_1024_sf_wo_comment_wo_initial_prompt_firefly.jsonl", "w") as writer:
    for js_sample in ans_json_list:
        writer.write(js_sample)