# -*- coding: utf-8 -*-
import json
from utils import CustomEncoder
json._default_encoder = CustomEncoder()

from tornado import gen
from tornado.httpserver import HTTPServer
import tornado.ioloop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler, asynchronous, url
from tornado.websocket import WebSocketHandler

from asyncmongo import Client
from bson.objectid import ObjectId

from config import MONGODB_SETTINGS, TORNADO_SETTINGS
from forms import AddEventForm


define("port", default=5000, type=int)


class Index(RequestHandler):

    @asynchronous
    def get(self):
        self.application.db.events.find(callback=self.callback)

    def callback(self, events, **kwargs):
        self.render('index.html', events=events)


class AddEvent(RequestHandler):
    form = AddEventForm()

    @asynchronous
    def get(self):
        self.render('add_event.html', form=self.form, success=None)

    @asynchronous
    def post(self):
        self.form = AddEventForm(self.request.arguments)
        if self.form.validate():
            self.application.db.events.insert(self.form.data, callback=self.callback)
        self.render('add_event.html', form=self.form, success=False)

    def callback(self, events, **kwargs):
        self.render('add_event.html', form=self.form, events=events, success=True)


class ShowEvent(RequestHandler):

    @asynchronous
    def get(self, event_id):
        self.application.db.events.find_one({'_id': ObjectId(event_id)},
                                            callback=self.callback)

    def callback(self, event, **kwargs):
        self.render('book_seat.html', event=event)


class BookSeat(WebSocketHandler):
    callbacks = []

    def find_event(self, event_id, callback):
        return self.application.db.events.find_one({'_id': ObjectId(event_id)}, callback=callback)

    def find_seats(self, event_id, callback):
        return self.application.db.seats.find({'event_id': ObjectId(event_id)}, callback=callback)

    def add_booking(self, event_id, row_id, seat_id, callback):
        return self.application.db.seats.insert({'event_id': ObjectId(event_id), 'row_id': row_id,
                                                 'seat_id': seat_id}, callback=callback)

    @gen.engine
    def get_available_seats(self, event_id):
        events, error = yield gen.Task(self.find_event, event_id=event_id)
        event = events[0]
        event['_id'] = str(event['_id'])
        booked_seats, error = yield gen.Task(self.find_seats, event_id=event_id)
        self.write_message({'event': event, 'booked_seats': booked_seats[0]})

    @asynchronous
    def open(self, event_id, **kwargs):
        self.get_available_seats(event_id)

    @asynchronous
    @gen.engine
    def on_message(self, message):
        data = json.loads(message)
        yield gen.Task(self.add_booking, data['event_id'], data['row_id'], data['seat_id'])
        self.get_available_seats(data['event_id'])


class CustomApplication(Application):
    def __init__(self):
        kwargs = {
            'handlers': [
                url('/', Index, name='index'),
                url('/events/add/', AddEvent, name='add-event'),
                url('/events/([a-z0-9]+)/', ShowEvent, name='show-event'),
                url('/events/([a-z0-9]+)/book/', BookSeat, name='book-seat')
            ]
        }
        kwargs.update(**TORNADO_SETTINGS)
        super(CustomApplication, self).__init__(**kwargs)
        self.db = Client(**MONGODB_SETTINGS)


if __name__ == '__main__':
    parse_command_line()
    app = CustomApplication()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
