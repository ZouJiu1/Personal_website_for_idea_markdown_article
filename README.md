# the website of myself using below open source projects
[http://zoujiu.com.cn](http://zoujiu.com.cn)

support idea post, reading book post, personal introduction with images, traveler post and video upload

support markdown article, including Math Latex, table, list and so on.

## 1. environment
`element-plus + django + vue3`

### 1.1 npm + nodejs

>**Macos**: `brew install node@22`

[https://nodejs.org/zh-cn/download](https://nodejs.org/zh-cn/download)

[install brew help---https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/](https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/)

according to homebrew's tips at tail, add to environment variables

`echo 'export PATH="/usr/local/opt/node@22/bin:$PATH"' >> ~/.zshrc`

`export PATH="/usr/local/opt/node@22/bin:$PATH"`

compile setting
```
  export LDFLAGS="-L/usr/local/opt/node@22/lib"
  export CPPFLAGS="-I/usr/local/opt/node@22/include"
```

**reboot your macos system computer to make effect**

### 1.2 set mirror
>`npm config set registry https://registry.npmmirror.com`

### 1.3 download packages
>cd /Users/zoujiu/Desktop

>npm create vue@latest
------all default, don't change anything
[https://cn.vuejs.org/guide/quick-start](https://cn.vuejs.org/guide/quick-start)

>cd /Users/zoujiu/Desktop/vue-project

>npm install element-plus --save

[https://element-plus.org/zh-CN/guide/installation.html](https://element-plus.org/zh-CN/guide/installation.html)

>npm install axios --save

>npm install hls.js --save

[https://github.com/video-dev/hls.js](https://github.com/video-dev/hls.js)

>npm install js-cookie --save

[https://github.com/js-cookie/js-cookie](https://github.com/js-cookie/js-cookie)

>npm install katex --save

[https://katex.org/docs/node](https://katex.org/docs/node)

>npm install vue-router@4 --save

[https://router.vuejs.org/zh/installation.html](https://router.vuejs.org/zh/installation.html)

### 1.four git clone
>cd /Users/zoujiu/Desktop

>`git clone https://github.com/ZouJiu1/Personal_website_for_idea_markdown_article.git`

>cp -rf Personal_website_for_idea_blog_article/*  ./vue-project

now, you have some directorys like these:

---Desktop

--------vue-project

------------mysite

------------src

------------people

...

### 1.5 Python set up
> cd /Users/zoujiu/Desktop/vue-project

>python3 -m venv ./venv

>source ./venv/bin/activate

>python3 -m pip install -r ./mysite/requirements.txt


## 2. Run
### 2.1 all project
>cd /Users/zoujiu/Desktop/vue-project

>`npm run dev -- --port 9000`

>source ./venv/bin/activate

>cd mysite

python3 manage.py runserver localhost:7009

## 3. release
### 3.1 packaging
>cd /Users/zoujiu/Desktop/vue-project

>npm run build

>cd mysite && python3 manage.py runserver localhost:7009

### 3.2 nginx
>sudo apt-get install nginx

or

>./configure --sbin-path=/home/admin/vue-project/nginx/nginx-1.26.2/bin --conf-path=/home/admin/vue-project/nginx/nginx-1.26.2/conf/nginx.conf --pid-path=/home/admin/vue-project/nginx/nginx-1.26.2/nginx.pid --with-http_ssl_module --add-module=/home/admin/vue-project/nginx/nginx-1.26.2/nginx-rtmp-module-master  --with-pcre=/home/admin/vue-project/nginx/nginx-1.26.2/pcre2-10.44 --with-openssl=/home/admin/vue-project/nginx/nginx-1.26.2/openssl-3.3.2  --user=root  --error-log-path=/home/admin/vue-project/nginx/nginx-1.26.2/error.log

**nginx.conf configuration**

http like this: [nginx_http.conf](./nginx_http.conf), you may need modify some path according to your directory. 

https with ssl_certificate like this: [nginx_https.conf](./nginx_https.conf), you may need modify some path according to your directory. 

### 3.3 start or restart
start: `nginx -c /etc/nginx/conf/nginx.conf`

stop: `nginx -s stop`

restart: `nginx -s restart`

after building src with `npm run build`、launching **django** and launching **nginx**, you can visit this website in **http://localhost**

## 4. administer
### 4.1 administer account and password
>account: **homepage@gmail.com**

>password: **01ab!+**

### 4.2 change administer password
>cd /Users/zoujiu/Desktop/vue-project

>modify the genpassword.py with `password = 01ab!+`

```python []
python3 genpassword.py

will get genpassword file, which content is:

01ab!+
83e6936fb8d502de61ebab5f4b7babf007eacff9324cf59bcc03c1012510000b
```

>modify the genpassword.py with `password = 06hj@#`

```python []
python3 genpassword.py

will get genpassword file, which content is:

06hj@#
34629c7dd225e65c1ba6e884ffde42edf6d253fd0df4eb6dd4c897959d89aeb1
```

```text []
edit file "vue-project/article/member.txt", change the password from 01ab!+ to 06hj@#

modify

83e6936fb8d502de61ebab5f4b7babf007eacff9324cf59bcc03c1012510000b<》!=$)(=$@homepage@gmail.com<》!=$)(=$@邹九<》!=$)(=$@1000000

to

34629c7dd225e65c1ba6e884ffde42edf6d253fd0df4eb6dd4c897959d89aeb1<》!=$)(=$@homepage@gmail.com<》!=$)(=$@邹九<》!=$)(=$@1000000
```

**now, you can use the new password to log in**


## other register user
you can use your email to change your password after you log in

because you have no access to modify the "vue-project/article/member.txt"

only the repo owner have access to it

## email setting
File `vue-project/mysite/csdn/views.py`

Function `def mailsend(mail, modify=False, notify_guanliyuan=None):`

change the password `smpt.login(user="1069679911@qq.com", password='zzzzzzzzzzzzz')`, open the service **POP3/IMAP/SMTP/Exchange/CardDAV**

```python []
    msg['From'] = '1069679911@qq.com'
    msg['To'] = mail
    # smtplib.SMTP()
    smpt = smtplib.SMTP_SSL("smtp.qq.com", port=465)
    # smpt.connect("smtp.qq.com", port=465)
    smpt.login(user="1069679911@qq.com", password='zzzzzzzzzzzzz')
```

Function `def notify_administer(dir, truemail, mail, urlmail, own=True, action='delete'):`

```python []
try:
    mailsend('1069679911@qq.com', modify=False, \
            notify_guanliyuan=['---delete', \
            f'{mail} delete {urlmail}\n\ncontent: \n{dir}\n\nnowdir: \n{urlmaildir}'])
```

## my blogs

[http://zoujiu.com.cn](http://zoujiu.com.cn)

[https://zoujiu.blog.csdn.net/](https://zoujiu.blog.csdn.net/)
