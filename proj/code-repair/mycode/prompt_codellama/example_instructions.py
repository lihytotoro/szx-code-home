# 使用 utils 中构建好的 prompt，按照 codellama 的用法样例，给出每个 bug 的回复！
from typing import Optional
import fire
import os
import sys

sys.path.append("/data/lihy/codellama/codellama")

from llama import Llama

from utils import clean_parse_d4j_single_line, clean_parse_d4j_single_hunk, clean_parse_d4j_single_func, \
                    clean_parse_d4j_test_info_single_line, clean_parse_d4j_test_info_single_hunk, clean_parse_d4j_test_info_single_func, \
                        construct_initial_prompt, \
                            single_line_code_path, single_hunk_code_path, single_func_code_path, \
                                test_info_path, output_reply_path, \
                                    single_line_metadata_path, single_hunk_metadata_path, single_func_metadata_path

def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.2,
    top_p: float = 0.95,
    max_seq_len: int = 2048,
    max_batch_size: int = 32,
    max_gen_len: Optional[int] = None,
    original_idx: int = 0,
    stop_idx: int = 470,
):
    print("start building generator!")
    
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    # 对每一个 bug 构建 instruction，然后添加到下面的列表中
    cleaned_single_func_code_result = clean_parse_d4j_single_func(single_func_code_path)
    assert len(cleaned_single_func_code_result) == 483
    print("finished getting original buggy code!")
    cleaned_single_func_test_result, single_func_bug_id_list = clean_parse_d4j_test_info_single_func(test_info_path, single_func_metadata_path)
    assert len(cleaned_single_func_test_result) == 470
    print("finished getting original test info!")
    
    for start_idx in range(original_idx, stop_idx, max_batch_size):
        end_idx = min(start_idx + max_batch_size, stop_idx)
        print("generating for bug idx %d to %d" % (start_idx, end_idx - 1))
        real_batch_size = end_idx - start_idx
        instructions = []
        legal_bug_id = []
        
        # 测试版本，先看看前 8/16/32 个如何？
        
        for bug_id in single_func_bug_id_list[start_idx:end_idx]:
            if bug_id in ["Closure-123", "Jsoup-15", "Jsoup-35", "Jsoup-38", "Jsoup-76"]:
                print("skipping bug %s because there are too many tokens to process!" % bug_id)
                continue
            legal_bug_id.append(bug_id)
            proj, id = bug_id.split("-")
            print("now constructing prompt for proj %s id %s" % (proj, id))
            buggy_patch =           cleaned_single_func_code_result[bug_id]["buggy"]
            failing_test_func =     cleaned_single_func_test_result[bug_id]["test_func_name"]
            failing_test_line =     cleaned_single_func_test_result[bug_id]["trigger_codes"]
            test_error_info =       cleaned_single_func_test_result[bug_id]["err_info"]
            prompt = construct_initial_prompt(None, None, buggy_patch, failing_test_func, failing_test_line, test_error_info, buggy_type="func")
            
            # print("\n")
            # print(prompt)
            # print("\n")
            instruction = [
                {
                    "role": "system",
                    "content": "Please provide the answers in Markdown.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
            instructions.append(instruction)
            
        if len(instructions) == 0:
            continue
        
        results = generator.chat_completion(
            instructions,  # type: ignore
            max_gen_len=max_gen_len,
            temperature=temperature,
            top_p=top_p,
        )
        assert len(results) == real_batch_size

        print("fninsh generating results!")

        # 这里是：对于每条 instruct 以及对应生成出来的 result，进行相应处理
        # 只要 zip 不报错，说明二者的长度就是相等的
        for bug_id, result in zip(legal_bug_id, results):
            proj, id = bug_id.split("-")
            model_reply = result['generation']['content']
            # 将回复写入到对应的目录下
            output_reply_subpath = os.path.join(output_reply_path, proj)
            if not os.path.exists(output_reply_subpath):
                os.mkdir(output_reply_subpath)
            output_reply_subsubpath = os.path.join(output_reply_subpath, id + "_func")
            if not os.path.exists(output_reply_subsubpath):
                os.mkdir(output_reply_subsubpath)
            try:
                with open(os.path.join(output_reply_subsubpath, "model_reply_single_func.txt"), "w", encoding="utf-8") as f:
                    f.write(model_reply)
            except:
                # 记录未能成功写入的 bug_id
                print("bug id %s in proj %s failed to generate reply!" % (id, proj))

# 目前，我大概看了下 code-llama 在解决基本的 bug 上的能力（起码输出是正常的）。我需要额外确认一下，如何进行带历史记录的多轮对话。（up to 10000 tokens?）

if __name__ == "__main__":
    fire.Fire(main)