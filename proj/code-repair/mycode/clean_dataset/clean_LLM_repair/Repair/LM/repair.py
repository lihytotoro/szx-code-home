import argparse
import sys
import torch
import os
import json
import time

########## test ##########
print("running repair!")
# exit()

# 相当于把这两个路径加入路径库中，保证引用的时候不会出错
sys.path.append(os.path.dirname(os.path.join(sys.path[0], '../../')))  # Hack
sys.path.append(os.path.dirname(os.path.join(sys.path[0], '../../Dataset/')))

# 看看作者是怎么用大模型的，可以转换为自己使用 code-llama 的形式
from model import GPT2, SpanLM
from Dataset.parse_quixbugs import parse_python, get_unified_diff, parse_java, parse_java_single_line
# 主要关注这一行的几个 parse 函数
from Dataset.parse_d4j import clean_parse_d4j, clean_parse_d4j_single_hunk, clean_parse_d4j_single_line
from Dataset.parse_manybugs import clean_parse_manybugs, clean_parse_manybugs_single_hunk, clean_parse_manybugs_single_line
from Repair.prompt import JAVA_LONG_VARY_PROMPT, VARY_BASE_PROMPT, C_VARY_PROMPT
from Repair.util import pick_smallest_example_fix, set_seed, _run_validation

# 这个相当于是处理 single_hunk 类型 bug 的单个循环
def suffix_repair_loop(args, model: SpanLM, prefix, suffix, file_name, folder, bug, t_chances, skip_val=True):
    start = time.time()
    repair_result = []
    p_diff = {}
    print("Repairing bug {} ... ".format(file_name.split(".")[0]))
    print(prefix)
    print(">>> [INSERT] <<<")
    print(suffix)
    if not model.check_input(prefix, suffix, bug['buggy']):
        return 0, False, False, repair_result

    total_times = 0
    while t_chances > 0:
        total_times += 1
        torch.cuda.empty_cache()
        print("Try :{}".format(total_times))
        well, early_stop, outputs, entropies = model.model_predict(prefix=prefix, suffix=suffix,
                                                                   do_sample=True,
                                                                   buggy=bug['buggy'],
                                                                   num_samples=t_chances)
        t_chances -= args.batch_size
        if well:
            for index, output in enumerate(outputs):
                output = prefix + output + suffix
                diff = get_unified_diff(bug['buggy'], output)
                if diff in p_diff:
                    repair_result[p_diff[diff]]['num'] += 1
                    continue
                p_diff[diff] = len(repair_result)
                print(diff)
                repair_result.append({'output': output,
                                      'diff': diff,
                                      'finish_reason': 'stop',
                                      'entropy': entropies[index],
                                      'valid': _run_validation(file_name.split(".")[0],
                                                               file_name.split(".")[0] + "_" + str(
                                                                   len(repair_result)) + "." + file_name.split(".")[1],
                                                               folder, output, skip_val=skip_val),
                                      'num': 1})
    end = time.time()
    print("{} Unique Patches Generated in {}s".format(len(repair_result), end - start))

    return total_times, False, False, repair_result

