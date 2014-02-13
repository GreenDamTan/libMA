#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:cyxsheep
# __doc__:extend function for libMA

#Database
HOST = ''
USER = ''
PASSWD = ''
DB = ''

#Strategy
DA_MO_SHEN = True
STRATEGY = 'collect' #kill or collect
LAST_HIT_BC = 30
COLLECTION_PER_BC = 6

#Area
SHOW_AREA = False

#Ranking
SHOW_RANKING = False

#Get reward
AUTO_GET_REWARD = False

#Sell card
SELL_CARD_SWITCH = False

#special card with TTL(time to live)
SPECIAL_CARD = {
        "华恋型亚瑟 -魔法之派-" : [3,2,1,28],
        "纯白型小灰人" : [3,2,15,28],
        "纯白型尤文之狮" : [2,2,1,28],
        "纯白型红玉之髓" : [2,2,1,14],
        "华恋型玛洛斯" : [2,2,1,14],
        "姬忧型茶茶" : [2,2,1,14],
        }

#Auto combination card
AC_SWITCH = True
AC_CARD= ('华恋型玛洛斯',)
AC_BLACK_LIST = ('切尔莉','超级切尔莉','支援型律涅特','第二型毕斯克拉乌莉特')
AC_CARDS_PER_TIME = 10
AC_RARITY = 3

#PVP switch
PVP_SWITCH = False
