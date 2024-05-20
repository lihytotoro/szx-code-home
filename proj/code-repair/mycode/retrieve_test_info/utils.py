import os
import json
import re

# 这里，我们定义获取各种测试信息所需的函数
# 用于过滤掉行右边的注释信息，在提取目标测试代码行时需要用到
# 这里的 line，默认是 strip 之后的结果
def filter_notes(line):
    find_double_slash = re.search(r"\/\/", line)
    if not find_double_slash is None:
        span_left = find_double_slash.span()[0]
        real_line = line[:span_left].strip()
        return real_line
    else:
        real_line = line.strip()
        return real_line

# 所有那些 文件名 + 函数名 这对组合中，只有函数名在下方的报错信息中有所体现的那些 bug
def check_only_test_func_name(proj, id):
    proj_id = "_".join([proj, id])
    if proj_id in ["Cli_27", "Lang_10", "Lang_9", "Math_101", "Math_102", "Math_41"]:
        return True
    else:
        return False

# 根据所在项目及编号进行获取
proj = "Chart"
id   = "1"
# 第一个路径是各个项目信息所在的目录，第二个路径是编译后的项目所在路径
base_projects_info_path = "../../defects4j/framework/projects"
base_projects_path = "/data/lihy/defects4j"

# 1. 获取测试函数名称 ———— trigger_func_name
# ---------- begin ----------
# 这个函数包含了两项功能：函数名称 + buggy 行（函数名称 + 错误行数）
def retrieve_test_func_name_and_trigger_codes(proj, id, proj_info_path, proj_path):
    trigger_tests_path = os.path.join(proj_info_path, proj, "trigger_tests", id)
    with open(trigger_tests_path, "r", encoding="utf-8") as f_trigger_tests:
        lines = f_trigger_tests.readlines()
    
    # 注意：可能有多个触发的 test，我们暂时只取第一个
    cnt_trigger_tests = 0
    second_trigger_test_idx = -1
    for line_idx in range(len(lines)):
        line = lines[line_idx]
        if line.startswith("--- "):
            cnt_trigger_tests += 1
            if cnt_trigger_tests == 2:
                second_trigger_test_idx = line_idx
            
    # 必须至少有一个被触发的测试
    if cnt_trigger_tests < 1:
        raise Exception("error: less than one triggered tests!")
    
    # TODO：注意，直接固定从指定的行获取某些错误信息，例如 expected 和 but was，可能是不准确的
    # 可以先输出一遍，然后看看哪些 bug 遇到了问题
    first_line = lines[0][:-1]
    first_line = first_line.removeprefix("--- ")
    # 获取前半部分：在编译项目中的不完整相对路径；以及后半部分：触发 err 的函数名称
    # 后半部分用于在后续行中找到触发 err 的那一行的信息（找到行号）
    test_file_relev_path, trigger_func_name = first_line.split("::")
    trigger_file_name = test_file_relev_path.split(".")[-1] + ".java"
    
    # 从最后一行开始倒序搜索
    cnt_lines = len(lines)
    if cnt_trigger_tests == 1:
        start_retrieve_idx = cnt_lines - 1
    elif cnt_trigger_tests > 1:
        start_retrieve_idx = second_trigger_test_idx - 1
    
    for idx in range(start_retrieve_idx, 0, -1):
        line_i = lines[idx].strip()
        if not line_i.startswith("at "):
            # print("line_i:", line_i)
            continue
        # 找到左括号的位置
        # 这里应该是想要找到括号内部的内容
        # 注意，这里找到的智能保证是括号里的内容，不能保证是目标行
        trigger_line = re.search(r"\(\S+\)", line_i)
        if not trigger_line is None:
            # print("trigger_line:", trigger_line)
            trigger_line_content = trigger_line.group()[1:-1]
            # print(trigger_line_content)
            # error:为什么这里 str has no attribute span?
            try:
                span_left = trigger_line.span()[0]
            except:
                raise Exception("error: failed to get span_left content!")
            # 从左括号开始往左的部分（不含左括号）
            line_i_left = line_i[:span_left]
            target_func_name = line_i_left.split(".")[-1]
            try:
                # 将获取的括号中的内容分割，尝试提取目标文件名
                trigger_line_split = trigger_line_content.split(":")
                if len(trigger_line_split) == 2:
                    target_file_name = trigger_line_split[0]
                    target_row_id = int(trigger_line_split[1])
                else:
                    # 表示这一行的格式不是 目标文件：行数
                    continue
            except:
                # 遇到了其他类型的错误？
                raise Exception("error: other errors while spliting!")
        else:
            # 按照括号匹配的方式没有找到，说明这一行肯定不是目标行
            continue
        
        # # 检查一下文件名、函数名的对应情况
        # if trigger_file_name == target_file_name:
        #     # print("HAHAHA")
        #     print(trigger_func_name == target_func_name)
        #     print(trigger_func_name[-1] == "\n")
        #     print(target_func_name)
        
        # 检查一下文件名和函数名是否均匹配
        # 结论：trigger_func_name 多带了一个换行符
        # 特例：有的时候，文件名对不上，函数名可以，这个时候就需要我们选取下方的文件名，也就是 target_file_name
        if check_only_test_func_name(proj, id):
            if trigger_func_name == target_func_name:
                trigger_row_id = target_row_id
                break
            else:
                continue
        else:        
            if trigger_file_name == target_file_name and \
                trigger_func_name == target_func_name:
                # 记录行号，即该文件 trigger_file_name 下的第 target_row_id 行
                trigger_row_id = target_row_id
                # print("HAHAHA")
                break
            else:
                # print("---------->>>>>>>>>>")
                # print("proj:%s\t\tbug_id:%s" % (proj, id))
                # print("from first line:", trigger_file_name, trigger_func_name)
                # print("from middle:", target_file_name, target_func_name)
                # print("<<<<<<<<<<----------")
                continue
    
    # 获取了一项：testGreatestSubtypeUnionTypes5()，即测试函数名
    
    # 根据文件路径以及行号，获取触发 bug 的代码行
    # print("111", test_file_relev_path)
    # test_file_relev_path += ".java"
    buggy_proj_name = "_".join([proj, id])
    
    # 这里针对的情况是：有可能函数名+文件名这两个匹配条件中，只出现了一种？
    # 注意，对于类似 Math_41 的 bug，单独做 removesuffix 处理还是不够！
    if check_only_test_func_name(proj, id):
        trigger_file_real_name = trigger_file_name.removesuffix(".java")
        target_file_real_name = target_file_name.removesuffix(".java")
        test_file_relev_path = test_file_relev_path.removesuffix(trigger_file_real_name)
        if proj == "Math" and id == "41":
            # print(test_file_relev_path)
            test_file_relev_path = test_file_relev_path.removesuffix("moment.")
        test_file_relev_path += target_file_real_name
        # print(test_file_relev_path)
    
    # 更新：每一个不同的项目中，测试代码放置的目录位置似乎不同
    if proj in ["Cli", "Codec", "JxPath"]:
        test_dir_subpath = "src/test"
    elif proj in ["Closure", "Mockito"]:
        test_dir_subpath = "test"
    elif proj in ["Collections", "Compress", "Csv", "JacksonCore", \
            "JacksonDatabind", "JacksonXml", "Jsoup", "Lang", "Math", "Time"]:
        test_dir_subpath = "src/test/java"
    elif proj in ["Chart"]:
        test_dir_subpath = "tests"
    elif proj in ["Gson"]:
        test_dir_subpath = "gson/src/test/java"
    else:
        raise Exception("unidentified project name %s!" % proj)
    
    # 特殊处理
    if proj == "Cli" and id in ["32", "35", "37", "38", "40"]:
        test_dir_subpath = "src/test/java"
    if proj == "Codec" and id in ["15", "17", "18"]:
        test_dir_subpath = "src/test/java"
    if proj == "Lang" and id in ["37", "38", "39", "40", "42", "43", "44", "45", "48", "49", \
                                "51", "52", "53", "54", "55", "57", "58", "59", "61", "65"]:
        test_dir_subpath = "src/test"
    if proj == "Math" and id in ["101", "102", "103", "105", "106", "85", "86", "87", "88", "89", \
                                "90", "91", "94", "95", "96", "97"]:
        test_dir_subpath = "src/test"
    
    # 这里，对于特殊情况，我们需要变更一下最后一位的文件名——从 trigger_file_name 变为 target_file_name！
    test_file_absol_path = \
        os.path.join(proj_path, proj, buggy_proj_name, test_dir_subpath, re.sub("\.", "/", test_file_relev_path))
    test_file_absol_path += ".java"
    # print("222", test_file_absol_path)
    # raise Exception("222")
        
    # 根据确定好的文件路径，打开，查找对应行号附近的触发语句
    trigger_codes = []
    
    cursor = 1
    with open(test_file_absol_path, "r", encoding="utf-8") as f_buggy:
        cursor = 1
        # 这里为什么老是出错呢？为什么 trigger_row_id 经常性地出问题？
        
        print(proj, id)
        
        # if proj == "Compress" and id == "8":
        #     print(trigger_file_name, trigger_func_name, trigger_row_id)
        
        while cursor < trigger_row_id:
            line = f_buggy.readline()
            cursor += 1
    
        # 目标行
        line = filter_notes(f_buggy.readline().strip())
        while len(line) <= 0:
            line = filter_notes(f_buggy.readline().strip())
        
        while line[-1] != ";":
            trigger_codes.append(line)
            line = filter_notes(f_buggy.readline().strip())
            # 注意：这里我们如果读到的是长度为 0 的行，就忽略这一行继续读
            while len(line) <= 0:
                line = filter_notes(f_buggy.readline().strip())
        trigger_codes.append(line)
    
    # try:
    #     cursor = 1
    #     with open(test_file_absol_path, "r", encoding="utf-8") as f_buggy:
    #         cursor = 1
    #         # 这里为什么老是出错呢？为什么 trigger_row_id 经常性地出问题？
            
    #         print(proj, id)
            
    #         if proj == "Cli" and id == "23":
    #             print("cursor:\t", cursor, "\ttrigger_row_id:\t", trigger_row_id)
            
    #         while cursor < trigger_row_id:
    #             line = f_buggy.readline()
    #             cursor += 1
        
    #         # 目标行
    #         line = f_buggy.readline().strip()
    #         while line[-1] != ";":
    #             trigger_codes.append(line)
    #             line = f_buggy.readline().strip()
    #         trigger_codes.append(line)
    # except:
    #     print("---------- error while extracting error test code >>>>>>>>>>")
    #     # 输出错误信息：错误项目、错误文件路径出错时光标所在的行号、触发错误时的行号
    #     print("buggy_proj:\t%s_%s\nfile_path:\t%s\nnow_row_id:\t%s\ntrigger_row_id:\t%s" % (proj, id, test_file_absol_path, cursor, str(trigger_row_id)))
    #     print("<<<<<<<<<< error while extracting error test code ----------")
    #     return trigger_func_name, None, cnt_trigger_tests, False, test_file_absol_path, cursor, trigger_row_id
    
    return trigger_func_name, trigger_codes, cnt_trigger_tests, True, None, -1, -1
            

