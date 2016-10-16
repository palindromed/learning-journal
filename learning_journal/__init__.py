# coding=utf-8
from __future__ import unicode_literals

import os
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .models import (
    DBSession,
    Base,
    )
from pyramid.session import SignedCookieSessionFactory
from .security import DefaultRoot


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Use ENV variable to access db

    if 'DATABASE_URL' in os.environ:
        settings['sqlalchemy.url'] = os.environ['DATABASE_URL']

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    auth_secret = os.environ.get('JOURNAL_SECRET', 'itsaseekrit')
    authentication_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha256',
    )

    authorization_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        authentication_policy=authentication_policy,
        authorization_policy=authorization_policy,
        root_factory=DefaultRoot,
    )

    session_secret = os.environ.get('JOURNAL_SECRET', 'itsaseekrit')
    session_factory = SignedCookieSessionFactory(session_secret, secure=True)
    config.set_session_factory(session_factory)

    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    # routes
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    # config.add_route('post_json', '/post_json')
    config.add_route('register', '/register')
    config.add_route('add_json', '/add_json')
    config.add_route('home', '/')
    config.add_route('detail', '/post/{post_id:\d+}')
    config.add_route('add_entry', '/create')
    config.add_route('add_entry_json', 'add_entry.json')
    config.add_route('edit', '/edit/{post_id:\d+}')

    config.scan()

    return config.make_wsgi_app()
