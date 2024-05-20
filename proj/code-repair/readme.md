当前任务 将错误版本的代码 从 git_diff 中提取出来，顺便，要不要提取一下正确版本的代码？

0910 晚间更新
目前，我们基于 patch 的代码修复已经跑出来一版本结果，需要改为函数级别的修复
如何从编译得到的原始文件中获取相关的代码呢？
我们需要修改 —— train.py 文件，但是这里获取 bug 代码是直接从 src.patch 文件中获取
我们需要改为：从编译出来的具体位置进行获取！

首先，编译出原版项目，然后，我们知道函数名称，因此从 start_pos 所在的行向前倒推比较合理
然后，如何确定最后的一行呢？需要看一下示例

0914 晚间更新
目前，我读了一篇有关如何处理 defects4J 数据集的论文

具体来讲，我们需要按照以下流程进行：数据清洗、迭代对话式（并且包含及时的反馈）进行 bug 修复、最后有一个流程就是手工查看通过了所有测试的修复版本是不是真的是对的（manual）
1. 数据清洗
需要哪些数据？
    1.1 bug 段代码，这次实际可以拆开为以下几部分！
        拆出来 bug 行（用 <INFILL> 替代）的代码段
        bug 代码行（段 —— single hunk，single func 情况另行处理），用于单独向 模型 指出错误
        也可以看一下所在类的名称管不管用！
    1.2 触发其中的 bug 的测试函数？
        需要测试函数的名称
        触发 bug 的测试行代码
    1.3 bug 信息
        需要 bug 的详细信息，例如：expected:<NoObject> but was:<None>
    1.4 后续情况下，如果给出的代码回填之后触发了编译错误，那我们需要指出代码含有 compilation error!
        The fixed version is still not correct.
            code has the following compilation error:

2. 按照论文中的说法进行迭代式 bug 修复
关于这一点我们需要看一下 starchat 有没有记录对话历史的功能！

我们需要限制这些参数：
    对话的轮次限制；
    错误修复迭代 + 看起来对的修复的继续迭代的总次数？
    这里我还没有完全理解其想法，看看两个参数有什么区别！

3. 评测结果
目前我们首先认为只要能通过测试的就是合理的回答！
之后再考虑加入手工查看是模棱两可的还是真正正确的答案的部分

基于以上的分析，我首先需要分别编写代码，提取各个 bug 的原始信息。
然后，我需要编写回填 + 编译 + 输出结果部分，输出的结果仍然需要归类输出，并回复给到大模型
最后，需要收集迭代中的各次结果，看看是否能够给出正确的回答

对于数据集，我们还有一个额外的任务，即需要首先按照 single line, single hunk, 以及 single function 的维度，过滤出 1.2 版本以及 2.0 版本的各种 bug，供测试使用！

实际上，在 800+ 的数据中，只有 300+ 的数据满足要求？

# 0916 最新进展
搞清楚了 1.2 和 2.0 的区别
1.2: 6 projects, 391 active bugs
chart closure lang math mockito time
2.0:(additional) 11 + 1(closure 134-176) projects, 444 active bugs

total: 17 proj + 835 active bugs

如何挑选出 single 类型的 bug？
注意 single line < single hunk < single func！
1.2 版本的是有网页数据可以参照的，可以看看里面 modified lines、modified func 等参数，看看是不是符合各集合的要求，然后需要对照一下作者给出的数据
2.0 版本作者没有给出数据？明早发个邮件问问？也可以后续自己手动过滤！

我们可以统一对这些 active bugs 构建一套迭代式问询式 bug 检测及修复流程

# 0918 最新进展
找作者要到了数据集的部分清洗后版本（包含 bug 所在的完整函数）
目前只获取到了 bug 的前缀和后缀信息

我们缺什么？—— 首先，测试部分的额外信息；其次，代码可以输入给大模型用于测试了，但是输出的代码的回填需要写一个自动处理的程序（已知 start 和 end，将提取出来的修复结果给到项目）

# 0925 更新
注意，在 chatgpt 那篇论文中，是选了 255 个 1.2 版本中的 single func，以及 228 个 2.0 版本的 single func 中的 82 个，
来源似乎是这篇论文（为了方便比较实验结果）：Less Training, More Repairing Please: Revisiting Automated Program Repair via Zero-shot Learning

