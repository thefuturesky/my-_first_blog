from . import home
from flask import render_template, request, url_for, redirect, flash
from app.models import Article, Tag,Comment, Idea, Message
from app.home.forms import CommentForm
from app import db


@home.route('/<int:page>/')
def index(page=None):
    tags = db.session.query(Tag).all()
    page_data = db.session.query(Article)

    # 标签
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))


    # 播放量
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(Article.click_count.desc())
        else:
            page_data = page_data.order_by(Article.click_count.asc())

    # 评论数量
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(Article.commentnum.desc())
        else:
            page_data = page_data.order_by(Article.commentnum.asc())


    if page == None:
        page=1
    page_data = page_data.paginate(page=page, per_page=5)
    p = dict(
        tid=tid,
        pm=pm,
        cm=cm
    )
    return render_template('home/index.html', page_data=page_data,p=p,tags=tags)


@home.route('/about/')
def about():
    return render_template('home/about.html')


@home.route('/idea/<int:page>/')
def idea(page=None):
    if page == None:
        page=1
    page_data = db.session.query(Idea).paginate(page=page,per_page=10)
    return render_template('home/idea.html',page_data=page_data)


@home.route('/message/',methods=['GET','POST'])
def message():
    form=CommentForm()
    messages = db.session.query(Message).all()
    if form.validate_on_submit():
        data = form.data
        message=Message(
            name=data['name'],
            content=data['content']
        )
        db.session.add(message)
        db.session.commit()
        flash("留言成功！","ok")
        return redirect(url_for("home.message"))
    return render_template('home/message.html',form=form,messages=messages)


@home.route('/article/<int:id>/<int:page>/',methods=['GET','POST'])
def article(id=None, page=None):
    article = db.session.query(Article).join(Tag).filter(Article.id == int(id), Tag.id == Article.tag_id).first_or_404()
    article.click_count = article.click_count+1
    form = CommentForm()
    if page is None:
        page = 1
    page_data = db.session.query(Comment).join(Article).filter(Article.id == article.id).order_by(
        Comment.addtime.desc()).paginate(page=page, per_page=10)
    db.session.add(article)
    db.session.commit()
    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            article_id=article.id,
            name=data['name']
        )
        db.session.add(comment)
        db.session.commit()
        article.commentnum = article.commentnum + 1
        flash("发布评论成功！", 'ok')
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('home.article', id=article.id, page=1))
    return render_template('home/article.html',form=form,page_data=page_data,article=article)
