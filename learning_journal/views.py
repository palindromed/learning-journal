# coding=utf-8
from __future__ import unicode_literals

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy import desc
from .models import (
    DBSession,
    Post,
    User,
    Comment,
    Category
)
from pyramid.security import remember, forget
from .user import UserService
from .post_form import ModifyPostForm, UserForm, CommentForm


# @view_config(route_name='post_json', renderer='json', xhr=True)
# def edit_ajax_post(request):
#     form = EditForm(request.POST)
#     if request.method == 'POST' and form.validate():
#         try:
#             post = request.POST['postid']
#             post = DBSession.query(Post).filter(Post.id == post).first()
#             post.title = request.POST['title']
#             post.text = request.POST['text']
#             DBSession.add(post)
#             DBSession.flush()
#         except DBAPIError:
#             form.errors.setdefault('error', []).append('Title must be unique!')
#     return {'form': form, 'use_case': 'Edit'}


@view_config(route_name='add_json', renderer='json', xhr=True)
def add_ajax_comment(request):
    form = CommentForm(request.POST)
    if request.method == 'POST' and form.validate():
        try:
            user = DBSession.query(User).filter(User.username == request.authenticated_userid).first()
            path = request.POST['path'].split('/')
            post = path[-1]
            post = DBSession.query(Post).filter(Post.id == post).first()
            comment = Comment()
            comment.thoughts = request.POST['thoughts']
            comment.author = user
            comment.parent = post
            post.comments.append(comment)
            user.my_comments.append(comment)
            DBSession.add_all([comment, user, post])
            DBSession.flush()
            return {'new_comment': comment}
        except DBAPIError:
            return {'form': form, 'error': 'FAIL'}

    return {'form': form}


@view_config(route_name='home', renderer='templates/list.jinja2',
             permission='read')
def list_view(request):
    posts = Post.all()
    return {'posts': posts}


@view_config(route_name='detail', renderer='templates/detail.jinja2',
             permission='read')
def detail_view(request):
    form = CommentForm(request.POST)
    post = Post.by_id(request.matchdict['post_id'])
    return {'post': post, 'form': form}


# @view_config(route_name='edit', renderer='json')
@view_config(route_name='edit', request_method='POST', permission='create')
@view_config(route_name='edit', renderer='templates/edit.jinja2', permission='change')
def edit_view(request):
    edit_id = int(request.matchdict['post_id'])
    post_to_edit = Post.by_id(edit_id)
    form = ModifyPostForm(request.POST, post_to_edit)

    form.existing_categories.choices = Post.get_choices()

    detail_url = request.route_url('detail', post_id=edit_id)

    if request.method == 'POST' and form.validate():
        Post.modify(form, edit_id)
        return HTTPFound(location=detail_url)

    return {'form': form, 'use_case': 'Edit'}



@view_config(route_name='add_entry', request_method='POST', check_csrf=True)
@view_config(route_name='add_entry', renderer="templates/edit.jinja2",
             permission='change')
def create_view(request):
    form = ModifyPostForm(request.POST)
    if request.method == 'POST' and form.validate():
        categories = Category(name=form.categories.data)
        new_post = Post(title=form.title.data, text=form.text.data)
        new_post.categories.append(categories)
        categories.posts.append(new_post)
        try:
            DBSession.add(new_post)
            new_post.categories.append(categories)
            DBSession.flush()
            detail_id = new_post.id
            re_route = request.route_url('detail', post_id=detail_id)
            return HTTPFound(location=re_route)
        except IntegrityError:
            form.errors.setdefault('error', []).append('Title must be unique!')
    return {'form': form, 'use_case': 'Create'}


@view_config(route_name='login', request_method='POST', check_csrf=True)
@view_config(route_name='login', renderer='templates/login.jinja2')
def login_view(request):
    form = UserForm(request.POST)
    if request.method == 'POST' and form.validate():
        if form.username.data:
            user = UserService.by_name(form.username.data)
            if user and user.verify_password(form.password.data):
                headers = remember(request, form.username.data)
                return HTTPFound(location=request.route_url('home'), headers=headers)
            else:
                headers = forget(request)
                return {'form': form, 'error': "Unable to validate login. Try again."}
    return {'form': form}


@view_config(route_name='logout')
def log_out(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=headers)


@view_config(route_name='register', request_method='POST', check_csrf=True)
@view_config(route_name='register', renderer='templates/register.jinja2')
def register(request):
    form = UserForm(request.POST)
    if request.method == 'POST' and form.validate():
        new_user = User()
        new_user.username = form.username.data
        new_user.set_password(form.password.data.encode('utf8'))
        DBSession.add(new_user)
        headers = remember(request, form.username.data)
        return HTTPFound(location=request.route_url('home'), headers=headers)

    return {'form': form}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning-journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
