from app import db
from datetime import datetime


# 后台管理员
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)  # id
    username = db.Column(db.String(250), nullable=False, unique=True)  # 账号
    password = db.Column(db.String(250), nullable=False)  # 密码
    is_super = db.Column(db.SmallInteger)  # 是否为超级管理员 , 1为超级管理员
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
    adminlogs = db.relationship("Adminlogin", backref=db.backref("admin"))  # 管理员登陆日志
    oplogs = db.relationship("Oplog", backref=db.backref("admin"))  # 管理员操作日志
    articles = db.relationship("Article", backref=db.backref("admin"))  # 管理员发布文章
    ideas = db.relationship("Idea", backref=db.backref("admin"))  # 管理员发布说说

    def __repr__(self):
        return "<admin %r>" % self.username

    def checkpwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, pwd)


#  管理员操作日志
class Oplog(db.Model):
    __tablename__ = "oplog"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))  # 所属管理员外键关联
    addtime = db.Column(db.DateTime, default=datetime.now)  # 操作时间
    ip = db.Column(db.String(100))  # 操作IP
    reason = db.Column(db.String(600))  # 操作类容

    def __repr__(self):
        return "<Oplog> %r" % self.id


#   管理员登陆日志
class Adminlogin(db.Model):
    __tablename__ = "adminlogin"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))  # 所属管理员外键关联
    addtime = db.Column(db.DateTime, default=datetime.now)  # 登陆时间
    ip = db.Column(db.String(100))  # 操作IP

    def __repr__(self):
        return "<Adminlogin: %r>" % self.id


#   博客文章
class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)  # 文章编号
    title = db.Column(db.String(100), nullable=False)  # 文章标题
    content = db.Column(db.Text, nullable=False)  # 文章类容
    recommend = db.Column(db.SmallInteger)  # 是否推荐该篇文章 1为推荐
    click_count = db.Column(db.BigInteger)  # 文章点击数
    commentnum = db.Column(db.BigInteger)  # 文章评论数
    author = db.Column(db.String(100))  # 文章作者
    addtime = db.Column(db.DateTime, default=datetime.now)  # 文章发布时间
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))  # 所属标签外键关联
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 发布管理员外键关联
    comments = db.relationship("Comment", backref=db.backref("article"))  # 文章评论
    abstract = db.relationship("Abstract", backref=db.backref("article"))   #摘要外键关联

    def __repr__(self):
        return "<Article:%r>" % self.title


# 标签
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 标签名字
    addtime = db.Column(db.DateTime, default=datetime.now, index=True)  # 标签创建时间
    articles = db.relationship('Article', backref=db.backref('tag'))  # 文章外键关联

    def __repr__(self):
        return "<Tag %r>" % self.name


# 文章摘要
class Abstract(db.Model):
    __tablename__ = "abstract"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 文章编号
    title = db.Column(db.String(255), unique=True)  # 文章名称
    content = db.Column(db.Text)  # 文章摘要类容
    logo = db.Column(db.String(100))  # 封面
    article_id = db.Column(db.Integer,db.ForeignKey("article.id"))  #所属文章ID

    def __repr__(self):
        return "<Abstract %r>" % self.title


# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    name = db.Column(db.String(100))  # 游客昵称
    content = db.Column(db.Text)  # 内容
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 评论添加时间
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"))  # 所属文章外键关联

    def __repr__(self):
        return "<Comment %r>" % self.id


# 留言评论
class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    name = db.Column(db.String(100))  # 游客昵称
    content = db.Column(db.Text)  # 内容
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 评论添加时间

    def __repr__(self):
        return "<Message %r>" % self.id


#   感悟人生
class Idea(db.Model):
    __tablename__ = 'idea'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)  # 编号
    content = db.Column(db.Text, nullable=False)  # 想法类容
    addtime = db.Column(db.DateTime, default=datetime.now)  # 想法发布时间
    logo = db.Column(db.String(100))  # 图片
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 发布管理员外键关联

    def __repr__(self):
        return "<Article:%r>" % self.title


# 我的相册
class Photo(db.Model):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 相册编号
    title = db.Column(db.String(255), unique=True)  # 相册名称
    logo = db.Column(db.String(255), unique=True)  # 相册
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 相册添加时间

    def __repr__(self):
        return "<Preview %r>" % self.title
