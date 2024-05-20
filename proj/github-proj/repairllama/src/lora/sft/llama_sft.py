# coding=utf-8
# Implements parameter-efficient or full parameters supervised fine-tuning for LLaMa model.
# This code is inspired by
# https://github.com/tatsu-lab/stanford_alpaca/blob/main/train.py and https://www.mlexpert.io/machine-learning/tutorials/alpaca-fine-tuning

# 这个应该是作者 lora fine tune 代码的版本了
# Supervised Fine-Tuning

# 0227 更新：注意如何从中途的 checkpoint 恢复训练！
# 要从检查点恢复，请将 resume_from_checkpoint 设置为要从中恢复的 adapter_model.bin 的路径：

import transformers
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForSeq2Seq,
    Trainer,
    Seq2SeqTrainer,
    HfArgumentParser,
    Seq2SeqTrainingArguments,
    BitsAndBytesConfig,
)

from peft import (
    LoraConfig,
    PeftModel,
    get_peft_model,
    get_peft_model_state_dict,
    prepare_model_for_int8_training,
    prepare_model_for_kbit_training,
    set_peft_model_state_dict,
)

import torch
import os
import evaluate
import functools
from datasets import load_dataset
import bitsandbytes as bnb
import logging
import json
import copy
from typing import Dict, Optional, Sequence
from dataclasses import dataclass, field


# Lora settings: rank, alpha, dropout
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT= 0.05
# 一般是一个字符串列表，每一个字符串是需要进行 LoRA 的层名称
LORA_TARGET_MODULES = [
    "q_proj",
    "v_proj",
]

# 在这里修改模型路径，注意这里用的是 huggingface 版本
@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="/data/lihy/codellama/CodeLlama-7b-Instruct-hf")
    # 这个是指：如果要在微调的基础上再次微调，那么应该从哪里找到上一次的 lora adapter 位置
    lora_path: Optional[str] = field(default="/data/lihy/training_output/repairllama/finetuned-models_maxlen=1024_epoch=2_newdata_wo_comment_wo_initial_prompt")
    # 这个路径是指：如果需要从中途载入模型的话，选择的 ckpt 的 adapter_model.bin 的位置
    # 只有在 resume_from_checkpoint 为 True 的时候才起作用
    resume_model_path: Optional[str] = field(default="/data/lihy/training_output/codellama-cwe/finetuned-models_maxlen=1024_cwe-desc=true_verbose-prompt=true_epoch=5_juliet-files=2/checkpoint-1800/adapter_model.bin")

# 在这里修改数据参数，现在还没搞明白 data_path 和 train_file、eval_file 之间的区别
# 这里定义了几个 sh 文件里没有声明的 path 参数
@dataclass
class DataArguments:
    data_path: str = field(default=None, metadata={"help": "Path to the data path(where the files are in)."})
    train_file: str = field(default=None, metadata={"help": "Path to the train data files."})
    eval_file: str = field(default=None, metadata={"help": "Path to the evaluation data files."})
    cache_path: str = field(default=None, metadata={"help": "Path to the cache directory."})
    num_proc: int = field(default=4, metadata={"help": "Number of processes to use for data preprocessing."})

# 这里定义了训练参数
# 包括 优化器、模型的最大长度限制、是否使用 LoRA 进行微调
# 这里强调：微调时，序列会被 right padded，研究一下左右 pad 有什么区别
@dataclass
class TrainingArguments(transformers.TrainingArguments):
    # cache_dir: Optional[str] = field(default=None)
    optim: str = field(default="adamw_torch")
    # adam_beta1: float = field(default=0.9)
    # adam_beta2: float = field(default=0.95)
    model_max_length: int = field(
        default=1024,
        metadata={"help": "Maximum sequence length. Sequences will be right padded (and possibly truncated)."},
    )
    is_lora: bool = field(default=True, metadata={"help": "Whether to use LORA."})
    from_lora: bool = field(default=False, metadata={"help": "Whether to use LORA-finetuned model."})
    # 是否从某个 ckpt 开始载入，继续未完成的训练
    resume_from_checkpoint: bool = field(default=False, metadata={"help":"Whether to continue training from a certain checkpoint."})

# 这里定义了如何 tokenize 输入序列
# 这里 max_seq_len 似乎指的是 token 的长度，而不是序列本身的长度
def tokenize(text, tokenizer, max_seq_len=4096, add_eos_token=True):
    result = tokenizer(
        text,
        truncation=False,
        max_length=max_seq_len,
        padding=False,
        return_tensors=None,
    )

    # If the tokenized length exceeds the max_seq_len, return None
    # 如果超出了 max_seq_len，返回一个空值
    if len(result["input_ids"]) >= max_seq_len:
        return None

    # 如果长度允许，在最后再加上 eos_token
    if (
        result["input_ids"][-1] != tokenizer.eos_token_id
        and len(result["input_ids"]) < max_seq_len
        and add_eos_token
    ):
        result["input_ids"].append(tokenizer.eos_token_id)
        result["attention_mask"].append(1)

    # if add_eos_token and len(result["input_ids"]) >= max_seq_len:
    #     result["input_ids"][max_seq_len - 1] = tokenizer.eos_token_id
    #     result["attention_mask"][max_seq_len - 1] = 1

    # 还没搞清楚为什么 labels 是原封不动 copy input_ids
    result["labels"] = result["input_ids"].copy()
    return result