# 0927 更新
目前，我将本周要做的代码工作分为以下几步：

1. 首先，获取第 0 次测试之前的各项测试信息及报错信息
2. 源代码，应该已经有了？
    SF：询问的时候直接问：这段代码有问题，如何修复？
    SH、SL：前缀 + <MASK> + 后缀，给定错误代码及测试信息，如何修改？
3. 回填代码
4. 看看编译错误以及编译过了测试不通过的情况下又怎么处理
    如何 retrieve 各项报错信息？

首先完成第一项任务，即获取 defects4J 数据集中，某个 bug 对应的 测试信息         ———————————— TODO！
    测试函数名称
    触发测试函数报错的那一行（需要源文件+行号）
    测试报错信息（例：expected:<NoObject> but was:<None>）

# 0928 更新
今天看了一下 github 版本（也就是官方版本）的 code-llama 的能力，感觉比较规整，回答速度也比较快
就是要实现 chat 的话，应当是需要手动将每一次 assistant 生成的内容拼接到 instruction 之后？

这样相对来说还是比较规整的。但后续针对 d4j 数据集，需要添加更多测试信息

# 1008 更新
今天大致写完了测试信息的提取，先测试一下正确性——即尝试生成所有 bug 的 test info
然后，尝试根据作者已经提取出来的 prefix、suffix，联合我后续提取出来的 test info，重新写一个 code-llama 版本的回复生成 + 代码回填 + 编译测试流程
注意明确数目：483（255+228） 313（154+159） 158（80+78）
作者的回复是，82 有误，应该是 78，另外 835 个 bug 实际上貌似扣除了 6 个 deprecated 的（391 + 438 / 444）

# 1015 更新
目前遇到的问题：
1. 应当从最后一个 at 开始，倒数到第一个出现目标函数名的行处
2. 有可能在一个 trigger_test 文件中，有多个 bug，这个问题可以通过 --- 来进行分割。目前，我们是否只考虑输入其中一个（第一个？）测试函数？

# 目前的问题
defects4J 目录里 由于当初只考虑了 single_change 的问题，现在需要额外把确实的 single_func 范围内的项目补编译出来
修改 mycode/checkout.py

# 早上的解决方案
目前等待 checkout 完成之后，可以重新运行 test_utils，看看提取怎么样了
提取的进度：
    Cli_27 与下面的 Lang_10 类似，只出现了函数名没出现文件名
    Cli_40 触发异常的函数并没有出现在报错信息里
    Codec_7 测试文件中出现了乱码，实际上是 unicode 字符（Base64Test.java），这个已经解决了
    Compress_28 触发异常的函数并没有出现在报错信息里，与 Cli_40 可能是同类型错误？（出现在 try 里）
    Compress_44 同上
    Compress_7 似乎有乱码 已经解决了
    Compress_8 一样的乱码已经解决了
    Gson_16 StackOverflow 触发异常的函数并没有出现在报错信息里

    目前到了 Jsoup 68
    继续做
    Jsoup_68 StackOverflow，同上
    Jsoup_85 AttributeTest::validatesKeysNotEmpty，文件名和函数名均未出现在报错信息中？
        junit.framework.AssertionFailedError: Expected exception: java.lang.IllegalArgumentException
    
    Lang_10 与 Cli_27 类似，问题在于文件名不一致但是函数名还是一致的
    Lang_57 触发异常的函数并没有出现在报错信息里，二者不一致
    Math_25 AssertionFailedError 文件名和函数名均未出现在报错信息中
    Math_34 AssertionFailedError 文件名和函数名均未出现在报错信息中
    Math_45 AssertionFailedError 文件名和函数名均未出现在报错信息中
    Math_50 AssertionFailedError 文件名和函数名均未出现在报错信息中
    Math_86 AssertionFailedError 文件名和函数名均未出现在报错信息中
    Mockito_8 StackOverflowError
    
结果：470 + 13 failed = 483 bugs
其中单行 bug：80 + 78 - 4 = 154？

看一下提取的效果？
应该可以用了

# 1023 利用提取出的测试信息和原始的代码信息，依次进行 SL SH SF 三种 bug 的测试
注意，如果测试信息太长的话？需不需要考虑做截断，比如使用至多前 n 行 error message？
clean_dataset/clean_LLM_repair/Defects4j 中，存储了所有 bug 对应的原始代码信息

