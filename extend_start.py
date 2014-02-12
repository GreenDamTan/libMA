#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: cyxsheep

import extend_func
import os
import ma
import time
import pickle
import random
import config

if __name__ == '__main__':
    import sys
    bot = extend_func.Bot()
    while True:
        try:
            bot.run()
            reload(extend_func)
        except ma.HeaderError, e:
            print e.code, e.message, 'sleep for 20s'
            import traceback; traceback.print_exc()
            time.sleep(20)
            continue
        except Exception, e:
            print e, 'sleep for 1min'
            import traceback; traceback.print_exc()
            time.sleep(60)
            continue
