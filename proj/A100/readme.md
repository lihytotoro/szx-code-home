# A100 服务器下的 readme
现在正在阅读 Firefly 的 readme，正在考虑如何编写 codellama 的微调

支持 QLoRA 微调？
LongQLoRA：大模型长度扩展项目，可在单卡V100上将LLaMA-13B的长度扩展至8192，且性能逼近MPT-8K

多卡时使用torchrun命令启动脚本：
    torchrun --nproc_per_node={num_gpus} train_qlora.py --train_args_file train_args/qlora/baichuan-7b-sft-qlora.json

注意：微调 codellama 时，需要使用 huggingface 版本的 codellama，并且需要修改 /train_args/qlora 目录下有关 codellama 的 json 文件

在使用模型进行推理时，
如果使用 LoRA 或者 QLoRA 进行训练，本项目仅保存 adapter 的权重和配置文件，需要将 adapter 权重与 base model 进行合并。脚本见**script/merge_lora.py**

**我们尝试过 DeepSpeed + QLoRA 的训练策略，但尚未成功，目前建议使用 torchrun 启动训练。后续若成功，我们将更新代码。**

# 1228 更新
从今天开始继续多寻找一些数据集，留作 finetune 过程备用，并且着重搜索一些有关 chat 的论文（两天左右时间完成）
另外，跑通 juliet 数据集里的编译部分，看看有没有什么坑，并且同时尝试写一下清理注释部分的代码

# 0108 更新
在 repairllama 作者提到的 megadiff 数据集的基础上微调 codellama
作者处理的版本中，+ 表示修复后的版本，- 表示修复前的版本

对于 Firefly 中的架构，仿照 dummy_data 的结构，构造数据？
输入格式：一个完整的函数 + 注释掉的 bug 部分（也就是上面说法中的减号行）+ MASK 的标识符
输出格式：只需要输出 fill me 的部分即可

目前，5w 条左右的数据被确认是 single chunk 的（即最多只有一段 +、一段 -）

# 0110 更新
基于 repairllama 作者处理的 megadiff 过滤后数据集（4096 token 以内的数据，共约 5w 条 —— 48631）
如果将max token len限制到 1024，那么条数是：37234，使用这种数据微调，有可能会快很多

目前，4096 长度条件下，batch_size 设置为 4，使用 4 张 A100，可以训练起来，一个 epoch 大概耗时 15h？
第二组实验尝试在 1024 的条件下进行，batch_size 不变

# 0110 任务
使用 finetune 之后得到的模型参数，搞一下新一轮的测试 —— 加入 beam_search（后续可以加入 patch_ranking？） 以及测试信息辅助
除此之外，还可以测试一下新模型在多轮对话上的效果。意味着我要写一下提取某一轮测试后得到的错误信息的功能
1. BEAM SEARCH（看一下别人的方法，这部分时间能节省吗？）
2. 多轮对话的流程 —— get error info, extract error info。我认为问题主要还是出现在：如何从混乱的自然语言回复中提取出代码的问题
3. 在 1、2 之后，清洗一下 juliet C++ 或者 java 的数据，其中 java 似乎会更重要？因为我们目前的目标主要还是 d4j

第一种 finetune 耗时 10 个小时多
第二种耗时 150 min 左右

### 微调之后得到的模型，如何使用呢？
1. 本项目仅保存adapter的权重和配置文件，需要将adapter权重与base model进行合并。脚本见script/merge_lora.py
2. 运行脚本之后，/vepfs/lihy/Firefly/output/firefly-codellama-7b_maxtoken=4096-merge 保存了微调后的完整模型

# 0112 进展
目前我在研究 repairllama 作者的微调手法 —— 直接使用了 Trainer 类进行后训练
对于 load_dataset 的问题，参见 https://stackoverflow.com/questions/77020278/how-to-load-a-huggingface-dataset-from-local-path

megadiff single function 数据分为 4 个 parquet，处理前后的概况：
    total  single_chunk
0   18099  12609
1   18098  12802
2   18098  12722
3   18098  12563
all 75633  50696

限制 token len 1024 的情况下，有 36508 条数据

查看了 parse_megadiff 中的逻辑，发现我是直接把 错误的段落给去掉了，而不是保留注释格式
在使用 repairllama 的框架之下，需要严格按照 IR4 X OR2 的格式进行微调

决定按照 parquet 的格式进行输出，包含两部分 —— input 和 output
这样输出一个文件，然后 train 和 eval 的时候暂时使用同一套数据集

目前，对于注释掉错误 chunk 的逻辑已经写好了，有待输出成文件检验一下

# 0114 进展
跑起来了 repairllama 的 finetune，开始研究 pred 部分，也就是如何利用生成的模型输出修复
主要先弄清楚各个路径的问题

5 小时左右 finetune 了两个 epoch，看完了 pred 部分，需要编写一个针对 d4j 数据集的 input 文件，包含：bug_id、buggy_code、fixed_code？
实际上，对于 buggy_chunk 类型的缺陷，xia 已经整理出包含：prefix、suffix、buggy_chunk、fixed_chunk 的文件，需要进一步整理出 buggy_code —— 
    首先指出含有 buggy chunk，然后 prefix + commented buggy chunk + [FILL_ME] + suffix

目标：构建这样的后处理数据集
构建完成之后，使用 lora-finetune 之后得到的模型进行测试

