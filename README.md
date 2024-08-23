
# ZhanYu Admin Panel

ZhanYu Admin Panel is a general backend management system developed based on the Flask 2.0 framework. The database and backend functionalities are inspired by the domestic FastAdmin. The primary motivation for developing this system was the lack of a well-designed, Python-based, and aesthetically pleasing general-purpose admin panel. Recently, there have been numerous AI projects, most of which are based on Python, creating an urgent need for a Python-based backend to support them.

**Origin of ZhanYu**: The author is a fish that does full-stack development. Development should be something that passionate people do freely.

## Screenshots

![Example Image](screen_shot/admin.png)
![Example Image](screen_shot/dashboard.png)
![Example Image](screen_shot/general_category_add.png)
![Example Image](screen_shot/general_category.png)
![Example Image](screen_shot/general_config.png)
![Example Image](screen_shot/generattor.png)
![Example Image](screen_shot/profile.png)

## Why Flask?

Flask is widely used.

- **Framework**: Flask
- **Template**: Jinja2
- **Frontend**: Based on the TablerUI library using Bootstrap + jQuery
- **Date Picker**: Flatpickr 4.6.13
- **Toast**: Toastr.js 2.1.4
- **Icon Library**: Tabler-icons
- **Clipboard**: Clipboard.js 2.0.11
- **jQuery**: jQuery 3.7.1
- **Form Validation**: jQuery-validate 1.19.5

Other updates are ongoing...

## Currently Developed Plugins

1. **Demo Plugin**: Demonstrates the system's form submission.
2. **[Code Generator](https://github.com/easyiit-com/generator-for-flask-admin-panel)**: Automatically generates models, templates, views, and corresponding JS files based on designed data tables, enabling CRUD functionality for the data tables.
3. **Member Balance Recharge Plugin**: Integrates commonly used WeChat and Alipay payment interfaces in China. The next plugin under development is the VIP purchase plugin.

These three plugins can basically meet the needs of building a highly flexible backend system. Flask's excellent plugin functionality is very suitable for large projects.

### Plugins Under Development

- Jiguang Authentication
- WeChat and Alipay Third-Party Login

## Getting Started

Follow the steps below to install:

If you have not switched to the newly created project directory, please enter the directory. The current working directory should be the same as where this `README.txt` file and `setup.py` file are located.

### 1. Installation

Install SQLite3 and its development package:

```
sudo apt-get install libsqlite3-dev

```

Clone the repository:

```
git clone https://github.com/easyiit-com/flask-admin-panel.git
```

Enter the directory:

```
cd flask-admin-panel
```

2. Create a Python Virtual Environment (if not already created)

```
python3 -m venv .venv

. .venv/bin/activate

```

3. Update pip and setuptools tools


```
pip install --upgrade pip setuptools
```

4. Install the project in editable mode, including testing dependencies
 

```
pip install -e ".[testing]"
```


If an error occurs:

Can not find valid pkg-config name. Specify MYSQLCLIENT_CFLAGS and MYSQLCLIENT_LDFLAGS env vars manually [end of output]

For Ubuntu/Debian-based Linux, you can install the MySQL development library with the following command:


 
```
sudo apt-get update
```

```
sudo apt-get install libmysqlclient-dev

```

For CentOS, execute:

```
sudo dnf install mysql-devel

```


5. Initialize and upgrade the database using Alembic to generate the first revision
Before executing this step, configure the database connection information in line 63 of the alembic.ini file and line 20 of the config.py file in the root directory:

sqlalchemy.url = mysql://root:123456@localhost:3306/flask_admin_panel_100?charset=utf8mb4


6. Perform a database migration

```
alembic revision --autogenerate -m "init"

```

```
alembic upgrade head
``` 

7. Load default data into the database


7. Load default data into the database


```
python initialize_db.py
```

8. Run the project tests
To execute tests:

```
 
```

9. Run the project
Start the project server:

```
flask --app main run --debug 

```
or
```
python main.py

```

Gunicorn startup command:

```



```
If Gunicorn is not installed, execute the following command to install:



```
 .venv/bin/pip install gunicorn
```

After startup, the default access address is: http://127.0.0.1:5000

Admin panel address: http://127.0.0.1:5000/admin

Default username: admin@admin.com

Default password: 88888888

10. Entering Production Environment
Nginx server reverse proxy configuration example:
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



11. i18n Multilingual Support
When adding a new template, if you need to use multiple languages, you need to update the language pack. The steps are as follows:

a. Install Dependencies
```
pip install Flask-Babel2 Babel


```

b. Extract messages
In the project's root directory, execute the following command:

```
pybabel extract -F babel.cfg --no-location -o app/locales/local_all.pot .

```
--no-location parameter is to hide file paths.

c. Initialize Language Files
For each language, initialize a .po file, for example en and zh, by executing:

```
pybabel init -i app/locales/local_all.pot -d app/locales -l en
pybabel init -i app/locales/local_all.pot -d app/locales -l zh
```
This will create:

app/locales/en/LC_MESSAGES/messages.po
app/locales/zh/LC_MESSAGES/messages.po
d. Compile Translation Files
Compile the .po files into .mo format:

```
pybabel compile -d app/locales
```

e. Update Translation Files
When your application has new strings to translate or the source strings of existing translations have changed, you typically need to re-run the pybabel extract command to update the .pot file (template file) to include the new and changed strings. The steps are as follows:

First, make sure your babel.cfg configuration file correctly specifies the Python source code, templates, and other files that need translation extraction.

Run the pybabel extract command to re-extract the translation template:

```
pybabel extract -F babel.cfg --no-location -o zhanor_admin/locales/zhanor_admin.pot .
```

This command will search for marked translatable strings in the source code and other files in the current directory and update the specified .pot template file.

Review the generated .pot file to confirm that it contains the expected new and modified strings.

Next, merge the updated template file into each language’s .po file so that the translation team can add or update the corresponding language translations in these files:

```
pybabel update -i zhanor_admin/locales/zhanor_admin.pot -d zhanor_admin/locales/

```
This command will automatically add new content to the existing .po files in the respective language directories while preserving the existing translations.

After the translation is complete, compile the .po files into binary .mo files for the application to load at runtime:

```
pybabel compile -f -d zhanor_admin/locales/
```
By following the above steps, your internationalization (i18n) process can keep pace with project development and ensure that the latest translation resources are always available.