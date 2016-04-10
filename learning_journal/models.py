# coding=utf-8
from __future__ import unicode_literals

import datetime

from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    DateTime,
    ForeignKey,
    Table

)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from passlib.apps import custom_app_context as blogger_pwd_context
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


association_table = Table(
    'association_table', Base.metadata,
    Column('posts_id', Integer, ForeignKey('posts.id')),
    Column('category_id', Integer, ForeignKey('category.id'))
)


class Post(Base):
    """Class for modeling a single blog post."""

    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(length=128), unique=True)
    text = Column(Unicode)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    categories = relationship('Category', secondary=association_table,
                              back_populates="posts")

    def __json__(self, request):
        """Create JSON of Post instance."""
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'created': self.created.isoformat(),
            'categories': self.categories.name
        }

    def to_json(self, request=None):
        """Return JSON of post instance."""
        return self.__json__(request)

    @classmethod
    def all(cls):
        """Class method to return all posts."""
        return DBSession.query(cls).order_by(cls.created.desc()).all()

    @classmethod
    def by_id(cls, post_id=None):
        """Class method to get one post by id."""
        return DBSession.query(cls).get(post_id)

    @classmethod
    def modify(cls, form, id):
        """Update an existing post."""
        instance = cls.by_id(id)
        instance.title = form['title'].data
        instance.text = form['text'].data
        # instance.categories = form['categories'] # query cats + append/create and append
        # instance.created = instance.created
        DBSession.add(instance)
        return instance

    @classmethod
    def get_choices(self):
        cats = DBSession.query(Category).order_by(Category.name).all()
        return [(cat.id, cat.name) for cat in cats]


class User(Base):
    """Create user class so individuals can register and login."""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255), unique=True, nullable=False)
    password = Column(Unicode(255), nullable=False)
    last_logged = Column(DateTime, default=datetime.datetime.utcnow)

    def verify_password(self, password):
        """Check for cleartext password, verify that provided pw is valid."""
        if password == self.password:
            self.set_password(password)

        return blogger_pwd_context.verify(password, self.password)

    def set_password(self, password):
        """Hash provided password to compare to user provided value later."""
        self.password = blogger_pwd_context.encrypt(password)

    def __json__(self, request):
        """Create JSON of user instance."""
        return {
            'id': self.id,
            'username': self.username,
        }

    def to_json(self, request=None):
        """Return JSON of user instance."""
        return self.__json__(request)


class Comment(Base):
    """Create a comment class connect to User and Post."""

    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    thoughts = Column(Unicode)
    written = Column(DateTime, default=datetime.datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    author = relationship("User", backref='my_comments')
    parent = relationship("Post", backref="comments")

    def __json__(self, request):
        """Return JSON of comment instance."""
        return {
            'id': self.id,
            'thoughts': self.thoughts,
            'author': self.author,
            'written': self.written.isoformat()
        }

    def to_json(self, request=None):
        """Get JSON of comment instance."""
        return self.__json__(request)


class Category(Base):
    """Class for category for post or comment."""

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    posts = relationship(
        "Post",
        secondary=association_table,
        back_populates="categories")

    def __init__(self, name):
        """Initialize with name of category."""
        self.name = name

    def __json__(self, request):
        """Create JSON of category instance."""
        return {
            'id': self.id,
            'name': self.name,
            'posts': self.posts,
        }

    def to_json(self, request=None):
        """Return JSON of category."""
        return self.__json__(request)


