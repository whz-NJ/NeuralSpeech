# 该脚本需要放在 fastcorrect 的上一级目录
rm -f Dockerfile
cp fastcorrect/app/Dockerfile .

if [ ! -d logs ]; then
    mkdir logs
fi
if [ -f logs/system.log ]; then
    cat /dev/null >  logs/system.log
fi
if [ -f logs/error.log ]; then
    cat /dev/null >  logs/error.log
fi

rm -rf config
cp -r fastcorrect/app/config .
rm -f fastcorrect/run_fc.py
cp fastcorrect/app/run_fc.py fastcorrect
chmod +x fastcorrect/run_fc.py
rm -f start.sh && cp fastcorrect/app/start.sh . && chmod +x start.sh
rm -f stop.sh && cp fastcorrect/app/stop.sh . && chmod +x stop.sh
docker build -t fastcorrect:1.0 .
