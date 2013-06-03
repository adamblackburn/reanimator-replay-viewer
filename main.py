import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from django.utils import simplejson as json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class Replay(ndb.Model):
    replay_data = ndb.StringProperty(indexed=False)
    metadata = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class GetReplay(webapp2.RequestHandler):
    def get(self, key):
        r = Replay.get_by_id(int(key))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(r.replay_data)

class MainPage(webapp2.RequestHandler):
    def get(self, key=None):
        if not key:
            # self.response.headers['Content-Type'] = 'text/plain'
            q = Replay.query().order(-Replay.created)
            self.response.write('available replays:')
            for x in q:
                self.response.write('''<div><a href="/replay/do/%s">%s</a></div>''' %
                    (x.key.id(), x.created))
        else:
            # self.response.headers['Content-Type'] = 'text/plain'
            r = Replay.get_by_id(int(key))

            template_values = { 'metadata' : json.loads(r.metadata),
                                'replay_key' : key };

            template = JINJA_ENVIRONMENT.get_template('replay.html')
            self.response.write(template.render(template_values))

    def head(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'

    def post(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        r = Replay(replay_data=self.request.get("replay_log"),
            metadata=self.request.get('metadata'))
        r.put()

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/replay/upload', MainPage),
    ('/replay/do/(\d+)', MainPage),
    ('/replay/get/(\d+)', GetReplay),
], debug=True)
