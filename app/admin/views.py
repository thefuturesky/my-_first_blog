from . import admin
from flask import render_template, redirect, url_for, session, flash, request
from app.admin.forms import LoginForm, PwdForm, TagForm, ArticleForm, PhotoForm, AdminForm, AbstractForm, IdeaForm
from app.models import Admin, Adminlogin, Tag, Article, Photo, Comment, Message, Oplog, Abstract, Idea
from app import db
from functools import wraps
import datetime


# 登陆装饰器
def admin_login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('admin'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin.login', next=request.url))

    return decorated_function


# 操作日志数据添加
def operate_log(content):
    oplog = Oplog(
        admin_id=session.get('admin_id'),
        ip=request.remote_addr,
        reason=content
    )
    db.session.add(oplog)
    db.session.commit()


# 上下文应用处理器
@admin.context_processor
def tpl_extra():
    # data = dict(
    #     online_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # )
    return {'online_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    # return data


#   后台首页
@admin.route('/')
@admin_login_required
def index():
    return render_template("admin/index.html")


# 后台登陆
@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = db.session.query(Admin).filter_by(username=data['account']).first()
        if not admin.checkpwd(data['pwd']):
            flash("密码错误!", "err")
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        session['admin_id'] = admin.id
        session.permanet = True
        adminlog = Adminlogin(
            admin_id=admin.id,
            ip=request.remote_addr
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', form=form)


# 退出登陆
@admin.route('/logout/')
@admin_login_required
def logout():
    session.pop('admin', None)
    session.pop('admin_id', None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd/', methods=['GET', 'POST'])
@admin_login_required
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = db.session.query(Admin).filter_by(username=session.get('admin')).first_or_404()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data['new_pwd'])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功！请重新登陆！", 'ok')
        operate_log("修改密码")
        return redirect(url_for('admin.logout'))
    return render_template('admin/pwd.html', form=form)


# 添加标签
@admin.route('/tag/add/', methods=['GET', 'POST'])
@admin_login_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = db.session.query(Tag).filter_by(name=data['name']).count()
        if tag == 1:
            flash("标签已存在", "err")
            return redirect(url_for('admin.tag_add'))
        else:
            tag = Tag(
                name=data['name']
            )
            db.session.add(tag)
            db.session.commit()
            flash("添加标签成功！", "ok")
            operate_log("添加标签:%s" % data['name'])
            return redirect(url_for('admin.tag_add'))
    return render_template('admin/tag_add.html', form=form)


# 标签列表
@admin.route('/tag/list/<int:page>/', methods=['GET'])
@admin_login_required
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(Tag.addtime.desc()).paginate(page=page, per_page=15)
    return render_template('admin/tag_list.html', page_data=page_data)


# 删除标签
@admin.route('/tag/del/<int:id>/', methods=['GET'])
@admin_login_required
def tag_del(id=None):
    tag = db.session.query(Tag).filter_by(id=int(id)).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功！", "ok")
    operate_log("删除标签:%s" % tag.name)
    return redirect(url_for('admin.tag_list', page=1))


# 编辑标签
@admin.route('/tag/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def tag_edit(id=None):
    tag = db.session.query(Tag).filter_by(id=int(id)).first()
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()
        if tag_count:
            flash("标签已存在", "err")
            return redirect(url_for('admin.tag_edit', id=id))
        else:
            tag.name = data['name']
            db.session.add(tag)
            db.session.commit()
            flash("修改标签成功！", "ok")
            operate_log("修改标签:%s" % tag.name)
            return redirect(url_for('admin.tag_edit', id=id))
    return render_template('admin/tag_edit.html', form=form, tag=tag)


# 添加文章
@admin.route('/article/add/', methods=['GET', 'POST'])
@admin_login_required
def article_add():
    form = ArticleForm()
    if form.validate_on_submit():
        data = form.data
        article = Article(
            title=data['title'],
            content=data['content'],
            recommend=int(data['recommend']),
            click_count=0,
            commentnum=0,
            tag_id=int(data['tag_id']),
            author=data['author'],
            admin_id=1,
        )
        db.session.add(article)
        db.session.commit()
        flash("添加文章成功", "ok")
        operate_log("添加文章:%s" % data['title'])
        return redirect(url_for('admin.article_add'))
    return render_template('admin/article_add.html', form=form)


# 文章列表
@admin.route('/article/list/<int:page>/', methods=['GET'])
@admin_login_required
def article_list(page=None):
    if page is None:
        page = 1
    page_data = db.session.query(Article).order_by(Article.addtime.desc()).paginate(page=page, per_page=15)
    return render_template('admin/article_list.html', page_data=page_data)


# 删除文章
@admin.route('/article/del/<int:id>/', methods=['GET'])
@admin_login_required
def article_del(id=None):
    article = db.session.query(Article).filter_by(id=int(id)).first_or_404()
    db.session.delete(article)
    db.session.commit()
    flash("删除文章成功！", "ok")
    operate_log("删除文章:%s" % article.title)
    return redirect(url_for('admin.article_list', page=1))


# 编辑文章
@admin.route('/article/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def article_edit(id=None):
    article = db.session.query(Article).filter_by(id=int(id)).first()
    form = ArticleForm()
    if request.method == 'GET':
        form.content.data = article.content
        form.tag_id.data = article.tag_id
        form.recommend.data = article.recommend
        form.author.data = article.author
        form.title.data = article.title
    if form.validate_on_submit():
        data = form.data
        article_count = db.session.query(Article).filter_by(title=data['title']).count()
        if article_count:
            flash("文章名称已存在", "err")
            return redirect(url_for('admin.article_edit', id=id))
        else:
            article.title = data['title']
            article.content = data['content']
            article.author = data['author']
            article.recommend = int(data['recommend'])
            article.tag_id = int(data['tag_id'])
            db.session.add(article)
            db.session.commit()
            flash("修改文章成功！", "ok")
            operate_log("修改文章:%s" % data['title'])
            return redirect(url_for('admin.article_edit', id=id))
    return render_template('admin/article_edit.html', form=form, article=article)


# 添加摘要
@admin.route('/abstract/add/', methods=['GET', 'POST'])
@admin_login_required
def abstract_add():
    form = AbstractForm()
    if form.validate_on_submit():
        data = form.data
        abstract = Abstract(
            title=data['title'],
            content=data['content'],
            article_id=data['article_id'],
            logo = data['logo']
        )
        db.session.add(abstract)
        db.session.commit()
        flash("添加摘要成功", "ok")
        operate_log("添加摘要:%s" % data['title'])
        return redirect(url_for('admin.abstract_add'))
    return render_template('admin/abstract_add.html', form=form)


# 摘要列表
@admin.route('/abstract/list/<int:page>/', methods=['GET'])
@admin_login_required
def abstract_list(page=None):
    if page is None:
        page = 1
    page_data = db.session.query(Abstract).order_by(Abstract.id.desc()).paginate(page=page, per_page=15)
    return render_template('admin/abstract_list.html', page_data=page_data)


# 删除摘要
@admin.route('/abstract/del/<int:id>/', methods=['GET'])
@admin_login_required
def abstract_del(id=None):
    abstract = db.session.query(Abstract).filter_by(id=int(id)).first_or_404()
    db.session.delete(abstract)
    db.session.commit()
    flash("删除摘要成功！", "ok")
    operate_log("删除摘要:%s" % abstract.title)
    return redirect(url_for('admin.abstract_list', page=1))


# 编辑摘要
@admin.route('/abstract/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def abstract_edit(id=None):
    abstract = db.session.query(Abstract).filter_by(id=int(id)).first()
    form = AbstractForm()
    if request.method == 'GET':
        form.content.data = abstract.content
        form.title.data = abstract.title
    if form.validate_on_submit():
        data = form.data
        abstract_count = db.session.query(Abstract).filter_by(title=data['title']).count()
        if abstract_count:
            flash("摘要名称已存在", "err")
            return redirect(url_for('admin.abstract_edit', id=id))
        else:
            abstract.title = data['title']
            abstract.content = data['content']
            db.session.add(abstract)
            db.session.commit()
            flash("修改摘要成功！", "ok")
            operate_log("修改摘要:%s" % data['title'])
            return redirect(url_for('admin.abstract_edit', id=id))
    return render_template('admin/abstract_edit.html', form=form, abstract=abstract)

# 添加照片
@admin.route('/photo/add/', methods=['GET', 'POST'])
@admin_login_required
def photo_add():
    form = PhotoForm()
    if form.validate_on_submit():
        data = form.data
        photo = Photo(
            title=data['title'],
            logo=data['logo']
        )
        db.session.add(photo)
        db.session.commit()
        flash("上传照片成功！", "ok")
        operate_log("添加照片:%s" % data['title'])
    return render_template('admin/photo_add.html', form=form)


# 照片列表
@admin.route('/photo/list/<int:page>/')
@admin_login_required
def photo_list(page=None):
    if page is None:
        page = 1
    page_data = db.session.query(Photo).order_by(Photo.addtime.desc()).paginate(page=page, per_page=10)
    return render_template('admin/photo_list.html', page_data=page_data)


# 删除照片
@admin.route('/photo/del/<int:id>/', methods=['GET'])
@admin_login_required
def photo_del(id=None):
    photo = db.session.query(Photo).filter_by(id=int(id)).first_or_404()
    db.session.delete(photo)
    db.session.commit()
    flash("删除照片成功！", "ok")
    operate_log("删除照片:%s" % photo.title)
    return redirect(url_for('admin.photo_list', page=1))


# 修改照片
@admin.route('/photo/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_required
def photo_edit(id=None):
    photo = db.session.query(Photo).filter_by(id=id).first_or_404()
    form = PhotoForm()
    if form.validate_on_submit():
        data = form.data
        photo_count = Photo.query.filter_by(title=data['title']).count()
        if photo_count:
            flash("照片名称已经存在！", "err")
            return redirect(url_for('admin.photo_edit', id=int(id)))
        else:
            photo.title = data['title']
            db.session.add(photo)
            db.session.commit()
            flash("修改照片成功！", "ok")
            operate_log("修改照片:%s" % data['title'])
            return redirect(url_for('admin.photo_edit', id=id))
    return render_template('admin/photo_edit.html', form=form, photo=photo)


# 评论列表
@admin.route('/comment/list/<int:page>/', methods=['GET'])
@admin_login_required
def comment_list(page=None):
    if page == None:
        page = 1
    page_data = db.session.query(Comment).join(Article).filter(Article.id == Comment.article_id).order_by(
        Comment.addtime.desc()).paginate(page=page, per_page=15)
    return render_template('admin/comment_list.html', page_data=page_data)


# 删除评论
@admin.route('/comment/del/<int:id>/', methods=['GET'])
@admin_login_required
def comment_del(id=None):
    comment = db.session.query(Comment).get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", "ok")
    operate_log("删除评论:%s" % comment.content)
    return redirect(url_for('admin.comment_list', page=1))


# 留言板列表
@admin.route('/message/list/<int:page>/', methods=['GET'])
@admin_login_required
def message_list(page=None):
    if page == None:
        page = 1
    page_data = db.session.query(Message).order_by(
        Message.addtime.desc()).paginate(page=page, per_page=15)
    return render_template('admin/message_list.html', page_data=page_data)


# 删除留言
@admin.route('/message/del/<int:id>/', methods=['GET'])
@admin_login_required
def message_del(id=None):
    message = db.session.query(Message).get_or_404(int(id))
    db.session.delete(message)
    db.session.commit()
    flash("删除留言成功！", "ok")
    operate_log("删除留言:%s" % message.content)
    return redirect(url_for('admin.message_list', page=1))


# 管理员登陆日志列表
@admin.route('/adminloginlog/list/<int:page>/', methods=['GET'])
@admin_login_required
def adminloginlog_list(page=None):
    if page == None:
        page = 1
    page_data = db.session.query(Adminlogin).join(Admin, Admin.id == Adminlogin.admin_id).order_by(
        Adminlogin.addtime.desc()).paginate(page=page, per_page=15)
    return render_template('admin/adminloginlog_list.html', page_data=page_data)


# 操作日志列表
@admin.route('/oplog/list/<int:page>/', methods=['GET'])
@admin_login_required
def oplog_list(page=None):
    if page == None:
        page = 1
    page_data = db.session.query(Oplog).join(Admin, Admin.id == Oplog.admin_id).order_by(Oplog.addtime.desc()).paginate(
        page=page, per_page=15)
    return render_template('admin/oplog_list.html', page_data=page_data)


# 管理员列表
@admin.route('/admin/list/<int:page>/')
@admin_login_required
def admin_list(page=None):
    if page == None:
        page = 1
    page_data = db.session.query(Admin).order_by(Admin.addtime.desc()).paginate(
        page=page, per_page=15)
    return render_template('admin/admin_list.html', page_data=page_data)


# 添加管理员
@admin.route('/admin/add/', methods=['GET', 'POST'])
@admin_login_required
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        data = form.data
        from werkzeug.security import generate_password_hash
        admin = Admin(
            username=data['username'],
            pwd=generate_password_hash(data['pwd']),
            is_super=1
        )
        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功！", "ok")
        operate_log("添加管理员:%s" % data['name'])
    return render_template('admin/admin_add.html', form=form)


# 添加说说
@admin.route('/idea/add/', methods=['GET', 'POST'])
@admin_login_required
def idea_add():
    form = IdeaForm()
    if form.validate_on_submit():
        data = form.data
        idea = Idea(
            content=data['content'],
            logo = data['logo']
        )
        db.session.add(idea)
        db.session.commit()
        flash("添加说说成功", "ok")
        operate_log("添加说说:%s" % data['content'])
        return redirect(url_for('admin.idea_add'))
    return render_template('admin/idea_add.html', form=form)


# 说说列表
@admin.route('/idea/list/<int:page>/', methods=['GET'])
@admin_login_required
def idea_list(page=None):
    if page is None:
        page = 1
    page_data = db.session.query(Idea).order_by(Idea.id.desc()).paginate(page=page, per_page=15)
    return render_template('admin/idea_list.html', page_data=page_data)


# 删除说说
@admin.route('/idea/del/<int:id>/', methods=['GET'])
@admin_login_required
def idea_del(id=None):
    idea = db.session.query(Idea).filter_by(id=int(id)).first_or_404()
    db.session.delete(idea)
    db.session.commit()
    flash("删除说说成功！", "ok")
    operate_log("删除说说:%s" % idea.content)
    return redirect(url_for('admin.idea_list', page=1))
