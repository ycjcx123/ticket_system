这是电影院购票系统的课程设计，前端使用html+css+js,后端使用python+flask+pymysql，数据库使用mysql.

------

app文件夹为后端代码

web文件夹为前端代码，static文件夹存放css,img等文件，templates文件夹存放html文件

------
app文件夹中：
start.py为主程序，从这里启动后端服务；
DB.py为数据库连接服务；
login.py为登录模块，负责用户的登录，注册，管理员的登录。
user.py为用户模块，负责用户的个人信息，订单信息，购票信息等的管理。
movie负责电影卡的生成，电影排期的生成，座位的生成等。
order负责查看订单和删除。

------
web文件夹中：
login为登录界面，负责用户的登录，注册，管理员的登录。
user为用户界面，负责用户的个人信息，订单信息，购票信息等的管理。
admin为管理员界面，负责管理员的管理，包括用户管理，电影管理，订单管理等。
schedule为电影排期界面，负责电影排期。
seat为座位界面，负责显示电影院的座位信息。
create_schedule为创建电影排期界面，负责创建电影排期。
order为订单界面，负责显示用户的订单信息。管理员查看订单复用该界面。

------
movie_spider文件夹中：
这是用来爬虫的代码，用于爬取豆瓣网的电影信息，然后使用trans.py转换成数据库需要的格式。
movie_images已经处理过一次了，所有数据会少很多

------
接下来是配置教程：
首先安装python3.11.8然后安装mysql，添加到系统环境变量中
解压文件夹，然后在文件夹中启动终端，输入:`python3 -m venv .venv`，用于创建名为.venv的虚拟环境
然后在继续在该文件夹中输入`.\.venv\Scripts\activate`，激活虚拟环境
最后输入：`pip install -r requirements.txt`，下载依赖包
这时候环境就完全配置好了。

随后配置数据库，创建个新数据库，这里我们将其命名为：ticket_system。随后将mysql.txt中的代码复制到终端中并运行，创建表和触发器。

随后打开movie/insert_DB.py文件，修改数据路径为你自己的路径，修改POOL中的user,password,database为自己刚刚创建的mysql数据库的用户名，密码和数据库名，根据需要，调用insert_movie，insert_hall，insert_seat，其中movie是读取movies_data.json文件，hall是在代码中自定义，seat是根据row和col，aim_hall来对aim_hall影厅生成座位。

之后，直接在admin表中插入管理员的账户，密码。

并且在app/DB.py中类似前两步的修改，修改POOL内容。

就在虚拟环境中，打开app/start.py，便可直接运行了。


```
DataBase
├── readme.md
├── requirements.txt
├── mysql.txt
├── web
│   ├── templates
│   │   ├── admin.html
│   │   ├── create_schedule.html
│   │   ├── login.html
│   │   ├── order.html
│   │   ├── schedule.html
│   │   ├── seat.html
│   │   └── user.html
│   └── static
│       ├── admin.css
│       ├── base.css
│       ├── creat_schedule.css
│       ├── login.css
│       ├── order.css
│       ├── schedule.css
│       ├── seat.css
│       ├── user.css
│       └── movie_images
├── movie
│   ├── main.py
│   ├── movies_data.json
│   ├── movies_data_org.json
│   ├── trans.py
│   └── movie_images
└── app
   ├── admin.py
   ├── create_schedule.py
   ├── DB.py
   ├── login.py
   ├── movie.py
   ├── order.py
   └── start.py```