#!/bin/bash

#SBATCH --nodelist=g3027
#SBATCH --partition=gpu3-2
#SBATCH --nodes=1

#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:0
#SBATCH --cpus-per-task=1
#SBATCH --mem=0G

cd /home/lihaoyu # 改为用户目录
module load rootless-docker/default
start_rootless_docker.sh
# stop_rootless_docker.sh

docker run -itd --gpus all -v `pwd`:/home/lihaoyu nvidia/cuda:11.6.2-base-ubuntu20.04 bash
# docker exec `docker ps -lq` bash /home/cuijunbo/Rhapsody-Musical-Memory/scripts/env_docker/run_docker_init.sh
docker exec -it `docker ps -lq` bash # 交互式运行，进入docker，然后执行bash docker_script.sh

sleep 90