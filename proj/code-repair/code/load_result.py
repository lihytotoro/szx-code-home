# 现在的任务是，看一下如何处理问完 starchat 的结果呢?
import json
import os
# 正确的程序所在的路径
det_path = 'correct_python_programs'
# 错误的程序所在的路径
source_path = 'python_programs'

if not os.path.exists(det_path):
    os.makedirs(det_path)

# 打开原始询问完成的结果？
# content 是啥？
with open('code_result1.json', 'r') as f:
    content = f.read()
    
content = json.loads(content)

# 每个 item 是一个程序修复对应的字典！
for item in content:
    dict_iter = iter(item)
    key = next(dict_iter)
    value = item[key]
    # 获取字典的第一个键，如果是 avg_token_speed，说明是总结
    if key == 'avg_token_speed':
        break
    # 否则是一个程序的修复结果！
    with open(os.path.join(det_path, key), 'w') as f:
        # 怎么写入？
        if isinstance(value, list):
            value = ''.join(value)
            if value[0:6] == 'python':
                f.write(value[6:])
            else:
                f.write(value)
        else:
            with open(os.path.join(source_path, key), 'r') as f1:
                f.write(f1.read())