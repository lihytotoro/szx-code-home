import json

def clean_parse_d4j_single_line(folder):
    # 打开 json 文件，里面记录了每个 bug 的 prefix、suffix、buggy、fix、start、end 六项信息，最终获取的 result 是一个字典
    with open(folder + "Defects4j/single_function_single_line_repair.json", "r") as f:
        result = json.load(f)
    # 记录清洗完成的数据
    cleaned_result = {}
    # k 是 bug 编号（Chart-1），v 是对应的内容（也是一个字典）
    for k, v in result.items():
        # 将 buggy 版本的代码按照行切分开？
        lines = v['buggy'].splitlines()
        # 这个是计算第一行左边的空白格有多少？因为原始数据不包含 \t 所以可以这样计算
        # 重新梳理一遍：这个参数的意思是——第一行缩进的空格数（应该是所有行缩进值的最小值）
        # 这样做的好处？省 token，而回填的时候需要记住应该补足多少缩进
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 按照空格数计算
        # if k == "Chart-10":
        #     print(leading_white_space)
        # cleaned_result 里面要分别记录清洗完成的数据？这里为什么把 leading white space 数目的空格给去掉了？
        cleaned_result[k + ".java"] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        # 接下来，获取前缀部分，同理，去掉不需要的多余空格
        lines = v["prefix"].splitlines()
        cleaned_result[k + ".java"]["prefix"] = "\n".join([line[leading_white_space:] for line in lines])
        # 同理处理后缀
        lines = v["suffix"].splitlines()
        cleaned_result[k + ".java"]["suffix"] = "\n".join([line[leading_white_space:] for line in lines])
        # 最后，同理处理 golden truth 部分
        lines = v['fix'].splitlines()
        # 这里的 leading_white_space 要重新计算？为啥？因为修复过后有可能变更缩进情况？
        leading_white_space_2 = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"]["fix"] = "\n".join([line[leading_white_space_2:] for line in lines])

        # 这里为什么重新获取了 buggy_line？看一下返回值：是 cleaned_result 这个字典！
        # removeprefix：移除指定前缀？
        # removesuffix：移除指定后缀？
        # 首先，移除前缀正确的部分；接下来，移除后缀正确的部分；最后，将剩余的 \n 去掉，就得到了 buggy 的代码行
        buggy_line = cleaned_result[k + ".java"]["buggy"] \
            .removeprefix(cleaned_result[k + ".java"]["prefix"]).removesuffix(
            cleaned_result[k + ".java"]["suffix"]).replace("\n", "")
            
        # 将含有 bug 的一行存进字典中，键名为 buggy_line
        cleaned_result[k + ".java"]["buggy_line"] = buggy_line
        
        # 我认为应当记录两个缩进数据
        cleaned_result[k + ".java"]["buggy_white_space"] = leading_white_space
        cleaned_result[k + ".java"]["fixed_white_space"] = leading_white_space_2
        
    return cleaned_result

# 测试一下 cleaned_result 最后应该包含什么

folder = "../../"

# clean_parse_d4j_single_line(folder=folder)

# 证明了实际上 buggy 和 fixed 只有修复的部分有区别
def test_clean_parse_func(folder):
    # 打开 json 文件，里面记录了每个 bug 的 prefix、suffix、buggy、fix、start、end 六项信息，最终获取的 result 是一个字典
    with open(folder + "Defects4j/single_function_single_line_repair.json", "r") as f:
        result = json.load(f)
    # 记录清洗完成的数据
    cleaned_result = {}
    # k 是 bug 编号（Chart-1），v 是对应的内容（也是一个字典）
    for k, v in result.items():
        buggy_lines = v['buggy'].splitlines()
        prefix_lines = v["prefix"].splitlines()
        suffix_lines = v["suffix"].splitlines()
        fixed_lines = v['fix'].splitlines()
        
        for idx in range(len(prefix_lines)):
            assert buggy_lines[idx] == prefix_lines[idx]
            assert fixed_lines[idx] == prefix_lines[idx]
            
        for idx in range(-1, -len(suffix_lines) - 1, -1):
            assert buggy_lines[idx] == suffix_lines[idx]
            assert fixed_lines[idx] == suffix_lines[idx]
            
    print("test passed!")
            
# test_clean_parse_func(folder=folder)
cleaned_result = clean_parse_d4j_single_line(folder=folder)

# 158 个单行 bug
# print(len(cleaned_result))

# 获取其中一个样例的字典
res = cleaned_result["Cli-17.java"]
# buggy prefix suffix fix buggy_line
print("------++++++------")
print("buggy_line:")
print(res["buggy_line"])
print("------++++++------")
print("prefix:")
print(res["prefix"])
print("------++++++------")
print("suffix:")
print(res["suffix"])
print("------++++++------")
print("buggy:")
print(res["buggy"])