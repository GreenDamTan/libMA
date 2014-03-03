#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:cyxsheep
# __doc__:extend function for libMA

#Database
HOST = ''
USER = ''
PASSWD = '!@#'
DB = ''

#Strategy
DA_MO_SHEN = False
STRATEGY = 'collect' #kill or collect
LAST_HIT_BC = 30
COLLECTION_PER_BC = 6

#Area
SHOW_AREA = True

#Ranking
SHOW_RANKING = True
RANKING_TYPE = 3

#Friend List
SHOW_FRIEND = False

#Get reward
AUTO_GET_REWARD = True

#Gacha
GACHA_SWITCH = False

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
        "义妹型奎利亚" : [2,2,15,28],
        "义妹型艾玛" : [2,2,15,28],
        "义妹型爱匹莉娅" : [2,3,1,16],
        }

#Auto combination card
AC_SWITCH = True
AC_CARD= ()
AC_BLACK_LIST = ('第二型毕斯克拉乌莉特')
AC_BL = ()
AC_CARDS_PER_TIME = 30
AC_RARITY = 3

#PVP switch
PVP_SWITCH = False
