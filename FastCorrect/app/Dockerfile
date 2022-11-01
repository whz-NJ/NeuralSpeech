FROM nvidia/cuda:10.2-cudnn7-devel-centos7
LABEL maintainer="migu"
#设置中文
ENV LANG en_US.UTF-8
#设置时区
ENV TZ=Asia/Shanghai
ENV PYTHONIOENCODING=utf-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#配置yum源
RUN rm /etc/yum.repos.d/*.repo
COPY yum.repos/ /root/fc/yum.repos/
RUN cd /root/fc/yum.repos/ && cp *.repo /etc/yum.repos.d/
#拷贝安装python3.6(离线rpm方式)
COPY whl_rpm_pkgs/ /root/fc/whl_rpm_pkgs/
RUN cd /root/fc/whl_rpm_pkgs/python3.6.8/ && rpm -Uvh ./*.rpm --nodeps --force
#pip升级(在线方式)
RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
#安装numpy/torch组件(离线whl方式)
RUN cd /root/fc/whl_rpm_pkgs/ && pip3 install ./numpy-1.19.5-cp36-cp36m-manylinux2010_x86_64.whl
RUN cd /root/fc/whl_rpm_pkgs/ && pip3 install ./torch-1.6.0-cp36-cp36m-linux_x86_64.whl
#安装fastcorrect倚赖组件(在线方式)
COPY requirements.txt /root/fc/
RUN pip3 install -r /root/fc/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
#删除不用的whl/rpm安装包，以及yum源等
RUN cd /root/fc/ && rm -rf ./yum.repos ./whl_rpm_pkgs ./requirements.txt
#拷贝fastcorrect模型需要字典数据文件
COPY std_noised_sports_corpus4.bin /root/fc/std_noised_sports_corpus4.bin/
#拷贝fastcorrect模型代码包和启停脚本
COPY fastcorrect/ /root/fc/fastcorrect/
COPY start.sh /root/fc/
COPY stop.sh /root/fc/
#设置工作目录和启动命令
WORKDIR /root/fc
CMD ["/usr/local/bin/gunicorn", "-k", "gevent", "-c", "./config/gun_basic.cfg", "run_fc:webapp"]