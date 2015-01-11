#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from gevent.monkey import patch_all
patch_all()

import redis
from gevent.wsgi import WSGIServer
from flask import Flask, g
from . import settings
from .channel_manager import ChannelManager
from .irc_robot import dmrobot

bot_list = {}
app = Flask(__name__)
app.config.from_object(settings)
r = redis.StrictRedis(host='localhost', port=6379, db=1)
chan_mgr = ChannelManager(app, r)
with app.app_context():
    chan_mgr.new_channel("demo", desc=u"演示频道, 发布、订阅均无需密码")
    bot_list["demo"] = dmrobot()
    bot_list["demo"].HOST = "card.freenode.net"
    bot_list["demo"].PORT = 6666
    bot_list["demo"].channel = "#tuna"
    bot_list["demo"].method = "CHANNEL"
    bot_list["demo"].dmch = chan_mgr.get_channel("demo")
    if bot_list["demo"].check():
        bot_list["demo"].start()
    

@app.before_request
def set_channel_manager():
    g.channel_manager = chan_mgr
    try:
        r.ping()
    except:
        r.connection_pool.reset()
    g.r = r


from . import views
from . import api
from . import wechat

def main():
    app.debug = True
    http_server = WSGIServer(('', 5000), app)
    print("Serving at 0.0.0.0:5000")
    http_server.serve_forever()


# vim: ts=4 sw=4 sts=4 expandtab
