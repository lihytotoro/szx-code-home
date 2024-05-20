# echo y | apt update

# echo y | apt-get install python3.10
echo y | apt-get install libfreetype6 xfonts-75dpi xfonts-base
echo y | apt --fix-broken install

# echo y | apt upgrade

# install subversion
echo y | apt-get install subversion
# curl
echo y | apt-get install curl
# unzip
echo y | apt-get install unzip
# install perl
echo y | apt-get install perl
# install git
echo y | apt-get install git
# install htop
echo y | apt-get install htop
# install pip
echo y | apt-get install python3-pip

# install java
echo y | apt-get install openjdk-8-jdk

# cpan install cpanm
apt-get install cpanminus
cpan App::cpanminus

# 
# ./init.sh
# export PATH=$PATH:"/home/cuijunbo/Rhapsody-Musical-Memory/src/defects4j"/framework/bin

# # 
# defects4j info -p Lang

# defects4j checkout -p Lang -v 1b -w ./tmp/lang_1_buggy
# # 查看htop进程占用内存
# # htop -u cuijunbo