重点关注一下，作者其实是有一步统一消除缩进的操作的，看一下有没有记录如何恢复！
single_line 有 4 个目前舍弃的：Cli-40、Lang-57、Math-34、Mockito-8

在余下的 154 个 single line bug 中，
Closure-123（编号 20）导致编号 20~23 的 bug 无法生成
Jsoup-15（编号 83）导致编号 80~83 的 bug 无法生成
Jsoup-35（编号 90）导致编号 88~91 的 bug 无法生成
Jsoup-76（编号 105）导致编号 104~107 的 bug 无法生成

我们暂时排除这 4 个太长的 case，还剩 150 个 bug。将这 150 个 bug 的修复结果尝试回填回去？测一下结果

记录回填时候的情况
    Gson-5 似乎没有生成正确回复？

backfill 的时候有点问题，应该也同时写入前缀和后缀的

# 1026 进展
今天晚间的任务：将 codellama 给出的代码回填

有两种方案：
    1. 根据 git diff 中给出的信息（起始行号、行数、终止行号）可以找到 bug 所在的位置，然后，根据 +++ 出现的位置（即需要修正的行），
        找出应当回填的位置，这样的好处是：不需要重新回填 prefix 和 suffix，直接回填 fixed_line(s) 即可；
    2. 按照 prefix + fixed_line(s) + suffix 的形式，找到出错的整个函数，然后整个得替代之，感觉没有这么做的必要

我个人的感觉是，虽然第一种方式需要额外的工作：即根据起始行号找到出错的位置，但是相对来说更稳妥，不需要重新找到出错的整个函数的位置

因此，我们在 backfill.py 函数中，额外添加一个函数，作用是：根据 proj, id 对应的 patch 信息，找出 +++ 即需要删除的行的行号！
在打开了 n.src.patch 的情况下，已知 lines、start_row、row_cnt，直接去找 +++ 那一行在什么位置就可以了！
忽略所有以 - 开头的行，然后找到 + 开头的行，注意：如果 + 多于一个，要看一下为什么会多于一个（比如分号是截止于下面的行？），可以打印出来具体情况具体分析

思考一下这个函数应当是什么参数类型：
    目的：根据指定的一些 lines（输入参数），以及 lines 对应的一些行号，搞清楚应该在源文件的哪一行进行前后缀截断
    返回值：直接给出 buggy_line 的行号——另外，还有一个任务：统计+开头的行的行数
    注意：不需要读取源文件，直接从给定的 buggy 段落找信息就可以了

中午，看了一下 single_line 涉及的所有 bug，均可以归类到以下三种：
    首先，都是单个 diff 单个 @@（单个文件中的单个段落）
        1. 一个 + 一个 -，即替换
        2. 一个 +，即删除
        3. 一个 -，即增添
    这样，我们收集 @@ 之后所有行的信息，即为 single line 情况下 lines 的内容了

目前，我们还有一个信息没有用到——start、end的信息，它记录了左闭右闭形式的整个 buggy 函数的位置（在目标文件中）
我们确定 prefix、suffix 有多少行，然后据此确定 buggy_line 的位置，即可！

又或者：新的想法——直接，1~1789行，prefix，fixed_lines，suffix，1823~末尾，按照这个顺序直接写入即可？
确认了：即使对于插入情况，start、end 也适用，因此我们可以重构 backfill.py 中的代码了

目前，完成了 150 (+4+4) 个 single line 的回填，关注一下之前写的编译运行逻辑需要改哪些
重点关注 run_test.py

在运行完这一次的 test 之后，在周一之前需要做的事情？
    1. 将单次拆得很零散的运行改为流程式运行

    2. 流程化之后，写一下收集错误信息的逻辑，用于提供给迭代

    3. 完成 1、2 之后，我们可以尝试按照循环迭代的逻辑完成作者在论文中的修复逻辑！

# 1027 晚间总结
目前，效果仍然很差，接下来，首先要看一下——
    1. backfill 的位置是否出现了问题 + 缩进有没有大问题（检查几个例子）；
    2. 如何避免每次打开某个 /data/lihy/defects4j 中的关键文件时，都要花很久去寻找路径。最好的方法是，复制原始文件内容，到 /home 中的某个目录下

