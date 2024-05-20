import json

# 这个字符串记录了 17 个项目以及它们各自含有的 active 的 bug 的数目
# 只是个注释
d4j_bug_lists = '''
| Chart           | jfreechart                 |       26       | 1-26                | None                    |
| Cli             | commons-cli                |       39       | 1-5,7-40            | 6                       |
| Closure         | closure-compiler           |      174       | 1-62,64-92,94-176   | 63,93                   |
| Codec           | commons-codec              |       18       | 1-18                | None                    |
| Collections     | commons-collections        |        4       | 25-28               | 1-24                    |
| Compress        | commons-compress           |       47       | 1-47                | None                    |
| Csv             | commons-csv                |       16       | 1-16                | None                    |
| Gson            | gson                       |       18       | 1-18                | None                    |
| JacksonCore     | jackson-core               |       26       | 1-26                | None                    |
| JacksonDatabind | jackson-databind           |      112       | 1-112               | None                    |
| JacksonXml      | jackson-dataformat-xml     |        6       | 1-6                 | None                    |
| Jsoup           | jsoup                      |       93       | 1-93                | None                    |
| JxPath          | commons-jxpath             |       22       | 1-22                | None                    |
| Lang            | commons-lang               |       64       | 1,3-65              | 2                       |
| Math            | commons-math               |      106       | 1-106               | None                    |
| Mockito         | mockito                    |       38       | 1-38                | None                    |
| Time            | joda-time                  |       26       | 1-20,22-27          | 21                      |'''

# single_hunk
# 现在我们回过头来看这部分，应该与 single line 版本的 parse 并无二致
def clean_parse_d4j_single_hunk(folder):
    with open(folder + "Defects4j/single_function_single_hunk_repair.json", "r") as f:
        result = json.load(f)
    # 同样，开一个字典记录 dataset 的信息
    cleaned_result = {}
    # k 是 bug 的编号（proj-id），v 是对应的各项代码（buggy、fix、start、end、prefix、suffix）
    for k, v in result.items():
        # 首先获取 buggy 版本的完整代码，按照 \n 分割
        lines = v['buggy'].splitlines()
        # 计算出所有行需要去除的多余空格数目（节省 token）
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 在 cleaned_result 里加入 buggy 部分！
        cleaned_result[k + ".java"] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        lines = v["prefix"].splitlines()
        cleaned_result[k + ".java"]["prefix"] = "\n".join([line[leading_white_space:] for line in lines])
        lines = v["suffix"].splitlines()
        cleaned_result[k + ".java"]["suffix"] = "\n".join([line[leading_white_space:] for line in lines])
        lines = v['fix'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"]["fix"] = "\n".join([line[leading_white_space:] for line in lines])
        
        # 注意：这里搞定 fix 项（也就是 golden truth 之后，没有进行后续处理，因为不存在单行的 buggy line）
        # 是否应该处理出类似的 single hunk？
        # buggy_hunk = cleaned_result[k + ".java"]["buggy"] \
        #     .removeprefix(cleaned_result[k + ".java"]["prefix"]).removesuffix(
        #     cleaned_result[k + ".java"]["suffix"]).replace("\n", "")
        # cleaned_result[k + ".java"]["buggy_line"] = buggy_hunk
        
    return cleaned_result

# single_function
def clean_parse_d4j(folder):
    with open(folder + "Defects4j/single_function_repair.json", "r") as f:
        result = json.load(f)
    cleaned_result = {}
    # k 为 bug 的编号（proj-id）
    # v 为 bug 对应的各种代码
    for k, v in result.items():
        lines = v['buggy'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 仍然同理记录了 buggy
        cleaned_result[k + ".java"] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        lines = v['fix'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        # 同理记录了 fix
        cleaned_result[k + ".java"]["fix"] = "\n".join([line[leading_white_space:] for line in lines])
        
        # 对于 single_func 来讲，没有 prefix 以及 suffix，代码是整个函数作为整体输入到模型中的
    return cleaned_result

# single_line
# folder 用于指定 repair 到 数据集根目录 的相对路径（"../../"）
def clean_parse_d4j_single_line(folder):
    # 打开 json 文件，里面记录了每个 bug 的 prefix、suffix、buggy、fix、start、end 六项信息，最终获取的 result 是一个字典
    with open(folder + "Defects4j/single_function_single_line_repair.json", "r") as f:
        result = json.load(f)
    # 记录清洗完成的数据
    cleaned_result = {}
    # k 是 bug 编号（Chart-1），v 是对应的内容（也是一个字典）
    for k, v in result.items():
        lines = v['buggy'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"] = {"buggy": "\n".join([line[leading_white_space:] for line in lines])}
        lines = v["prefix"].splitlines()
        cleaned_result[k + ".java"]["prefix"] = "\n".join([line[leading_white_space:] for line in lines])
        lines = v["suffix"].splitlines()
        cleaned_result[k + ".java"]["suffix"] = "\n".join([line[leading_white_space:] for line in lines])
        lines = v['fix'].splitlines()
        leading_white_space = len(lines[0]) - len(lines[0].lstrip())
        cleaned_result[k + ".java"]["fix"] = "\n".join([line[leading_white_space:] for line in lines])

        buggy_line = cleaned_result[k + ".java"]["buggy"] \
            .removeprefix(cleaned_result[k + ".java"]["prefix"]).removesuffix(
            cleaned_result[k + ".java"]["suffix"]).replace("\n", "")
        cleaned_result[k + ".java"]["buggy_line"] = buggy_line
    return cleaned_result