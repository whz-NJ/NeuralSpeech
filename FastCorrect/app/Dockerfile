FROM nvidia/cuda:10.2-cudnn7-devel-centos7
LABEL maintainer="migu"
#设置中文
ENV LANG en_US.UTF-8
#设置时区
ENV TZ=Asia/Shanghai
ENV PYTHONIOENCODING=utf-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN rm /etc/yum.repos.d/*.repo
COPY yum.repos/ /root/fc/yum.repos/
RUN cd /root/fc/yum.repos/ && cp *.repo /etc/yum.repos.d/
#COPY BCLinux-BaseOS.repo /etc/yum.repos.d/
#COPY BCLinux-Kernel.repo /etc/yum.repos.d/
#COPY BCLinux-PowerTools.repo /etc/yum.repos.d/
#COPY epel.repo /etc/yum.repos.d/
#RUN yum clean all
#RUN yum install -y python36 --nogpgcheck
COPY whls/ /root/fc/whls/
RUN cd /root/fc/whls/python3.6.8/ && rpm -Uvh ./*.rpm --nodeps --force
#RUN pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY requirements.txt /root/fc/
RUN cd /root/fc/whls/ && pip3 install ./numpy-1.19.5-cp36-cp36m-manylinux2010_x86_64.whl
RUN cd /root/fc/whls/ && pip3 install ./torch-1.6.0-cp36-cp36m-linux_x86_64.whl
#RUN pip3 install -r /root/fc/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
RUN pip3 install -r /root/fc/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN cd /root/fc/ && rm -rf ./yum.repos ./whls ./requirements.txt
COPY std_noised_sports_corpus4.bin /root/fc/std_noised_sports_corpus4.bin/
COPY fastcorrect/ /root/fc/fastcorrect/
COPY start.sh /root/fc/
COPY stop.sh /root/fc/
WORKDIR /root/fc
#CMD python3 run_detect_server.py --instanceId=1
#gunicorn -k gevent -c ./app/config/gun_basic.cfg run_fc:webapp
CMD ["/usr/local/bin/gunicorn", "-k", "gevent", "-c", "./config/gun_basic.cfg", "run_fc:webapp"]

