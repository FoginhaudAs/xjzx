import pymysql
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db



# 实现python2和python3 数据库之间相互转换使用

pymysql.install_as_MySQLdb()

# 创建app对象
app = create_app('development')

# 创建管理对象
manager = Manager(app)

# 创建数据库迁移对象
Migrate(app, db)

# 添加数据库迁移命令
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()