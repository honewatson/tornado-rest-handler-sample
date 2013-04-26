#!/usr/bin/env python
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
from bson import json_util
from bson.objectid import ObjectId
from tornado.options import define, options
from tornado_rest_handler import TornadoRestHandler, routes, rest_routes
from python_rest_handler import ObjectDict
from python_rest_handler.data_managers import MongoEngineDataManager
from mongoengine import *

define("port", default=8888, help="run on the given port", type=int)
connect('animal')

class ExtraHandler(TornadoRestHandler):

    def render(self, template_name, **kwargs):

        if 'objs' in kwargs.keys():
            data = [{ k:getattr(item, k) for k in item._fields.keys() } for item in kwargs['objs']]
        else:
            data = { k:getattr(kwargs['obj'], k) for k in kwargs['obj']._fields.keys() }

        self.write(json.dumps(data, sort_keys=True, indent=4, default=json_util.default))


class AnimalHandler(ExtraHandler):
    pass


class NMongoEngineDataManager(MongoEngineDataManager):
    def find_instance_by_id(self, instance_id):
        try:
            return self.model.objects.get(pk=instance_id)
        except:
            return {}
    def delete_instance(self, instance):
        try:
            instance.delete()
        except:
            return False

class Animal(DynamicDocument):
    name = StringField(max_length=200, required=True)
    description = StringField(max_length=200, required=False)



TORNADO_ROUTES = [
    # another handlers here

    rest_routes(Animal, data_manager=NMongoEngineDataManager, handler=AnimalHandler, prefix='animal', redirect_pos_action='/animal'),

    # another handlers here
]

TORNADO_SETTINGS = {}

#application = tornado.web.Application(routes(TORNADO_ROUTES), **TORNADO_SETTINGS)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(routes(TORNADO_ROUTES), debug=True)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

#curl --data "name=sun&description=peg" http://192.168.56.101:8888/animal
#curl http://192.168.56.101:8888/animal
#curl -X DELETE http://192.168.56.101:8888/animal/517a868d1d41c80a8a000001
#curl --data "name=doggywoggy" http://192.168.56.101:8888/animal/517a8ff41d41c80b83000000