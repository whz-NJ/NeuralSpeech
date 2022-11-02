#!/bin/bash
# 容器名称
DOCKER_NAME=fc_gpu_28900
# 日志目录
LOG_PATH=fc_28900
# 项目名称目录
PROJECT_NAME=FC_MidPlatform_GPU
# 代码目录
# CODE_PATH=HQ_TTS
# 服务对外服务端口 按情况更改
LOCAL_PORT=28900
# 容器内部服务端口
DOCKER_PORT=5051
# torch1.6:cuda10.1为镜像名称
IMAGE_NAME=fastcorrect:1.0

LOCAL_LOG_DIR=/root/fc/logs
DOCKER_LOG_DIR=/root/fc/logs

#models_path 服务器模型存放路径，按情况更改
LOCAL_MODELS_PATH=/root/fc/models
DOCKER_MODELS_PATH=/root/fc/models

LOCAL_CONFIG_PATH=/root/fc/config
DOCKER_CONFIG_PATH=/root/fc/config

# export DOCKER_PORT
# NV_GPU 指定使用的GPU序号; ??启动命令哪里指定 GPU序号
#/etc/localtime：更新容器时间
# 当不用GPU时，或者是不准备用GPU时，启动命令中 NV_GPU=2 nvidia-docker 改为 docker      # -v /data/wanglieqi/python_project//${PROJECT_NAME}:/workspace/${PROJECT_NAME}/ \
nvidia-docker run --restart=always --gpus "device=5" -dti -u root -p ${LOCAL_PORT}:${DOCKER_PORT} \
     -v ${LOCAL_LOG_DIR}:${DOCKER_LOG_DIR} \
     -v /etc/localtime:/etc/localtime:ro \
     -v ${LOCAL_MODELS_PATH}:${DOCKER_MODELS_PATH} \
     --name ${DOCKER_NAME} \
	 ${IMAGE_NAME}
