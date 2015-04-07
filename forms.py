# -*- coding: utf-8 -*-
from wtforms.fields import IntegerField, StringField, DateField
from wtforms.validators import Required
from wtforms_tornado import Form


class AddEventForm(Form):
    name = StringField('Name')
    rows = IntegerField('Number of rows')
    seats = IntegerField('Number of seat in row')
    capacity = IntegerField('Capacity')