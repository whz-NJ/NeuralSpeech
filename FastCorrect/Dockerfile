FROM nvidia/cuda:10.2-cudnn7-devel-centos7
LABEL maintainer="migu"
#设置中文
ENV LANG en_US.UTF-8
#设置时区
ENV TZ=Asia/Shanghai
ENV PYTHONIOENCODING=utf-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN yum install -y python3 --nogpgcheck
RUN pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
COPY requirements.txt /root/fc/
COPY numpy-1.19.5-cp36-cp36m-manylinux2010_x86_64.whl /root/fc/
RUN cd /root/fc/ && pip3 install ./numpy-1.19.5-cp36-cp36m-manylinux2010_x86_64.whl
COPY torch-1.6.0-cp36-cp36m-linux_x86_64.whl /root/fc/
RUN cd /root/fc/ && pip3 install ./torch-1.6.0-cp36-cp36m-linux_x86_64.whl
RUN pip3 install -r /root/fc/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN cd /root/fc/ && rm -rf ./numpy-1.19.5-cp36-cp36m-manylinux2010_x86_64.whl ./torch-1.6.0-cp36-cp36m-linux_x86_64.whl ./requirements.txt
COPY std_ftb_sports_corpus_en.bin /root/fc/std_ftb_sports_corpus_en.bin/
COPY fastcorrect/ /root/fc/fastcorrect/
WORKDIR /root/fc/fastcorrect
#CMD python3 run_detect_server.py --instanceId=1
#gunicorn -k gevent -c ./app/config/gun_basic.cfg run_fc:webapp
CMD ["/usr/local/bin/gunicorn", "-k", "gevent", "-c", "./app/config/gun_basic.cfg", "run_fc:webapp"]

