cd /home/lihaoyu/szx/proj/code-repair/defects4j
cpanm --installdeps .
./init.sh
export PATH=$PATH:/home/lihaoyu/szx/proj/code-repair/defects4j/framework/bin

# # 
# defects4j info -p Lang

# defects4j checkout -p Lang -v 1b -w ./tmp/lang_1_buggy
# # 查看htop进程占用内存
# # htop -u cuijunbo