# 主函数
def main():
    parser = HfArgumentParser((ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    # 使用 lora 进行微调，因此重点关注这个分支
    if training_args.is_lora:
        # from_lora 为 True 时，表示需要进行二轮微调，这主要用在 repairllama-cwe 任务中
        if training_args.from_lora:
            model = AutoModelForCausalLM.from_pretrained(
                model_args.model_name_or_path,
                cache_dir=data_args.cache_path,
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
            
            # 准备训练！
            model = prepare_model_for_kbit_training(model)
            
            # 新一轮 lora 的参数
            config = LoraConfig(
                r=LORA_R,
                lora_alpha=LORA_ALPHA,
                target_modules=LORA_TARGET_MODULES,
                lora_dropout=LORA_DROPOUT,
                bias="none",
                task_type="CAUSAL_LM",
            )
            model = get_peft_model(model, config)
            
            # 如果从检查点进行恢复（继续中断的训练）
            if training_args.resume_from_checkpoint:
                if os.path.exists(model_args.resume_model_path):
                    print(f"Restarting from {model_args.resume_model_path}")
                    adapters_weights = torch.load(model_args.resume_model_path)
                    set_peft_model_state_dict(model, adapters_weights)
                else:
                    print(f"Checkpoint {model_args.resume_model_path} not found")
        # 在单纯的一轮微调以及 codellama-cwe 任务中，关注这个分支
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_args.model_name_or_path,
                cache_dir=data_args.cache_path,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                load_in_8bit=True,
                quantization_config=BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0
                ),
            )
            # PEFT 提供的方法
            model = prepare_model_for_kbit_training(model)

            # lora 的参数
            config = LoraConfig(
                r=LORA_R,
                lora_alpha=LORA_ALPHA,
                target_modules=LORA_TARGET_MODULES,
                lora_dropout=LORA_DROPOUT,
                bias="none",
                task_type="CAUSAL_LM",
            )
            model = get_peft_model(model, config)
            
            # 如果从检查点进行恢复（继续中断的训练）
            if training_args.resume_from_checkpoint:
                if os.path.exists(model_args.resume_model_path):
                    print(f"Restarting from {model_args.resume_model_path}")
                    adapters_weights = torch.load(model_args.resume_model_path)
                    set_peft_model_state_dict(model, adapters_weights)
                else:
                    print(f"Checkpoint {model_args.resume_model_path} not found")
    # 这个分支表示全量微调
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_args.model_name_or_path,
            torch_dtype=torch.float16,
            cache_dir=data_args.cache_path,
            trust_remote_code=True,
        )
    model.config.use_cache = False

    # 输出可训练的参数量
    def print_trainable_parameters(model):
        """
        Prints the number of trainable parameters in the model.
        """
        trainable_params = 0
        all_param = 0
        for _, param in model.named_parameters():
            all_param += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()
        print(
            f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
        )
    # 在 lora 模式下，调用上面的函数，看看比例多少
    if training_args.is_lora:
        print_trainable_parameters(model)

    # 构建 tokenizer
    # padding_side 设置的作用是指定 tokenizer 添加填充标记(padding)的位置
    # encoder-only 模型的填充一般是right-padding
    # only-decoder 的 LLM 采用 left padding
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=data_args.cache_path,
        model_max_length=training_args.model_max_length,
        padding_side="left",
        trust_remote_code=True,
        use_fast=True,
    )
    # 注意，这里为什么设置成了 unk_token，而不是 end_token？
    tokenizer.pad_token = tokenizer.unk_token

    # Load dataset
    def generate_and_tokenize_prompt(sample):
        # 从下面的格式可以看出，sample 要求必须有 input 和 output 两项
        input_text = sample["input"]
        target_text = sample["output"] + tokenizer.eos_token
        full_text = input_text + target_text

        # 这个字典应当包含 input_ids、attention_mask 以及 labels 三项！
        tokenized_full_text = tokenize(full_text, tokenizer, max_seq_len=training_args.model_max_length)

        if tokenized_full_text is None:
            # Return a null sample if the tokenized length exceeds the max_seq_len
            # 0111 阅读代码进度
            
            return {"input_ids": [], "attention_mask": [], "labels": []}

        tokenized_input_text = tokenize(input_text, tokenizer, max_seq_len=training_args.model_max_length)
        input_len = len(tokenized_input_text["input_ids"]) # This is a bug of llamatokenizer that it does not add eos token
        # 这句是什么意思？首先 input 都用 -100，然后后面的部分直接用 tokenized_full_text 中 target_text 的部分代替
        tokenized_full_text["labels"] = [-100] * input_len + tokenized_full_text["labels"][input_len:]
        return tokenized_full_text

    # 这里定义了 train_file、eval_file 的用法 —— data_file 的键值
    data_files = {}
    if data_args.train_file is not None:
        data_files["train"] = data_args.train_file
    if data_args.eval_file is not None:
        data_files["eval"] = data_args.eval_file

    # 调用，第一个参数是 路径，第二个参数是 包含了 train 和 eval 两个键的字典？
    # 注意：针对 parquet 有专门的读取方式。但是我们不一定要使用原始的数据
    # data_files = {"train":"train.parquet", "test":"train.parquet"}
    dataset = load_dataset("parquet", data_dir=data_args.data_path, data_files=data_files, cache_dir="/data/lihy/training_output/codellama-cwe/cache")
    
    # dataset = load_dataset(data_args.data_path, data_files=data_files)
    # 训练集和测试集
    train_dataset = dataset["train"]
    eval_dataset = dataset["eval"]

    # 输出数据集的名称，name 需要作为参数指定
    def print_dataset_length(dataset, name):
        print(f"Number of samples in {name} dataset after filtering: {len(dataset)}")

    # 对 dataset 进行 tokenize 操作
    train_dataset = train_dataset.map(generate_and_tokenize_prompt, num_proc=data_args.num_proc)
    eval_dataset = eval_dataset.map(generate_and_tokenize_prompt, num_proc=data_args.num_proc)
    # Filter null samples
    # 过滤条件：对于 tokenize 之后的样本，如果 input_ids 是一个空 list，即认定为无效样本
    train_dataset = train_dataset.filter(lambda sample: len(sample["input_ids"]) > 0)
    eval_dataset = eval_dataset.filter(lambda sample: len(sample["input_ids"]) > 0)

    # 输出过滤之后的样本数目
    print_dataset_length(train_dataset, "train")
    print_dataset_length(eval_dataset, "eval")

    # 定义了一个数据收集器，data_collator的作用就是将features特征数据转换为tensor类型的dataset
    # pad_to_multiple_of 表示填充的序列的倍数（填充完的序列长度一定是 8 的倍数？）
    # padding 表示填充至最大序列长度
    data_collator = DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt", padding=True)

    # Evaluation metrics
    # 这里是传入 Trainer 类的 computer_metrics 参数的函数，似乎是用来计算预测值和真实值之间的某种指标的？
    # 必须传入 EvalPrediction 并将返回一个字典，键值对是 metric 和其 value
    # eval_preds 是啥呢？必须传入 EvalPrediction 参数。 EvalPrediction是一个具有 predictions 字段和 label_ids 字段的元组
    def compute_metrics(eval_preds, tokenizer):
        # 使用 完全匹配 ？
        metric = evaluate.load('exact_match')
        # predictions 和 label_ids（golden_truth）
        preds, labels = eval_preds
        # In case the model returns more than the prediction logits
        # 如果预测返回的不止一个参数，那么默认第一个是返回的序列
        if isinstance(preds, tuple):
            preds = preds[0]

        # 返回的是 token 序列，对其进行 decode，复原出原始序列
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        # Replace -100s in the labels as we can't decode them
        # 刚刚，在 full_text 的返回值中，input 部分的 token 都给了 -100
        # 因此，在对 labels 也就是 gt 进行复原时，忽略这些 -100
        labels[labels == -100] = tokenizer.pad_token_id
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        # Some simple post-processing
        # 后处理部分，去掉空白格
        decoded_preds = [pred.strip() for pred in decoded_preds]
        decoded_labels = [label.strip() for label in decoded_labels]

        # 使用现成的字符串匹配指标
        result = metric.compute(predictions=decoded_preds, references=decoded_labels)
        # 返回值是一个字典，键值对是 key：metric 名字（string 类型），value：metric 值（float 类型）
        return {'exact_match': result['exact_match']} 

    # 相当于包装了上面的函数，帮助我们事先确定了 tokenizer 参数
    compute_metrics_fn = functools.partial(compute_metrics, tokenizer=tokenizer)

    # Training
    # 训练部分？参数包括：模型、训练数据集、验证数据集、训练参数、数据收集器（用于将 List 转化为 torch.tensor）、计算指标的额外函数
    trainer = Trainer(
        model=model, 
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,  
        args=training_args,
        data_collator=data_collator,
        compute_metrics=compute_metrics_fn,
    )
    trainer.train()
    
    # 保存模型？
    trainer.save_state()
    trainer.save_model(output_dir=training_args.output_dir)
    # 保存 tokenizer 的参数？
    tokenizer.save_pretrained(save_directory=training_args.output_dir)


if __name__ == "__main__":
    main()