# 2. 获取 on this test line(源文件 + 触发行数)，记得去除前面的空白
# 注意，从论文示例可见（Closure 104），错误行有可能是多于1行，记得按照分号作为标准进行检查

# 3. 获取 test error info
# 涉及读取源文件，bug 信息应该是 at 之前的。暂且考虑一般情况（比如前几行？）
# ---------- begin ----------
def retrieve_test_err_info(proj, id, proj_info_path):
    # 该项目的测试信息所在路径
    trigger_tests_path = os.path.join(proj_info_path, proj, "trigger_tests", id)
    with open(trigger_tests_path, "r", encoding="utf-8") as f_trigger_tests:
        lines = f_trigger_tests.readlines()
    
    # TODO: 这里也需要考虑到多个 trigger_tests 的情况
    # 由于是以第一次碰到的 at 作为退出循环的条件，因此暂时不需要下面这部分代码
    # cnt_trigger_tests = 0
    # second_trigger_test_idx = -1
    # for line_idx in len(lines):
    #     line = lines[line_idx]
    #     if line.startswith("--- "):
    #         cnt_trigger_tests += 1
    #         if cnt_trigger_tests == 2:
    #             second_trigger_test_idx = line_idx
    
    test_err_info = []
    
    # 暂定的截断策略为：从第二行开始，直到第一个以 at 开始的行出现，期间的所有行
    curser = 1
    while True:
        line = lines[curser]
        curser += 1
        if line.strip().startswith("at "):
            break
        # 前面的缩进不要去掉，但是后面的 \n 去掉
        test_err_info.append(line[:-1])
        
    return test_err_info, True