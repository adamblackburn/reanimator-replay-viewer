import webapp2
import jinja2
import os
import string
import random

from google.appengine.ext import ndb
from django.utils import simplejson as json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

def id_generator(size=6, chars=string.ascii_letters + string.digits):
   return ''.join(random.choice(chars) for x in range(size))

class Replay(ndb.Model):
    replay_data = ndb.StringProperty(indexed=False)
    metadata = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    app_id = ndb.StringProperty(indexed=True)

class GetReplay(webapp2.RequestHandler):
    def get(self, key):
        r = Replay.get_by_id(key)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(r.replay_data)

class AppLister(webapp2.RequestHandler):
    def get(self, app_id):
        # self.response.headers['Content-Type'] = 'text/plain'
        q = Replay.query(Replay._properties['app_id'] == app_id).order(-Replay.created)
        self.response.write('available replays:')
        for x in q:
            self.response.write('''<div><a href="/replay/do/%s">%s</a></div>''' %
                (x.key.id(), x.created))

class EntryPage(webapp2.RequestHandler):
    def get(self):
        # self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Please enter the URL of the app you want to view replays for. ')
        self.response.write('Something like /app/ABCDEFG')

class DataGetter(webapp2.RequestHandler):
    def get(self, key):
        # self.response.headers['Content-Type'] = 'text/plain'
        r = Replay.get_by_id(key)

        template_values = { 'metadata' : json.loads(r.metadata),
                            'replay_key' : key }

        template = JINJA_ENVIRONMENT.get_template('replay.html')
        self.response.write(template.render(template_values))

class MainPage(webapp2.RequestHandler):
    def head(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'

    def post(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        r = Replay(app_id=self.request.get('app_id'),
            replay_data=self.request.get("replay_log"),
            metadata=self.request.get('metadata'),
            id=id_generator()
            )
        r.put()

application = webapp2.WSGIApplication([
    ('/', EntryPage),
    ('/app/([A-Za-z0-9]{7})', AppLister),
    ('/replay/upload', MainPage),
    ('/replay/do/([A-Za-z0-9]{6})', DataGetter),
    ('/replay/get/([A-Za-z0-9]{6})', GetReplay),
], debug=True)