目前，使用 1024 max_len + 256 max_new_token 的组合，beam search = 10，预测大约需要 130 分钟以生成 313 个 single chunk bug 的 每个 10 种 样本（待测试）

# 0115 进展
目前，成功生成了 2 个 epoch 情况下的 295 个（有 18 个测例因为太长了没能生成？）样例的回复，每个 sample 产生了 10 个 patch
对于早上跑完的 epoch=5 的微调，目前按照同样的方法尝试生成回复，beam 仍然设置为 10

回填的逻辑？
1.去看一眼 backfill 的原始版本，看看如何填充（目前已知行数，但是文件名需要从 d4j 的 patch 的 diff_info 中手动提取）
2.能不能保存一个 bug_id 到 附加路径 的映射文件？这样我们下次知道了路径和行数就不用额外的精力了
3.测试结果的生成：最好弄成一个表格形式，记录 1~10 号备选方案到底是 compile error、test failed 还是 test passed。最后统计一下 10 个里面各有多少

# 0117 进展
目前正在运行首次测试的最后几个循环，在此之前已经构建了每个项目回填的目标文件（针对 single hunk，313 个），以及全套的自动化流程（针对单轮次对话）

接下来的任务：
1. 研究多轮对话格式（multi-chat？这个似乎需要借用 firefly 的思路，那里有 multi-chat 的部分）
2. * 对于 megadiff 的全数据，研究 single func 类型的数据如何进行处理（优先）
3. CWE！研究如何处理含有 cwe 类别标注的 bug。在将这部分数据整理成微调数据集时，需要注意注释的剔除，以及函数名等部分的内容

针对 megadiff 的全数据，按照作者的回复，不管有多少个 chunk，只关注第一次出现的 bug 的地方，以及最后一次出现 bug 的地方。（只关注 - 号不要关注 + 号）
input:
从 第一个 chunk（第一次出现 - 的地方开始），截止到最后一个 chunk（最后一次出现 - 的地方？）
这中间的所有行都注释掉，然后在第一行的前面加上 buggy chunk
output:
作者的思路是把中间的正确行都忽略掉（一起注释），然后合成一个完整的段落 —— 认为这样更有利于模型理解更多的代码
output 时，从第一行 + 所在的位置开始，然后到最后一个 + 所在的位置，其中也包括本身就正确的行。合并之后，作为 fixed chunk

目标文件（可以重新复制一份，新建一个新的文件）：parse_megadiff
实际上，跑起来新一轮的训练之后（先跑 2 轮吧），我们还需要按照同样的思路，parse d4j 数据集

# 0119 进展
处理了新版本的 megadiff，限制 input、output 各自不能超过 1024，共 49867 条数据！
准备开始训练！
在并未去除注释的数据版本上进行了训练，但是目前注意到注释行是不需要的，可以省略
注释行的判定标准？在 diff 版本的文件中，只要去除了第一个字符之后，再进行 lstrip 操作，左边剩余的开头部分以 // 开始，那么就视为注释部分
这样处理的好处是可以有效节省 token 数目，增大训练样本数

注释完的数据有接近 5w 条，设定训练 3 个 epoch，maxlen=1024，使用 4 张卡训练

# 0119 进展 - 2
目前我们还需要将 483 个（repairllama 作者声称 488 个）bug 转换为 finetune 数据遵循的格式 —— 即严格按照将所有 single func 都转化为 single hunk 的模式
首先看一下相对于作者声称的 488，我们差了哪几个 bug？

目前已经完成了剩余 170 个 bug 的处理
明早完成 313 + 170 个 bug 的输入数据处理，最重要的工作是：去掉空行以及带注释的行！

最新的两次 generation（pred）之中，使用自行训练的模型，生成 4780 个 sample 用时 2 小时 10 分；而使用作者留下的 lora adapter，那么生成 4780 个 sample 用时 3 小时 20 分
区别在于，目前我训练的模型，注释格式和作者有区别（见 prompt.txt），并且比作者的 prompt 多了开头的一句话，不知道这个有没有影响

为此，准备将 megadiff 数据集按照作者的思路修改一下，然后重新训练 3~5 个 epoch。（训练 + 预测 + 重新测试）
现在似乎空出来了 4 张卡，看看能不能插个队进去

目前，训练好了没有 initial prompt 的版本！总共是用 50109 条数据进行了 2 个 epoch 的训练

# 0123 进展
epoch=2 的 copy_author 版本测试已经在运行，基本上已经完成了
epoch=5 的版本刚刚完成训练，跑一下测试

epoch=5 的效果很差，还是 epoch=2 比较好？
目前，重新训练一个 epoch=1 的版本？

        my      au
common  472     472     au 比 my 多 20 个 test passed!
special 2       8       多出 1 个 pass

# 0125 进展
尽快（今晚）研究清楚 CWE 数据集的情况，看看具体应该怎么构造数据集！
如何进行微调？
第一轮：将类别隐去，只输入原始版本代码，然后
第二轮：输入 CWE + bad code，然后找一些 good code 输进去？

对于 qlora，训练了一个版本的模型，看看新模型 2 个 epoch 之后有没有改善？

# 0224 进展
今天主要是在 A100 上训练起来 repairllama-cwe 的两个版本（注意，我目前只写了 lora 的融合模型继续训练的逻辑，还没有写 qlora 如何继续训练）
并且，使用一张卡进行一下 qlora 在 d4j 数据集上的 inference（争取明天进行测试！）