# 这个是处理 single_line 类型 bug 的单一循环
# 先看怎么处理单行的 bug
# args
# model：用于对话的模型
# prefix：prefix = bug['prefix'] + "\n"
# suffix：suffix = "\n" + bug['suffix']
# file_name：Chart-1、Chart-10
# folder：args.folder
# bug：该 bug 的各种信息，是一个字典，包括 prefix、suffix、buggy_line 之类
# t_chances、skip_val 暂时不知道是控制什么的参数，可能是用来控制模型输出的
def single_line_repair_loop(args, model, prefix, suffix, file_name, folder, bug, t_chances, skip_val=True):
    start = time.time()
    # 用于记录修复的结果
    repair_result = []
    # 这个字典是干什么的？
    p_diff = {}
    # 这里，file_name 形似 Chart-1.java
    print("Repairing bug {} ... ".format(file_name.split(".")[0]))
    print(prefix)
    # check_input 应该是检查输入合法性的一个操作
    if not model.check_input(prefix, ""):
        return 0, False, False, repair_result

    # 注意 total_times 的含义
    total_times = 0
    while t_chances > 0:
        total_times += 1
        torch.cuda.empty_cache()
        print("Try :{}".format(total_times))
        
        # 这是涉及到使用大模型进行预测的主要部分
        # input：prefix、buggy_line、以及两个别的参数？
        # output：目前看来 well、outputs 以及 entropies 最重要
        well, length, outputs, entropies = model.model_predict(prefix, bug['buggy'], do_sample=True,
                                                               num_samples=t_chances)
        
        # t_chances 每次预测完毕都需要减去 batch_size，为什么？
        t_chances -= args.batch_size
        if well:
            for index, output in enumerate(outputs):
                output = prefix + output + suffix
                diff = get_unified_diff(bug['buggy'], output)
                if diff in p_diff:
                    repair_result[p_diff[diff]]['num'] += 1
                    continue
                p_diff[diff] = len(repair_result)
                print(diff)
                repair_result.append({'output': output,
                    'diff': diff,
                    'finish_reason': 'stop',
                    'entropy': entropies[index],
                    'valid': _run_validation(file_name.split(".")[0],
                                             file_name.split(".")[0] + "_" + str(
                                                 len(repair_result)) + "." + file_name.split(".")[1],
                                             folder, output, skip_val=skip_val),
                    'num': 1})

    end = time.time()

    print("{} Unique Patches Generated in {}s".format(len(repair_result), end - start))

    return len(repair_result), False, False, repair_result

# 这个应该是处理 single_func 类型 bug 的单一 loop
def repair_loop(args, model, prompt, file_name, folder, bug, t_chances, skip_val=True):
    start = time.time()
    repair_result = []
    p_diff = {}
    print("Repairing bug {} ... ".format(file_name.split(".")[0]))
    print(prompt)
    if not model.check_input(prompt, bug['buggy']):
        return 0, False, False, repair_result

    total_times = 0
    while t_chances > 0:
        total_times += 1
        torch.cuda.empty_cache()
        print("Try :{}".format(total_times))
        well, length, outputs, entropies = model.model_predict(prompt, bug['buggy'], do_sample=True,
                                                               num_samples=t_chances)
        t_chances -= args.batch_size
        if well:
            for index, output in enumerate(outputs):
                diff = get_unified_diff(bug['buggy'], output)
                if diff in p_diff:
                    repair_result[p_diff[diff]]['num'] += 1
                    continue
                p_diff[diff] = len(repair_result)
                print(diff)
                repair_result.append({'output': output,
                                      'diff': diff,
                                      'finish_reason': 'stop',
                                      'entropy': entropies[index],
                                      'valid': _run_validation(file_name.split(".")[0],
                                                               file_name.split(".")[0] + "_" + str(
                                                                   len(repair_result)) + "." + file_name.split(".")[1],
                                                               folder, output, skip_val=skip_val),
                                      'num': 1})

    end = time.time()

    print("{} Unique Patches Generated in {}s".format(len(repair_result), end - start))

    return len(repair_result), False, False, repair_result

