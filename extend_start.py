#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-08-08 00:15:50
import extend_func
import os
import ma
import time
import pickle
import random
import config

if __name__ == '__main__':
    import sys
    fs = set()
    while True:
        reload(extend_func)
        bot = extend_func.Bot()
        try:
            bot.run(fs)
            reload(extend_func)
        except ma.HeaderError, e:
            print e.code, e.message, 'sleep for 10s'
            import traceback; traceback.print_exc()
            time.sleep(10)
            continue
        except Exception, e:
            print e, 'sleep for 20s'
            import traceback; traceback.print_exc()
            time.sleep(20)
            continue
