# 这个文件复制了 llama_pred（原始版本 repairllama 预测修复代码）
# 目的：输入 bad code（juliet-java），得到 cwe 类型

# 0503 new: 这是原来的推理代码（基于 repairllama 的版本），输入为 之前预处理过的 defects4j jsonl，输出为对应的 483 * 10 个回复。
# 示例输出文件：

import json
import jsonlines
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
import os

import torch
import transformers
from peft import PeftModel
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GenerationConfig, 
    HfArgumentParser, 
    BitsAndBytesConfig,
)
from tqdm import tqdm

# 仍然按照 train 的代码，分别定义模型参数、数据参数、生成参数 三部分
# lora_path 应当是训练之后生成的 lora adapter 位置
@dataclass
class ModelArguments:
    # 基础模型
    base_model_path: Optional[str] = field(default="/data/lihy/models/CodeLlama-7b-Instruct-hf")
    # lora adapter
    lora_path: Optional[str] = field(default="/data/lihy/training_output/repairllama/finetuned-models_maxlen=1024_epoch=1_newdata_wo_comment_wo_initial_prompt")
    # 这个好像没用上？实际上是想控制输入序列的长度
    max_length: int = field(default=2048, metadata={"help": "Maximum length of the input sequence."})


@dataclass
class DataArguments:
    # 测试目标文件所在目录
    test_data_dir: str = field(default=None, metadata={"help": "Path to the data path(where the files are in"})
    # 要测试的文件？在 codellama-cwe 任务中，要求包含 input + output（用于检验正确性）
    test_file: str = field(default="defects4j_all_single_func_repairllama_wo_initial_prompt.jsonl", metadata={"help": "Test file name."})
    # 如果测试数据来自于 d4j，那么就是所谓实战，而不是验证微调之后的模型（juliet-java）
    test_file_from_d4j: bool = field(default=False, metadata={"help": "Test file from d4j or not."})
    # 如果该数据来自于 java-juliet-test，那么截取一定数目的行，进行测试
    row_cnt_from_juliet: int = field(default=200, metadata={"help": "Number of testcases from java-juliet-test."})
    # 输出 output_patches 到哪个文件之中？
    output_file: str = field(default=None, metadata={"help": "Output file name."})

# 疑问：为什么限制新生成的 token 数目在 256 以内？
# 是不是认为修复一定是小范围的？
@dataclass
class GenerationArguments:
    max_new_tokens: int = field(
        default=1024,
        metadata={"help": "Maximum number of new tokens to generate."},
    )
    is_lora: bool = field(default=True, metadata={"help": "Whether to use LORA."})
    # 应该是控制是否进行 sampling
    do_sample: bool = field(default=True, metadata={"help": "Whether to use sampling."})
    # 只进行 beam-search
    only_do_beam: bool = field(default=False, metadata={"help": "Whether to only use beam search."})
    # 只进行 top-p 搜索？
    only_do_topp: bool = field(default=False, metadata={"help": "Whether to only use top-p sampling."})
    # 只进行 top-k 搜索？
    only_do_topk: bool = field(default=False, metadata={"help": "Whether to only use top-k sampling."})
    # 温度搜索
    only_do_temp: bool = field(default=False, metadata={"help": "Whether to only use temperature sampling."})
    # 集束宽度，即一次生成多少样本
    num_beams: int = field(default=1, metadata={"help": "Number of beams for beam search. 1 means no beam search."})
    temperature: float = field(default=1.0, metadata={"help": "Temperature for sampling."})
    top_k: int = field(default=50, metadata={"help": "Top-k for sampling."})
    top_p: float = field(default=1.0, metadata={"help": "Top-p for sampling."})
    # 这是什么意思？在 sh 里也设置成了 10
    request_num: int = field(default=1, metadata={"help": "Number of requests."})
    # 每个 bug 有多少请求？
    sub_request_num: int = field(default=10, metadata={"help": "Number of requests for each bug."})