# 这个是不是指 single_hunk 类型的 bug 修复？
def suffix_repair(args, model, bugs, folder, chances, skip_val=True):
    """
    Suffix LM repair loop
    :param args: input arguments
    :param model: model to use for repair
    :param bugs: dict of bugs
    :param folder: folder to save the files
    :param chances: number of chances to try to repair
    :param skip_val: if True, skip validation
    :param set_suffix: set prefix for infilling
    :param set_prefix: set suffix for infilling
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + "/args.txt", "w") as f:
        f.write(str(args))

    result = {}
    t_generated = 0
    t_unique = 0
    start_t = time.time()
    for file_name, bug in bugs.items():
        if 'suffix' not in bug:
            continue
        suffix = "\n" + bug['suffix']
        # leading white space removal is needed to help with codet5 prediction since it does not have concept of
        # white spaces
        # leading_white_space = len(bug['buggy'].splitlines()[bug['line_no']]) - len(bug['buggy'].splitlines()[bug['line_no']].lstrip())
        prefix = bug['prefix'] + "\n" #+ " "*leading_white_space
        n_generated, valid, first_try, result[file_name] = suffix_repair_loop(args, model, prefix, suffix,
                                                                                  file_name,
                                                                                  folder, bug,
                                                                                  chances, skip_val)
        if n_generated >= 1:
            t_generated += chances
            t_unique += len(result[file_name])

    end_t = time.time()

    with open(folder + "/stats.txt", "w") as f:
        f.write("Total generated: {}\n".format(t_generated))
        f.write("Total unique: {}\n".format(t_unique))
        f.write("Total time: {}\n".format(end_t - start_t))

    with open(folder + "/lm_repair.json", "w") as f:  # write to file
        json.dump(result, f)


def single_line_repair(args, model, bugs, folder, chances, skip_val):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + "/args.txt", "w") as f:
        f.write(str(args))

    result = {}
    t_generated = 0
    t_unique = 0
    start_t = time.time()
    for file_name, bug in bugs.items():
        if "suffix" not in bug:
            continue

        suffix = "\n" + bug['suffix']
        prefix = bug['prefix'] + "\n"
        n_generated, valid, first_try, result[file_name] = single_line_repair_loop(args, model, prefix, suffix, file_name, folder, bug,
                                                                                   chances, skip_val)
        if n_generated >= 1:
            t_generated += chances
            t_unique += len(result[file_name])

    end_t = time.time()

    with open(folder + "/stats.txt", "w") as f:
        f.write("Total generated: {}\n".format(t_generated))
        f.write("Total unique: {}\n".format(t_unique))
        f.write("Total time: {}\n".format(end_t - start_t))

    with open(folder + "/lm_repair.json", "w") as f:  # write to file
        json.dump(result, f)


def repair(args, model, bugs, folder, used_prompt, chances, skip_val=True, only_same=True):
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + "/prompt.txt", "w") as f:
        f.write(used_prompt)
    with open(folder + "/args.txt", "w") as f:
        f.write(str(args))

    result = {}
    t_generated = 0
    t_unique = 0
    start_t = time.time()
    for file_name, bug in bugs.items():
        if "Collections" in file_name:
            example_bug, example_fix = pick_smallest_example_fix(bugs, file_name, only_same=False)
        else:
            example_bug, example_fix = pick_smallest_example_fix(bugs, file_name, only_same=only_same)
        prompt = used_prompt.format(example_bug=example_bug, example_fix=example_fix, bug=bug['buggy'])
        n_generated, valid, first_try, result[file_name] = repair_loop(args, model, prompt, file_name, folder, bug,
                                                                       chances, skip_val)
        if n_generated >= 1:
            t_generated += chances
            t_unique += len(result[file_name])

    end_t = time.time()

    with open(folder + "/stats.txt", "w") as f:
        f.write("Total generated: {}\n".format(t_generated))
        f.write("Total unique: {}\n".format(t_unique))
        f.write("Total time: {}\n".format(end_t - start_t))

    with open(folder + "/lm_repair.json", "w") as f:  # write to file
        json.dump(result, f)

########## 主函数 ##########
def main():
    parser = argparse.ArgumentParser()
    
    # 用到的大模型
    parser.add_argument("--model_name", type=str, default="EleutherAI/gpt-neo-1.3B")
    # 批处理大小
    parser.add_argument("--batch_size", type=int, default=1)
    # 数据集？可以指定为 defects4j
    parser.add_argument("--dataset", type=str, default="defects4j",
                        help="Dataset to use, current support: defects4j, quixbug-python, quixbugs-java, manybugs")
    # TODO: 这个参数的意义？
    parser.add_argument("--chances", type=int, default=1)
    # TODO: 这个参数的意义？
    parser.add_argument("--skip_val", action="store_true", default=False)
    parser.add_argument("--folder", type=str, default="Results/test")
    parser.add_argument("--weight", type=str, default=None)
    
    # 这个又是什么意思？
    # 以下两个参数应当是控制 func、hunk、line 的
    # store_true 表示在命令里指定即为 True
    parser.add_argument("--suffix", action="store_true", default=False)
    # 单行？是不是在指定单行的 bug
    parser.add_argument("--single_line", action="store_true", default=False)
    
    # 随机种子
    parser.add_argument("--seed", type=int, default=420)
    
    args = parser.parse_args()
    if args.dataset == "defects4j":
        # 确定去 single_hunk？
        if args.suffix:
            dataset = clean_parse_d4j_single_hunk(folder="../../")
        # 确定去 single_line 分支？
        # 这里看明白了，clean 函数完成了对于特定类别 bug 的处理，返回一个字典
        # 其中每个 bug 对应的子字典都记录了该 bug 的五项信息：buggy、fix、buggy_line、prefix、suffix
        elif args.single_line:
            dataset = clean_parse_d4j_single_line(folder="../../")
        # 确定去 single_func 分支？存疑！
        else:
            dataset = clean_parse_d4j(folder="../../")
            
        # 这里为什么要加一个这样的 prompt？应该是保证 few-shot 吧
        # prompt 的意思大致是：先放了一对修复示例，然后放一个示例模版，最后放 bug 代码以及希望修复的提示
        prompt = JAVA_LONG_VARY_PROMPT
        # stop 是什么意思？停止标志？
        stop = "// Provide a fix for the buggy function"
        # 如果处理的版本是单行 bug
        if args.single_line:
            stop = "\n"
        # 目标语言
        args.language = "java"
    ### 以下的部分暂时不需要看
    elif args.dataset == "quixbug-python":
        dataset = parse_python(folder='../../')
        prompt = VARY_BASE_PROMPT
        stop = "# Provide a fix for the buggy function"
        if args.single_line:
            stop = "\n"
        args.language = "python"
    elif args.dataset == "quixbug-java":
        if args.single_line:
            dataset = parse_java_single_line(folder="../../")
        else:
            dataset = parse_java(folder='../../')
        prompt = JAVA_LONG_VARY_PROMPT
        stop = "// Provide a fix for the buggy function"
        if args.single_line:
            stop = "\n"
        args.language = "java"
    elif args.dataset == "manybugs":
        if args.single_line:
            dataset = clean_parse_manybugs_single_line(folder='../../')
        elif args.suffix:
            dataset = clean_parse_manybugs_single_hunk(folder='../../')
        else:
            dataset = clean_parse_manybugs(folder='../../')
        prompt = C_VARY_PROMPT
        stop = "/* Provide a fix for the buggy function */"
        if args.single_line:
            stop = "\n"
        args.language = "c"
    ### 目前没有处理到其他数据集
    else:
        print("Unknown dataset: {}".format(args.dataset))
        return -1
    
    # 设置种子
    set_seed(args.seed)
    
    # single hunk?
    if args.suffix:
        # 定义模型，这里为什么是采用的 SpanLM 模型？另外两个采用 GPT-2？有什么区别吗？
        # weight 参数的含义尚不明确
        model = SpanLM(pretrained=args.model_name, weight=args.weight, batch_size=args.batch_size)
        suffix_repair(args, model, dataset, args.folder, args.chances, args.skip_val)
    # single line?
    elif args.single_line:
        # 注意这里指定了 stop 参数？
        model = GPT2(batch_size=args.batch_size, pretrained=args.model_name, stop=stop, weight=args.weight)
        single_line_repair(args, model, dataset, args.folder, args.chances, args.skip_val)
    # single function?
    else:
        # 这里也指定了 stop 参数？
        model = GPT2(batch_size=args.batch_size, pretrained=args.model_name, stop=stop, weight=args.weight)
        # 注意 only_same 参数的含义？这是为了过滤什么嘛？
        repair(args, model, dataset, args.folder, prompt, args.chances, args.skip_val, only_same=args.dataset.startswith("defects4j"))


if __name__ == '__main__':
    main()
