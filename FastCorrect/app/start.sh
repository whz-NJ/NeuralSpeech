cd /root/fc/fastcorrect
nohup /usr/local/bin/gunicorn -k gevent -c ./app/config/gun_basic.cfg run_fc:webapp > /dev/null 2>&1 &
