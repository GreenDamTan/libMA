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
DA_MO_SHEN = False
STRATEGY = 'collect' #kill or collect
LAST_HIT_BC = 30
COLLECTION_PER_BC = 6

#Area
SHOW_AREA = True

#Ranking
SHOW_RANKING = True
RANKING_TYPE = 4

#Friend List
SHOW_FRIEND = True

#Get reward
AUTO_GET_REWARD = True

#Gacha
GACHA_SWITCH = False

#Sell card
SELL_CARD_SWITCH = True

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
AC_CARD= ('义妹型可可娜','剑神型阿科玛','剑神型巴鲁蒙克','第一型兰斯洛特','特异型帕尔修斯','特异型阿倍晴明')
AC_BLACK_LIST = ('第二型毕斯克拉乌莉特')
AC_BL = ('特异型汉尼拔','第二型柯尔格利万斯','特异型猎户座','特异型鲁克蕾齐亚','特异型安托瓦内特','星冠型处女座','魔装型兰斯洛特','魔装型罗恩格林','试作型洛特','复制型渔夫王','虏获型摩高斯','学徒型德斯迪奥','学徒型莫比尔菲','学徒型菈婕娅','炎夏型诺蕾','华恋型乌瑟','华恋型洛特','凯特西','特异型罗宾汉','第二型尤文','特异型乔治','特异型拿破仑','支援型乌妮莉','支援型艾多尔利亚','星冠型心宿二','星冠型军市一','幻兽型格里芬','支援型阿尔凯','支援型克罗基思','支援型索菲德','纯白型圣','华恋型达芬奇','第二型妮丝','第二型格里弗雷特','幻兽型里丘亚','幻兽型阿德拉梅莱克','支援型梅尔特')
AC_CARDS_PER_TIME = 30
AC_RARITY = 3
#Force combination card
FC = False
A = 306401261
B = 313672445

#Force explore
FE = False
FE_AREA = 50001
FE_FLOOR = 1

#PVP switch
PVP_SWITCH = False