# 主函数
def main():
    # 先载入三部分参数
    parser = HfArgumentParser((ModelArguments, DataArguments, GenerationArguments))
    # 分别指派变量接收这些参数
    model_args, data_args, generation_args = parser.parse_args_into_dataclasses()

    print("max input len:", model_args.max_length)
    print("max new tokens:", generation_args.max_new_tokens)
    print("output path:", data_args.output_file)

    # 使用 lora，重点注意这部分内容
    if generation_args.is_lora:
        # 先定义原始模型
        model = AutoModelForCausalLM.from_pretrained(
            model_args.base_model_path,
            torch_dtype=torch.float16,
            load_in_8bit=True,
            trust_remote_code=True,
            quantization_config=BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            ),
            # 这个应该是管模型并行的
            device_map='auto',
        )

        # 加入 lora 部分，这里是 lora_path 的主要作用域
        model = PeftModel.from_pretrained(
            model,
            model_args.lora_path,
            torch_dtype=torch.float16,
        )
    # 全量微调部分
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_args.base_model_path,
            torch_dtype=torch.float16,
        )
        
    # 定义 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_args.base_model_path, trust_remote_code=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    # 将 model 和 tokenizer 中的 pad_token 同时设置为 unk_token
    model.config.pad_token = tokenizer.pad_token = tokenizer.unk_token
    model.to(device)
    
    # 这个 分支 处理了 beam_search 等内容，即一次针对一个 bug 生成多个修复结果
    if generation_args.do_sample:
        if generation_args.only_do_beam:
            # Beam search
            print("We now use beam search to generate the patches.")
            # the generation stops as soon as there are num_beams complete candidates
            generation_config = GenerationConfig(
                num_beams=generation_args.num_beams,
                early_stopping=True,
            )
        else:
            # The combination of Top-k & Top-p & Temperature sampling
            print("We now use sampling strategies to generate the patches.")
            generation_config = GenerationConfig(
                do_sample=generation_args.do_sample,
                temperature=generation_args.temperature if generation_args.only_do_temp else None,
                top_k=generation_args.top_k if generation_args.only_do_topk else None,
                top_p=generation_args.top_p if generation_args.only_do_topp else None,
            )

    # buggy_code 的列表，如果是单个，为什么还要搞一个 list 呢？
    buggy_code_list = []
    # llama 生成的列表？
    llama2_output = []
    # 从测试样本所在的路径，找到所有需要测试的文件
    test_data_dir = Path(data_args.test_data_dir)
    
    # 这里是读取数据部分，要分 json 和 parquet 两种情况考虑！
    # jsonl 是指？d4j 数据集的数据格式是 jsonl，而 java-juliet-test 数据集的格式是 parquet
    if data_args.test_file.endswith(".jsonl"):
        with jsonlines.open(test_data_dir / data_args.test_file, 'r') as reader:
            # 每一行是一个测试样例，并且期望整理成 json 格式
            for sample in reader:
                assert type(sample) == dict
                buggy_code_list.append(sample)
    elif data_args.test_file.endswith(".parquet"):
        # 按照 parquet（dataframe）的格式进行读取
        df_read_ori = pd.read_parquet(os.path.join(test_data_dir, data_args.test_file))
        # 截取一定数量的行进行测试！
        df_read = df_read_ori.iloc[:data_args.row_cnt_from_juliet,:]
        for row_idx, row in df_read.iterrows():
            input_code = row["input"]
            output_cwe = row["output"]
            sample = {"input":input_code, "output":output_cwe}
            buggy_code_list.append(sample)
    
    # If we want to generate 100 patches for a bug, we need to generate 10 times due to the limited GPU resources.
    if generation_args.only_do_temp or generation_args.only_do_topk or generation_args.only_do_topp:
        gen_epoch = int(generation_args.request_num / generation_args.sub_request_num)

    # 开始生成
    # 每一个 sample 生成多个样本（预设 10 个）
    # sample 要求的键：bug_id、buggy_code、fixed_chunk
    for sample in tqdm(buggy_code_list, desc="Generating..."):
        tmp_dict = {}
        
        # 如果数据是来源于 d4j（实战），那么前面还缺一句前缀！
        if data_args.test_file_from_d4j:
            system = "You are a powerful automatic program repair assistant with plenty of knowledge about common weakness enumeration(CWE). Provide your answer in Markdown, in which you should include the exact CWE type of the flaw in the provided code and the definition of this CWE."
            user_buggy_code_prefix = "Buggy Code:\n"
            user_question_prefix = "Question:\n"
            user_question_content = "The previous java code contains a flaw. What is the exact CWE(common weakness enumeration) type of the flaw? What is the definition of this CWE type? Give your answer in the same format as the following example.\n"
            user_example_prefix = "Answer Example:\n"
            user_example_content_1 = "The CWE type of the code is: CWE129--Improper Validation of Array Index. "
            user_example_content_2 = "The description of CWE129 is: The product uses untrusted input when calculating or using an array index, but the product does not validate or incorrectly validates the index to ensure the index references a valid position within the array.\n"
            user_your_answer_prefix = "Your Answer:"

            user = user_buggy_code_prefix + sample["input"] + "\n" + user_question_prefix + user_question_content + user_example_prefix + \
                user_example_content_1 + user_example_content_2 + user_your_answer_prefix
                
            total_input = f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user}[/INST]"
        else:
            # 进入这个分支，是指用于推理的是 java-juliet 数据集的测试集（.parquet）
            # 这里是指：由于处理 java-juliet 数据集时，已经提前加上了各种修饰，因此不需要再加一遍了
            total_input = sample["input"]

        # 将输入转换为 token 序列
        inputs = tokenizer(total_input, return_tensors='pt')
        inputs_len = inputs.input_ids.shape[1]
        input_ids = inputs.input_ids.to(device)

        # beam search
        if generation_args.only_do_beam:
            try:
                with torch.no_grad():
                    # 一次可以生成多个例子
                    outputs = model.generate(
                        input_ids=input_ids,
                        max_new_tokens=generation_args.max_new_tokens,
                        num_return_sequences=generation_args.request_num,
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id,
                        generation_config=generation_config,
                    )
            except Exception as e:
                print("Exception:{}.".format(e))
                continue
            # 输出在最开始时是包含 input_ids 的，要截断
            output_ids = outputs[:, inputs_len:]

            # decode，还原到真实代码
            # 其中，output_diff 应该是还原的真实代码
            # original_outputs 是包含输入的所有部分
            output_diff = tokenizer.batch_decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
            original_outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False)

            # output 字典，重点：结构是什么？
            output_dict = {}

            # 生成的可能是多个样本，逐个进行处理！
            for i in range(len(output_diff)):
                output_dict[i] = {
                    "original_output": original_outputs[i],
                    "output_patch": output_diff[i],
                }
            
            # 最上层返回结构，按每个 buggy sample 构造一个字典
            if data_args.test_file_from_d4j:
                # 如果是 d4j（真实数据集），那么没有 gold cwe
                tmp_dict['bug_id'] = sample['bug_id']
                tmp_dict["output"] = output_dict
                tmp_dict['total_input'] = total_input
            else:
                tmp_dict['output'] = output_dict
                tmp_dict['total_input'] = total_input
                tmp_dict['gold_cwe'] = sample['output']

            llama2_output.append(tmp_dict)
        # 以下这个分支表示：不做 beam_search，而是 greedy_serach，涉及 top_p、top_k 等参数
        else:
            temp_list = []
            for _ in range(gen_epoch):
                try:
                    with torch.no_grad():
                        outputs = model.generate(
                            input_ids=input_ids,
                            max_new_tokens=generation_args.max_new_tokens,
                            num_return_sequences=generation_args.sub_request_num,
                            pad_token_id=tokenizer.pad_token_id,
                            eos_token_id=tokenizer.eos_token_id,
                            generation_config=generation_config,
                        )
                except Exception as e:
                    print("Exception:{}.".format(e))
                    break
                output_ids = outputs[:, inputs_len:]

                output_diff = tokenizer.batch_decode(output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
                original_outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False)
                temp_list.append((original_outputs, output_diff))

            output_dict = {}

            for i in range(len(temp_list)):
                for j in range(len(temp_list[i][1])):
                    output_dict[i*10+j] = {
                        "original_output": temp_list[i][0][j],
                        "output_diff": temp_list[i][1][j],
                    }
            
            if data_args.test_file_from_d4j:
                tmp_dict['bug_id'] = sample['bug_id']
                tmp_dict['output'] = output_dict
                tmp_dict['total_input'] = total_input
            else:
                tmp_dict['output'] = output_dict
                tmp_dict['total_input'] = total_input
                tmp_dict['gold_cwe'] = sample['output']

            if len(output_dict) == generation_args.request_num:
                llama2_output.append(tmp_dict)

    # 对获取的所有字典进行输出。应该是个 json
    with jsonlines.open(data_args.output_file, 'w') as writer:
        for each in llama2_output:
            writer.write(each)

# 实际上输出的是所有候选修复 patch，不负责检测
if __name__ == "__main__":
    main()