解决方案：
    生成以下的文件：
    1. 修改之前的目标文件的目标函数部分？（copied，原封不动）
    2. 修改之后的目标文件的目标函数部分
    3. 将 src.patch 复制一份，到同一目录下，方便看出问题
    4. 要插入的回复，即 fixed_model_reply，复制一份，到同一目录下，看看模型回复拷贝得对不对

观察之后发现，我们还需要一个文件——记录 prefix、suffix、buggy_line 的输入方式
目前似乎观察到的有较为严重的缩进问题，需要看看 prompt 是不是有问题

# 1028 解决方案
我们需要将复制后的文件移出去？放到 output 目录下面吧
目前，已经完成：
    1. 删除项目目录下的所有 copied 文件
    2. 将 copied，也就是没有任何修改的版本移到 mycode/output 目录下，命名后缀为 copied

当前结论：20 passed + 85 failed + 45 compile error = 150 bugs
single_hunk：19 passed + 162 failed + 118 compile error = 299 bugs

# 1105 晚间
目前，似乎进化成多轮对话版本不是特别现实
我们试一下 single hunk、single function 版本能不能今晚跑通？

我认为需要修改的模块：
    0. checkout: 所有 single_hunk、single_func 的项目还没有编译出来
    1. retrieve_test_info：目前获取的只是 single line 的所有 **测试信息**
    2. prompt_codellama: 提示信息的构建似乎只用微调一下就好了
    3. 回填的时候: 注意，顺序应当是 —— 首先写入前面无关的行的代码，再写入 prefix + 段落 + suffix，或是 一整个函数
    4. output: 回填代码的时候，顺便把 single line 情况下获取的六项 info 都获取出来

解决这些问题之后，不要奢求出来很好的结果，能跑通就行

# 1105 夜间
我们从 single hunk 开始
bug 数目：313（154 + 159）

    0. checkout: 已完成（因为是一次性把所有 single func 以下的都 checkout 出来了）
    1. retrieve_test_info: 首先原来的 single line 有一部分已经获取了，我们需要获取剩下的所有 bug 的信息！
        进展：实际上，获取测试信息时，已经提前将所有 483 个 bug 的信息统一提取出来了！
        这里写一下提取测试信息遇到问题的所有 bug
            ["Cli-40", "Compress-28", "Compress-44", "Gson-16", "Jsoup-68", "Jsoup-85", "Lang-57", "Math-25", "Math-34", "Math-45", "Math-50", "Math-86", "Mockito-8"], 共 13 个（总共 483 个）
    2. prompt_codellama: 
        上面 13 个 bug 里面，哪些是 single hunk 的？
            ["Cli-40", "Compress-44", "Gson-16", "Jsoup-68", "Lang-57", "Math-34", "Math-45", "Math-50", "Mockito-8"], 共 9 个
        这里记录一下失败的各个 bug（最大可能是长度太长了）
            编号 36，Closure-123
            编号 179，Jsoup-15
            编号 189，Jsoup-35
            编号 191，Jsoup-38
            编号 209，Jsoup-76
        算下来，313 个 single hunk 的 bug 中，成功生成回复的有 313 - 9 - 5 = 299 个
    2-3 之间的准备工作：看一下回复是否都合规！

# 1112 夜间

目前进展：已经生成了所有的 single hunk bugs 的未提纯回复
需要完成的任务：
    1. single hunk bugs 的提取与回填
    2. single hunk bugs 的单元测试
    3. single func bugs 的回复生成
    4. single func bugs 的提取与回填
    5. single func bugs 的单元测试

明早之前完成这些部分

+ 论文阅读 + 数据集收集（提到的数据集：Vul4J、VJBench）
看起来应该是 Java 语言的新 bug

    1. single hunk bugs 的提取与回填

        !!! 注意到之前写的 single hunk 的 prompt codellama 逻辑有问题！
        single hunk 的多行代码不能直接 replace \n

    extract 之后应该是 逐个检查一遍

    2. single hunk bugs 的单元测试，正在运行

    3. single func bugs 的 prompt 及回复生成
        首先，大体上过一遍剩余的 483 - 313 = 170 个 bug 是什么情况吧 —— 指的是看一下 info
        给人的感觉是：尽量不要直接操作这些 bug 的 src.patch 信息了！

    4. single func bugs 的提取与回填
        目前，已经完成 初步回填，有待进一步后处理
        后处理完毕后，可以进行直接回填

