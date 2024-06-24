
栈鱼 Admin Panel 是基于flask 2.0框架开发的一个通用后台管理系统，数据库及后台的功能参考了国内的fastadmin。开发此系统主要是因为没有找到一个好用的、python版的UI好看一点的通用后台系统，近期人工智能的项目较多，大多都是python，急切的需要一个python版的后台做支持。

栈鱼的来历，作者是一只做全栈开发的鱼。开发应该是热爱的人做自由的事。

选择flask的原因：flask用的人多

框架：flask

模版：jinja2

前端：基于bootscrap的tablerUI库+jQuery

时间选择器：flatpickr 4.6.13

toast：toastr.js 2.1.4

图标库：tabler-icons

粘贴板：clipboard.js 2.0.11

jquery：jquery 3.7.1

表单验证：jquery-validate 1.19.5 

其他更新中...

目前开发了3个插件:
-------------------------------------------
1.demo插件，演示系统的表单提交。

2.代码生成器，可以根据设计好的数据表自动生成model，模版，views，还有对应的js文件，数据表的CRUD功能就有了。

3.会员余额充值插件，集成了国内常用的微信和支付宝支付接口。下一个插件是vip购买插件，开发中...

以上3个插件基本就可以满足搭建一个灵活度很高的后台系统了，flask优质的插件功能，非常适合大型项目。

开发中的插件：极光认证，微信支付宝第三方登录

--------------------

Getting Started（安装如下步骤）
------------------------------------------

如果您还未切换到新创建的项目目录，请进入该目录。当前工作目录应当与本 README.txt 文件和 setup.py 文件所在目录相同。

1.安装

安装 SQLite3 及其开发包：

```
sudo apt-get install libsqlite3-dev

```

克隆：

```
git clone https://github.com/easyiit-com/flask-admin-panel.git
```

进入目录

```
cd flask-admin-panel
```

2.如果尚未创建，请创建一个 Python 虚拟环境，创建虚拟环境：

```
python3 -m venv .venv

. .venv/bin/activate

```


3.更新 pip 和 setuptools 工具：


```
.venv/bin/pip install --upgrade pip setuptools
```

4.使用包含测试依赖项的方式，以可编辑模式安装项目。

安装项目及测试依赖：

```
pip install -e ".[testing]"
```


如出现错误：

Can not find valid pkg-config name. Specify MYSQLCLIENT_CFLAGS and MYSQLCLIENT_LDFLAGS env vars manually [end of output]

对于Ubuntu/Debian系Linux，可以运行以下命令安装MySQL开发库：
 
```
sudo apt-get update
```

```
sudo apt-get install libmysqlclient-dev

```

对于CentOS需执行：

```
sudo dnf install mysql-devel

```


5.使用 Alembic 初始化并升级数据库，生成首个修订版本。

执行这一步之前，需配置好根目录下的alembic.ini文件的63行和根目录下面config.py文件中的20行的数据库连接信息：

sqlalchemy.url = mysql://root:123456@localhost:3306/flask_admin_panel_100?charset=utf8mb4


6.执行数据库迁移：

```
alembic revision --autogenerate -m "init"

```

```
alembic upgrade head
``` 

7.使用脚本将默认数据加载到数据库中。


加载默认数据至数据库：

```
python initialize_db.py
```

8.运行项目的测试。

执行测试：

```
 
```

9.运行项目。
启动项目服务：

```
flask --app main run --debug 

```
或
```
python main.py

```

gunicorn启动命令：

```



```

未安装gunicorn，则需要执行以下命令安装：

```
 .venv/bin/pip install gunicorn
```

启动后默认访问地址：http://127.0.0.1:5000

后台地址：http://127.0.0.1:5000/admin
默认用户名：admin@admin.com
默认密码：88888888
 
10.进入生产环境

Nginx服务器反向代码配置实例：
```
server
{
    listen 80;
    server_name admin.zhanor.com;
    index index.html index.htm default.htm default.html;
    root /www/python_venv/flask_admin_panel/__init__.py;

    #SSL-START SSL相关配置
    #error_page 404/404.html;
    
    #SSL-END

    #ERROR-PAGE-START  错误页相关配置
    #error_page 404 /404.html;
    #error_page 502 /502.html;
    #ERROR-PAGE-END


    #REWRITE-START 伪静态相关配置
    include /www/server/panel/vhost/rewrite/other___init___py.conf;
    #REWRITE-END

    #禁止访问的文件或目录
    location ~ ^/(\.user.ini|\.htaccess|\.git|\.svn|\.project|LICENSE|README.md|package.json|package-lock.json|\.env) {
        return 404;
    }

    #一键申请SSL证书验证目录相关设置
    location /.well-known/ {
        root /www/wwwroot/java_node_ssl;
    }

    #禁止在证书验证目录放入敏感文件
    if ( $uri ~ "^/\.well-known/.*\.(php|jsp|py|js|css|lua|ts|go|zip|tar\.gz|rar|7z|sql|bak)$" ) {
        return 403;
    }


    # HTTP反向代理相关配置开始 >>>
    location ~ /purge(/.*) {
        proxy_cache_purge cache_one 0.0.0.0$request_uri$is_args$args;
    }

    location / {
        proxy_pass http://0.0.0.0:5000;
        proxy_set_header Host admin.zhanor.com:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header REMOTE-HOST $remote_addr;
        add_header X-Cache $upstream_cache_status;
        proxy_set_header X-Host $host:$server_port;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 86400s;
        proxy_send_timeout 30s;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    # HTTP反向代理相关配置结束 <<<

    access_log  /www/wwwlogs/__init___py.log;
    error_log  /www/wwwlogs/__init___py.error.log;
}
```
Apache配置实例：
待更新



11.i18n多语言支持
待更新

