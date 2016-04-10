# coding=utf-8
from __future__ import unicode_literals

from wtforms import (Form, StringField, validators,
                     TextAreaField, PasswordField, HiddenField,
                     SelectMultipleField)


strip_filter = lambda x: x.strip() if x else None


class ModifyPostForm(Form):
    """Create class for form to edit/create a post"""

    id = HiddenField()
    title = StringField('title', [validators.Length(min=4, max=128)])
    text = TextAreaField('text', [validators.Length(min=6)])
    categories = StringField('categories', [validators.Length(max=128)])

    existing_categories = SelectMultipleField('Category', coerce=int)


class UserForm(Form):
    """Create class for a form to create a user and login."""

    username = StringField('username', [validators.Length(min=2, max=128)])
    password = PasswordField('password', [validators.Length(min=5, max=128)], filters=[strip_filter])


class CommentForm(Form):
    """Create a text field form for adding comments to posts"""

    thoughts = TextAreaField('thoughts', [validators.Length(min=1)])
    HiddenField()

