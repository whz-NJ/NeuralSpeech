import os
from configparser import ConfigParser

config = ConfigParser()
config.read(filenames='/root/fc/fastcorrect/app/config/config.cfg', encoding='utf8')

# yolo 安装目录
pwd = os.getcwd()

# 是否使用GPU
GPU = True
# 是否指定GPU INDEX(1：指定，0：不指定)
GPU_INDEX_ON_OFF = int(config['system']['GPU_INDEX_ON_OFF'])
# GPU设备指定
GPU_DEVICE = config['system']['GPU_DEVICE']

# 日志配置
LOG_PATH = config['log_info']['LOG_PATH']
# the loggers file for post server
IS_POST_SERVER = False
LOG_PRE = ""

BS_LOG_FILE = os.path.join(LOG_PATH, LOG_PRE + config['log_info']['BS_LOG_FILE'])
ERROR_LOG_FILE = os.path.join(LOG_PATH, LOG_PRE + config['log_info']['ERROR_LOG_FILE'])
LOG_FORMAT = config.get('log_info', 'LOG_FORMAT', raw=True)
ROOT_LOG_LEVEL = int(config['log_info']['ROOT_LOG_LEVEL'])
DATA_BS_LOG_LEVEL = int(config['log_info']['DATA_BS_LOG_LEVEL'])
LOG_ROTATE = config['log_info']['LOG_ROTATE']
LOG_BACKUP_COUNT = int(config['log_info']['LOG_BACKUP_COUNT'])
EPOCH = config['system']['EPOCH']

# [post_server_info]
# 服务IP
SERVE_HOST = config['server_info']['SERVE_HOST']
# 服务端口
SERVE_PORT = config['server_info']['SERVE_PORT']


# model
# YOLOV5_PATH=config['label_info']['YOLOV5_PATH']
# THRESH = config['model']['THRESH']
