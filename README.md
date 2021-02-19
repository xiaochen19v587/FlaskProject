## FlaskProject 运行环境

### Linux环境

```shell
Ubuntu 16.04
```

### python依赖

```python
 Name	    Version
python	 	3.5.2
flask    	1.1.2
requests    2.9.1
```

### Mysql数据库

```shell
mysql 5.7.33
```

## FLaskProject 运行步骤

#### mysql数据库信息

```shell
# 安装mysql
sudo apt-get install mysql-server mysql-client
# 创建数据库,导入FlaskProject/sql/info_db.sql
# 登录数据库
mysql -u root -p
# 创建数据库
create database info;
# 导入数据文件
mysql -u root -p info < FlaskProject/sql/info_db.sql
```

#### python代码

```shell
# 安装Flask
pip3 install flask==1.1.2
# 修改tools.py文件中的mysql连接信息,修改为自己本地的数据库信息
# 运行程序
python FlaskProject/views.py
# 打开浏览器输入127.0.0.1:500
```

