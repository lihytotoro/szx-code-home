# 直接复制之前 defects4J 那里使用到的关于调用 codellama 生成回复的代码
from typing import Optional
import fire
import os
import sys

# 引入 codellama 模型所在的路径
sys.path.append("/data/lihy/codellama/codellama")

from llama import Llama

def main(
    ckpt_dir: str,
    tokenizer_path: str,
    buggy_path: str,
    temperature: float = 0.2,
    top_p: float = 0.95,
    max_seq_len: int = 2048,
    max_batch_size: int = 32,
    max_gen_len: Optional[int] = None,
):
    print("start building generator!")
    
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    # 对每一个 bug 构建 instruction，然后添加到下面的列表中
    
    instructions = []
    
    # 针对当前 test case，构建 prompt
    prompt_1 = "The following code is written in C++ and contains a bug.\n"
    prompt_2 = "Which Common Weakness Enumeration class(CWE) does this bug belong to?\n"
    buggy_code = ""
    
    with open(buggy_path, "r", encoding="utf-8") as f_buggy:
        for buggy_line in f_buggy.readlines():
            buggy_code += buggy_line
    
    prompt = prompt_1 + buggy_code + prompt_2
    
    # print("\n")
    # print(prompt)
    # print("\n")
    instruction = [
        {
            "role": "user",
            "content": prompt,
        },
    ]
    instructions.append(instruction)
    
    # 生成回复
    results = generator.chat_completion(
        instructions,  # type: ignore
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )

    print("finish generating results!")

    # 这里是：对于每条 instruct 以及对应生成出来的 result，进行相应处理
    # 只要 zip 不报错，说明二者的长度就是相等的
    for instruction, result in zip(instructions, results):
        model_reply = result['generation']['content']
        print(model_reply)

# 目前，我大概看了下 code-llama 在解决基本的 bug 上的能力（起码输出是正常的）。我需要额外确认一下，如何进行带历史记录的多轮对话。（up to 10000 tokens?）

if __name__ == "__main__":
    fire.Fire(main)