# 1203 晚间
总感觉断了很久没有写 readme，不应该
今天的任务：研究 Vul4J 数据集跟 CWE 信息的关系
先下载 Vul4J 数据集

下载完成了，好像还挺大的
看一下怎么使用

# 1224 晚间
一、最近几天在加紧完成收集数据集以及 finetune 模型的工作

1. juliet-cpp
2. juliet-java
3. juliet-csharp

这几个数据集是含有 CWE 标注的，暂时还没有看有没有 test suite
希望在这几个数据集以及其他一些数据集上验证一下几个问题：

PreciseBugCollector只丰富了数据集，没有做实验，证明代码错误类型对于代码修复有用。
1. 能检测代码错误并对应到CWE类型；（能不能在 few-shot 甚至 zero-shot 的情况下，回答出 CWE 类型？）
2. 引入CWE错误解决措施相关信息，辅助完成代码修复；（作为辅助信息）
3. 迭代流程实现；（测试多轮对话效果，赶紧进行 case study）
4. 针对CWE类型的测试案例生成。

二、目前除此之外，还在研究去年的一个论文：Impact of Code Language Models on Automated Program Repair，这篇论文在 zenodo 提供了 finetune 的模型、用于训练的数据，以及 re-finetune 的方法

论文中的数据格式：
分为 10w+ 条 train 和 1w+ 条 validation，每一条包含：bug、fix、prefix、suffix 之类的信息，似乎可以等价为 defects4J 中的 single hunk 类别。
但是，论文涉及的预训练数据，并没有具体的 CWE 类别
可以先跑通 finetune 的过程

与此同时，我们应当与 finetune 同步进行 CWE 信息的验证工作

我们测试一下能否回答出 CWE 类型，这个任务，我们针对 java 中选取的一些样例进行测试——在 code-repair 目录中新建子目录进行测试

# 0114 修改
如何注释？
    lkhca
        ochdsocw
    canknckj
注释：
    // cajlci
    //    xmqlm
如何注释？
        ajdlk
    xabkjcsbakj
    }
注释：
        // xdnoq
        // xaooc
        // }
目标注释：
    //
    //
    //

# 0115
1.去看一眼 backfill 的原始版本，看看如何填充（目前已知行数，但是文件名需要从 d4j 的 patch 的 diff_info 中手动提取）
2.能不能保存一个 bug_id 到 附加路径 的映射文件？这样我们下次知道了路径和行数就不用额外的精力了  ———— 目前已经生成了这样的文件，之后直接 backfill 到该路径下即可！
3.测试结果的生成：最好弄成一个表格形式，记录 1~10 号备选方案到底是 compile error、test failed 还是 test passed。最后统计一下 10 个里面各有多少

注意：写入新生成的补丁时，由于输入给模型的代码去除了前面的空格，因此每一行都要加上 whitespace
目前，已经准备好了：回填路径文件、input_info 文件（包含行数、空白数量等信息）、output 文件（每个 bug 10 个 patch）

最新进展：已经开始运行测试了，明早应该能跑出来 2~3 个循环

# 0116 进展
注意到在 repairllama 的文献之中提到了 patch assessment 的技巧，大体来讲是讲生成的 patch 和 golden truth patch
同时转化为 AST 结构，然后对比语法语义上的差异，具体的指标还要看论文决定
Following related work [17, 43, 48], we compute the following repair effectiveness metrics

思考一下 微调数据集 和 测试 的范围
目前我们相当于是把测试范围限定在了 single hunk 领域内。但是，repairllama 的作者声称对 488 个 d4j-v2 的 single-func bug 都进行了测试

1. 如何处理非 single hunk 模式的微调数据？

如何处理呢？这事关后续我们研究 single func 类别代码的微调方法
作者在文章里写的方式是输入整段 function。选中其中所有需要删除的行

举个例子：
    func a() {
        // buggy code
        // -
        ...
        // buggy code
        // -
        // -
        // -
    }

# 0119 进展
需要写一下 d4j 处理成 single HUNK 的脚本 —— 将 single function 都视为一个巨大的 hunk。按照作者的假设，实际上大部分 sf 非 sh 的 bug，不同的 hunk 之间的距离不会很大
先处理一下 single hunk 的 313 个，再处理剩余的 170 个非 single hunk 的？

