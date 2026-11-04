#/bin/bash
# 端口必须与 nginx 的 proxy_pass 一致（nginx_http.conf / nginx_https.conf 均为 7290）
# 生产环境关闭 DEBUG（不设置 DJANGO_DEBUG 或设为 0 都会关闭；本地开发想开调试：DJANGO_DEBUG=1 ./run.sh）
export DJANGO_DEBUG=0
nohup ../venv/bin/python3 manage.py runserver localhost:7290 &
