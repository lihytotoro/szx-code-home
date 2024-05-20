import json
import jsonlines
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

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
    base_model_path: Optional[str] = field(default="/data/lihy/models/CodeLlama-7b-Instruct-hf")
    lora_path: Optional[str] = field(default="/data/lihy/training_output/repairllama/finetuned-models_maxlen=1024_epoch=1_newdata_wo_comment_wo_initial_prompt")
    max_length: int = field(default=2048, metadata={"help": "Maximum length of the input sequence."})


@dataclass
class DataArguments:
    data_path: str = field(default=None, metadata={"help": "Path to the data path(where the files are in"})
    # 要测试的文件？buggy code？output 中应当包含了
    test_file: str = field(default="test.json", metadata={"help": "Test file name."})
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
    data_path = Path(data_args.data_path)
    with jsonlines.open(data_path / data_args.test_file, 'r') as reader:
        # 每一行是一个测试样例，并且期望整理成 json 格式
        for sample in reader:
            assert type(sample) == dict
            buggy_code_list.append(sample)
    
    # If we want to generate 100 patches for a bug, we need to generate 10 times due to the limited GPU resources.
    if generation_args.only_do_temp or generation_args.only_do_topk or generation_args.only_do_topp:
        gen_epoch = int(generation_args.request_num / generation_args.sub_request_num)

    # 开始生成
    # 每一个 sample 生成多个样本（预设 10 个）
    # sample 要求的键：bug_id、buggy_code、fixed_chunk
    for sample in tqdm(buggy_code_list, desc="Generating..."):
        tmp_dict = {}
        buggy_code = sample["input"]

        # 将输入转换为 token 序列
        inputs = tokenizer(buggy_code, return_tensors='pt')
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
                print("Bug:{}\t Exception:{}.".format(sample['bug_id'], e))
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
            tmp_dict['bug_id'] = sample['bug_id']
            tmp_dict['output'] = output_dict
            tmp_dict['buggy_code'] = buggy_code
            tmp_dict['gold_patch'] = sample['fixed_chunk']

            llama2_output.append(tmp_dict)
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
                    print("Bug:{}\t Exception:{}.".format(sample['bug_id'], e))
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
            
            tmp_dict['bug_id'] = sample['bug_id']
            tmp_dict['output'] = output_dict

            if len(output_dict) == generation_args.request_num:
                llama2_output.append(tmp_dict)

    # 对获取的所有字典进行输出。应该是个 json
    with jsonlines.open(data_args.output_file, 'w') as writer:
        for each in llama2_output:
            writer.write(each)

# 实际上输出的是所有候选修复 patch，不负责检测
if __name__ == "__main__":
    main()