思考：我们首先已知了函数的开始和终止行数
在此范围内，diff 信息内的每个部分都以 start_idx 和 row_cnt 给定了一个小范围（理论上一定在函数内部，若有特例再议）
我们在每个段落内部找出 +、- 存在的行数，最终即可决定 first_diff_line_idx 和 last_line_diff_idx 了
与此同时，我们标记一下 - 和 + 的行号，分别形成两个行号列表，方便决定 buggy_hunk 的去留时用
这样我们就不需要重新构建一个相应的纯 diff 文件了（涵盖整个函数的）

# 注意
函数的 start 和 end 是左闭右闭的，而且是从 1 开始计算
与此同时，patch 文件记录的 diff 格式所记载的行号也是从 1 开始计算的

目前，我们正在进行新版本 megadiff 数据 + 新版本 single func d4j 数据的测试工作，生成 4830 个 patch
测试时，我们还缺 single_func 的一个 backfill_path

483 个 single func 类型的 bug，一共生成了 478 个 bug 的回复：
以下这些 bug 没能生成 —— 明显是因为长度太长了！
    编号 36，Closure-123 没看出来
    编号 179，Jsoup-15 5941
    编号 189，Jsoup-35 5932
    编号 191，Jsoup-38 5608
    编号 209，Jsoup-76 5599
回复存储路径：/home/lihy/proj/d4j-output/defects4j_all_single_func_repairllama_test_output_maxlen=1024_epoch=3_newdata_wo_comment.jsonl

下面主要基于这次生成的回复进行代码回填及测试工作

目前，测试已经开始，由于生成了 10 个样本，因此我们需要开很多个 defects4j 的副本进行测试
defects4j       0~1
defects4j-2     2~3
defects4j-3     4~5
defects4j-4     6~7
defects4j-5     8~9

# 进展
目前看到了 0、2、4、6、8 的测试结果，没有预想的好
目前决定：
    1. 直接拿 instruct-7b 和作者留下的 repairllama-lora 适配器试一下，对于 d4j 数据集，我们不再添加 前面的 instrcution，并且 // 的方式也改成直接在前面注释
    2. 按照这个思路，重新组织 megadiff-7b 数据集进行微调，然后，今晚之前开始训练，明早之前训练出来一个新的版本！

    已经完成了 1 中的 pred 部分，需要进行测试！安排在本轮测试完成后进行
    2 中的 megadiff 数据集已经完成了处理，新版数据去掉了 initial_prompt，并且注释方式跟作者也保持一致！

最新进展：自己训练 3 个 epoch 的版本，目前已经能够修复：161 个 bug —— 距离作者的 188 还有距离！
上述的 1 已经生成完毕，马上开始测试

注意：一定要保持 d4j-6 目录的纯净，不能向内部写入
涉及到 backfill 的 10 个目录分别为 1~5、7~11

今晚的测试只能用到 除了 10、11 以外的 8 个目录
defects4j-1     0~1
defects4j-2     2~3
defects4j-3     4~5
defects4j-4     6~7
defects4j-5     8~9

在运行 author version 的 lora adpater 以及观察之前生成的 patch 的测试结果（最早的一批 output_csv）时，发现 time out 比重很大，是否这会影响最终输出的结果呢？
明天早上最后几个 epoch 也会运行完毕，那时我们看一下最终能否比 161 高很多！

# 0123 更新
准备看一下跟原作者差距在哪些 bug 上面
以及我自己生成的版本中，具体有哪些测试超时了？

曾经的文章里提到：5s + 1.5 倍的原本的测试时间？

# 0124 更新
针对测试超时的问题，有研究提到：应当使用 5s + 1.5 * 原始测试时间，作为本次 bug 的超时额度
跑一次 buggy + fixed 的测试，确定所有时间！

接下来的任务：研究构造 CWE 数据集！
今晚继续跑了一下两组 pred，明天早上看一下 epoch 近似等于 1 以及 epoch=2 但是 max_len 分别调整到 2048 和 1024 的效果？

目前的进展：
    马上跑出来了测试 d4j 数据集时的时间基准：加起来大概 8 个小时
    有两组数据需要我们测试：一组是 epoch=1 的，另外一组是 epoch=2 情况下，将 max_len 改成 2048 + 512 的
    尤其是第二组，如果我们将 生成 的参数调整之后，那么结果可以与原始 1024 + 256 情况下的结果相合并

