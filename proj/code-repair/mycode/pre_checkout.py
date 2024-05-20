# 对于每个子目录，都首先新建各个 proj 的二级目录
import os
from tqdm import tqdm

base_checkout_dir = "/home/lihaoyu/szx/test_suites/defects4j-02"

proj_list = ["Chart", "Cli", "Closure", "Codec", "Collections", "Compress",
    "Csv", "Gson", "JacksonCore", "JacksonDatabind", "JacksonXml", "Jsoup", "JxPath", 
    "Lang", "Math", "Mockito", "Time"
]

for subdir in tqdm(os.listdir(base_checkout_dir)):
    print(subdir)
    checkout_dir = os.path.join(base_checkout_dir, subdir)
    
    for proj in tqdm(proj_list):
        proj_dir = os.path.join(checkout_dir, proj)
        if not os.path.exists(proj_dir):
            os.mkdir(proj_dir)