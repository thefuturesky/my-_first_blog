from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Article
from app import db
from app import create_app

app = create_app()
app.app_context().push()
tags = db.session.query(Tag).all()
articles = db.session.query(Article).all()

#   管理员登陆表单
class LoginForm(FlaskForm):
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！"
        }

    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码"
        }
    )
    submit = SubmitField(
        label="登陆",
        render_kw={
            "class": "btn btn-primary btn-block"
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = db.session.query(Admin).filter_by(username=account).count()
        if admin == 0:
            raise ValidationError("账号不存在！")


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码!")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码",
            # "required": "required"
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码!")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码",
            # "required": "required"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_old_pwd(self, field):
        from flask import session
        pwd = field.data
        name = session['admin']
        admin = Admin.query.filter_by(username=name).first()
        if not admin.check_pwd(pwd):
            raise ValidationError("旧密码不正确！")


class TagForm(FlaskForm):
    name = StringField(
        label="标签",
        validators=[
            DataRequired("请输入标签！")
        ],
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class ArticleForm(FlaskForm):
    title = StringField(
        label="文章名",
        validators=[
            DataRequired("请输入文章名！")
        ],
        description='文章名',
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入文章名！"
        }
    )
    content = TextAreaField(
        label="文章类容",
        validators=[
            DataRequired('请输入文章类容！')
        ],
        description='文章类容',
        render_kw={
            "class": "form-control",
            "rows": 50
        }
    )
    tag_id = SelectField(
        label='标签',
        validators=[
            DataRequired('请选择标签！')
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        description='标签',
        render_kw={
            "class": "form-control",
        }
    )
    recommend = SelectField(
        label='推荐',
        validators=[
            DataRequired('请选择是否推荐！')
        ],
        coerce=int,
        choices=[(2, "不推荐"), (1, "推荐")],
        description='推荐',
        render_kw={
            "class": "form-control",
        }
    )
    author = StringField(
        label="作者",
        validators=[
            DataRequired("请输入作者！")
        ],
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入作者名字！"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PhotoForm(FlaskForm):
    title = StringField(
        label="照片标题",
        validators=[
            DataRequired("请输入照片标题！")
        ],
        description='照片标题',
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入照片标题！"
        }
    )
    logo = StringField(
        label='照片地址',
        validators=[
            DataRequired('请上传照片地址!')
        ],
        description='照片地址',
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入照片地址！"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class AdminForm(FlaskForm):
    username = StringField(
        label='管理员名称',
        validators=[
            DataRequired("请输入管理员名称！")
        ],
        description="管理员名称",
        render_kw={
            'class': "form-control", \
            'placeholder': "请输入管理员名称！",
            # "required": "required"
        }
    )
    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("请输入管理员密码!")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码",
        }
    )
    repwd = PasswordField(
        label="管理员重复密码",
        validators=[
            DataRequired("请输入管理员重复密码!"),
            EqualTo("pwd",message="两次密码不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员重复密码",
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class AbstractForm(FlaskForm):
    title = StringField(
        label="文章名",
        validators=[
            DataRequired("请输入文章名！")
        ],
        description='文章名',
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入文章名！"
        }
    )
    content = TextAreaField(
        label="摘要内容",
        validators=[
            DataRequired('请输入摘要内容！')
        ],
        description='摘要内容',
        render_kw={
            "class": "form-control",
            "rows": 20
        }
    )
    article_id = SelectField(
        label = "所属文章",
        validators = [
            DataRequired("请选择所属文章！")
        ],
        coerce = int,
        choices = [(v.id,v.title) for v in articles],
        description='所属文章',
        render_kw={
            "class": "form-control",
        }
    )
    logo = StringField(
        label="文章封面",
        validators=[
            DataRequired("请输入文章封面！")
        ],
        description='文章封面',
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入文章封面！"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )

class IdeaForm(FlaskForm):
    content = TextAreaField(
        label="说说内容",
        validators=[
            DataRequired('请输入说说内容！')
        ],
        description='说说内容',
        render_kw={
            "class": "form-control",
            "rows": 5
        }
    )
    logo = StringField(
        label="说说图片",
        description='说说图片',
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入说说图片地址！"
        }
    )
    submit = SubmitField(
        label="编辑",
        render_kw={
            "class": "btn btn-primary"
        }
    )