# 0128 进展
目前，最好的结果没有能够超过 167
如果把 epoch=1 的情况和 epoch=2 的情况合并，那么能上升到 195

现在我正在抓紧处理 juliet 数据集，一共有 28881 条，但是每一条中可能有多种 fix！
文件数目有 1~5 这几种可能，并且文件名的后缀基本都是固定格式的，接下来我们分别研究其

今天跑了一下新的——使用 epoch=2 训练的 epoch=1 的 ckpt 进行 inference 的生成结果

# 0130
现在正在研究如何在中间模型的基础上，继续微调（基于 cwe 的数据）

# 0202
使用 double file 版本训练好模型之后，应当在 codellama-cwe 测试集（验证集）上测试一下预测的准确性。
首先应当在 原始验证集 上，试一下模型接收 bad code 输出 cwe 的能力！（生成，然后与实际值进行比较，同时兼顾看一下 生成格式是否遵循微调数据格式）
当务之急：修改一下 llama_pred 文件，改为 llama_pred_cwe_category 文件，接收 input bad code，预测 cwe gategory（output_patch）

对于 d4j 而言，进行 cwe pred 阶段，需要：buggy_code（应该需要重新构造？），并且没有 可供参考的 cwe category
因此，我们直接对 d4j 数据集的 483 个 input，全部输出我们推测的类别即可！

# 新想法
作者还留下了 top_p top_k 等说法，我们是否可以在 only_do_beam 之外，对于 d4j 数据集继续做一次新的实验？
export CUDA_VISIBLE_DEVICES="0"
python llama_pred_cwe_category.py \
    --base_model_path /data/lihy/models/CodeLlama-7b-Instruct-hf \
    --lora_path /data/lihy/training_output/codellama-cwe/finetuned-models_maxlen=1024_epoch=3_juliet-files=2 \
    --data_path /data/lihy/datasets/java-juliet/src/parsed_dataset/parquet \
    --test_file finetuning_data_maxlen_1024_codellama-cwe_2_test.parquet \
    --test_file_from_d4j False \
    --output_file /data/lihy/testing_output/codellama-cwe/cwe_output_dataset=juliet_maxlen=1024_maxnew=128_training-epoch=3_juliet-files=2.jsonl \
    --is_lora True \
    --max_length 1024 \
    --max_new_tokens 128 \
    --do_sample True \
    --only_do_beam True \
    --only_do_topp False \
    --only_do_topk False \
    --only_do_temp False \
    --num_beams 10 \
    --temperature 0.8 \
    --top_k 0 \
    --top_p 0.95 \
    --request_num 10 \

# 任务
1. 跑起来 repairllama-cwe 的新模型（二轮微调）在 d4j 数据集上的生成实验，这需要重写一个 run_llama_pred
2. 跑一下加入了 top_p、top_k 等参数的 d4j patches 生成（目的是看一看效果是不是比单纯的 beam_search 更好！）

# 0224 更新
前两天 codellama-cwe 分别在 lora 和 qlora 上跑了一组训练，都分别训练了 5 个 epoch
今天，可以将 repairllama-cwe 的数据运用起来，仍然使用 lora + qlora，各 4 张卡跑实验！

inference 部分，前两天跑出来的 codellama-cwe 模型，有两组，可以分别在 codellama-cwe-test（分离出来的测试集）以及 d4j 上进行 inference，看一下出来的结果如何
另外，春节期间训练完毕的 qlora + megadiff + 5 epoch 可以在 defects4j 上跑一下生成？主要是需要修改一下 single_chat 脚本，或者看一下新版 firefly 的 chat 脚本

# 0226 更新
写完今天的周报，最近的主要任务是：
1. 修改数据格式，将提问环节后置，然后看看最后的效果如何
2. 解决一下 lora 版本在 inference 时，耗时长、显存占用高（60G+）的问题
3. 将 qlora 版本的脚本改好，换用 qlora 进行推理和测试

拆开来看，今晚要跑的实验：
1. 修改数据格式到后面，然后在 A100 上跑训练（lora + qlora，实际上应该是两组）
2. 降低 beam_size，看看显存占用能否降低，并且这次将 max_token 设定为 64（32 行不行呢？）

# 0313 更新
H100 资源没了之后，火速学习一下多卡推理！
找到的链接是使用 accelerate 针对 llama2-7b 模型，在 3090 上进行推理
