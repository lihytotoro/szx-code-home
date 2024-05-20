# 这是安装 python 3.10 卡死之后应该执行的命令
ps aux | grep apt

kill -9 pid
rm /var/lib/dpkg/lock-frontend
rm /var/lib/apt/lists/lock
rm /var/cache/apt/archives/lock