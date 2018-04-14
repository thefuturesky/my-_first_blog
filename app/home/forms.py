from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired,Length


class CommentForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！"),
            Length(max=10,message="已超过昵称最大字数限制")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder":"请输入昵称"
        }
    )
    content = TextAreaField(
        label="评论",
        validators=[
            DataRequired("请输入评论！"),
            Length(max=50, message="已超过昵称最大字数限制")
        ],
        description="评论",
        render_kw={
            "class": "form-control",
            "style":"width:670px",
            "placeholder": "请输入评论",
            "rows":5
        }
    )
    submit = SubmitField(
        label="发布评论",
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )