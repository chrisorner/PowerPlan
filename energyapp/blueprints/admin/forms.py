from collections import OrderedDict

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_alchemy import Unique

from lib.util_wtforms import ModelForm, choices_from_dict
from energyapp.blueprints.user.models import db, User


class SearchForm(FlaskForm):
    q = StringField('Search terms', [Optional(), Length(1, 256)])


class BulkDeleteForm(FlaskForm):
    SCOPE = OrderedDict([
        ('all_selected_items', 'All selected items'),
        ('all_search_results', 'All search results')
    ])

    scope = SelectField('Privileges', [DataRequired()],
                        choices=choices_from_dict(SCOPE, prepend_blank=False))
    

class UserForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        Optional(),
        Length(1, 16),
        # Part of the Python 3.7.x update included updating flake8 which means
        # we need to explicitly define our regex pattern with r'xxx'.
        Regexp(r'^\w+$', message=username_message)
    ])

    role = SelectField('Privileges', [DataRequired()],
                       choices=choices_from_dict(User.ROLE,
                                                 prepend_blank=False))
    active = BooleanField('Yes, allow this user to sign in')