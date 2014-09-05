#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author:cyxsheep
# __doc__:extend function for libMA
import config
import simplejson as json
import ma
import MySQLdb
import math
import datetime
import time
import random
import copy
import sys

class sp_card:
    name = ''
    serial_id = ''
    master_card_id = ''
    lv = 0
    power = 0
    hp = 0
    hp_power = 0
    cp = 0
    cost = 0

class Bot(object):

    def __init__(self):
        self.ma = ma.MA()
        self.my_fairy = None
        self.touched_fairies = set()
        self.touched_spe_fairies = set()
        self.most_powerful = []
        self.ma.user_id = 0
        self.battleCard = []
        self.min_cost_card = None

    def run(self,fs):
        try:
            self.touched_fairies = fs
            self._print('--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*')
            body = self.ma.login(config.loginId, config.password)
            if not self.ma.user_id:
                self.ma.user_id = (body.xpath('./login/user_id/text()'))[0]
            self._print('登录成功')
            self.db_userdatacollect()
            self.db_cardCollect()
            if not self.battleCard:
                self.battleCard = self.db_battleCardCollect()
            self.func_getRewardMoney()
            self.func_forceExplore()
            self.func_forceItem()
            self.func_forceSellCard()
            self.msg_itemlist()
            try:
                self.msg_ranking()
                self.func_forceCombination()
            except:
                pass
            self.func_autoGacha()
            self.func_sellCard()
            try:
                self.func_autoCardCombination()
            except:
                self.func_forcesellCard()
                pass
            if len(self.ma.cards) < 250:
                self.func_battleFairy()
                self.func_mostPowerful()
                self.func_exploreArea()
                self.func_autoGetReward()
            self.func_pvpbattle()
            self.func_friendList()
            self.db_skilldb()
        except ma.HeaderError, e:
            print e.code, e.message
            if e.code == 1020:
                time.sleep(60)
            import traceback; traceback.print_exc(file=open('error_log','a'))
            pass
        except Exception, e:
            print e
            z = open('error_log','a')
            t = datetime.datetime.now()
            z.write("%s\n" % t.ctime())
            import traceback; traceback.print_exc(file=open('error_log','a'))
            pass
        return

    def db_config(self):
        f = open('config.json','r')
        s = json.load(f)
        f.close()
        while(not s):
            f = open('config.json','r')
            s = json.load(f)
            f.close()
        return s

    def db_connect(self):
        s = self.db_config()
        conn = MySQLdb.connect(host=s['HOST'], user=s['USER'],passwd=s['PASSWD'],db=s['DB'],unix_socket='/tmp/mysql.sock', init_command="set names utf8")
        return conn

    def db_cardset(self, msg):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        addquery = "insert into card_data values(NULL,'%s')" % msg
        cursor.execute(addquery)
        conn.commit()
        conn.close()

    def db_battledata(self, battleData):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        counter = 0
        atk = {}
        hp = 0
        for k in battleData['card_origin']:
            group = counter/3
            if group in atk:
                atk[group] += self.ma.cards[k].power
            else:
                atk[group] = self.ma.cards[k].power
            hp += self.ma.cards[k].hp
            counter += 1
        result = self.func_battleSimulate(int(battleData['f_atk']),int(battleData['f_hp']),atk.values(),hp)
        battleData['damage_est'] = result["damage"]
        if "collect" in battleData:
            battleData['collect_est'] = self.func_collect(battleData['f_lv'],battleData['damage_est'],battleData['f_name'])
        else:
            battleData['collect'] = 0
            battleData['collect_est'] = 0
        addquery = "insert into battledata values(NULL,%s,%s,%s,%s,%s,'%s',now(),%s,'%s',%s,%s)" % (battleData["bc"],battleData["collect"],battleData["collect_est"],battleData["damage"],battleData["damage_est"],battleData["card"].encode('utf8'),battleData["f_lv"],battleData["f_name"],battleData["f_hp"],battleData["f_atk"])
        cursor.execute(addquery)
        conn.commit()
        conn.close()

    def db_userdatacollect(self):
        conn = self.db_connect()
        s = self.db_config()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        timequery = "select max(collecttime) from userdata"
        cursor.execute(timequery)
        lasttime = cursor.fetchone()[0]
        t = datetime.datetime.now()
        a = t - lasttime
        timelag = a.seconds
        if (timelag > 300):
            if self.ma.iterms.has_key('%s' % s['DATACOLLECTITEM']):
                item = self.ma.iterms[str(s['DATACOLLECTITEM'])]
            else:
                item = 0
            fairy_reward = int(self.ma.fairy_select().xpath('//remaining_rewards/text()')[0])
            addquery = "insert into userdata values(NULL,NULL,%s,%s,%s)" % (self.ma.bc,item,fairy_reward)
            cursor.execute(addquery)
            conn.commit()
        conn.close()

    def db_skilldb(self):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        for card in self.ma.cards.values():
            if 'skill_type' in dir(card):
                countquery = "select count(*) from skill where type=%s and name like '%s'" % (card.skill_type,card.skill_description)
                cursor.execute(countquery)
                countquery = cursor.fetchone()[0]
                if countquery == 0:
                    addquery = "insert into skill values(NULL,%s,'%s')" % (card.skill_type,card.skill_description)
                    countfairy = cursor.execute(addquery)
                    conn.commit()
        conn.close()

    def db_fairyCollect(self,lv,name,power,hp_max):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        countquery = "select count(*) from fairy where lv='%s' and name='%s' and atk='%s'" % (lv,name,power)
        cursor.execute(countquery)
        countquery = cursor.fetchone()[0]
        if countquery == 0:
            addquery = "insert into fairy values(NULL,%s,'%s',%s,%s)" % (lv,name,power,hp_max)
            countfairy = cursor.execute(addquery)
            conn.commit()
        conn.close()

    def db_fairyDetail(self,lv,option,fname):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        countquery = "select * from fairy_d where name='%s' " % (fname)
        cursor.execute(countquery)
        res = cursor.fetchone()
        if res:
            (mark1,mark2,atkK,atkB,hpK,hpB) = res
        else:
            calc_q = "select * from fairy where name = '%s' " % (fname)
            cursor.execute(calc_q)
            res_q = cursor.fetchall()
            if len(res_q):
                i = 1
                flag = 0
                while i<len(res_q):
                    if int(res_q[0][1]) != int(res_q[i][1]):
                        flag = 1
                        break
                    else:
                        i += 1
                if flag:
                    atkK = (int(res_q[0][3]) - int(res_q[i][3])) / (int(res_q[0][1]) - int(res_q[i][1]))
                    atkB = int(res_q[0][3]) - int(res_q[0][1])*atkK
                    hpK = (int(res_q[0][4]) - int(res_q[i][4])) / (int(res_q[0][1]) - int(res_q[i][1]))
                    hpB = int(res_q[0][4]) - int(res_q[0][1])*hpK
                    addquery = "insert into fairy_d values(NULL,'%s',%s,%s,%s,%s)" % (fname,atkK,atkB,hpK,hpB)
                    countfairy = cursor.execute(addquery)
                    conn.commit()
                else:
                    calc_q = "select * from fairy where name = '%s' and lv = %s" % (fname,lv)
                    cursor.execute(calc_q)
                    res_q = cursor.fetchone()
                    if res_q:
                        if option == 'atk':
                            return int(res_q[3])
                        else:
                            return int(res_q[4])
                    else:
                        return 1
            else:
                return 1
        atk = int(lv)*atkK+atkB
        hp = int(lv)*hpK+hpB
        conn.close()
        if option == 'atk':
            return atk
        else:
            return hp

    def db_cardCollect(self):
        self._print('数据库卡牌资料写入开始')
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        counter = int(self.ma.user_id)
        for card in self.ma.cards.values():
            cardclean = "delete from `card` where `user_id` = %s and `psy` = %s" % (self.ma.user_id , counter)
            cursor.execute(cardclean)
            conn.commit()
            if card.rarity == 0:
                card.rarity = (int(card.lv_max) + int(card.plus_limit_count) * 10 - int(card.holography) * 10)/10 - 4
            addquery = "insert into `card` values(%s,%s,%s,'%s',%s,%s,%s,%s,%s,%s,%s,%s)" % (counter,card.serial_id,card.lv,card.name,card.master_card_id,card.holography,card.lv_max,card.hp,card.power,card.rarity,card.cost,self.ma.user_id)
            countfairy = cursor.execute(addquery)
            conn.commit()
            counter += 1
        cardclean = "delete from `card` where `user_id` = %s and `psy` >= %s" % (self.ma.user_id , counter)
        cursor.execute(cardclean)
        conn.commit()
        conn.close()
        self._print('数据库卡牌资料写入结束')

    def db_battleCardCollect(self,by="power", limit=150, reverse=True):
        conn = self.db_connect()
        s = self.db_config()
        cursor = conn.cursor()
        cursor.execute("set names utf8")
        countquery = "select * from card where user_id = "+self.ma.user_id
        cursor.execute(countquery)
        card_database = cursor.fetchall()
        atk_card = []
        newcard = []
        specialCardsNameList = s['SPECIAL_CARD'].keys()
        tMonth = int(str(datetime.date.today())[5:7])
        tDay = int(str(datetime.date.today())[8:10])
        for card_d in card_database:
            card = sp_card()
            card.serial_id = card_d[1]
            card.lv = int(card_d[2])
            card.name = card_d[3].decode('utf8')
            card.master_card_id = card_d[4]
            card.hp = int(card_d[7])
            card.power = int(card_d[8])
            card.cost = int(card_d[10])
            if card.lv != 1:
                if card.name in specialCardsNameList:
                    if int(s['SPECIAL_CARD'][card.name][1]) == tMonth and \
                            int(s['SPECIAL_CARD'][card.name][2]) < tDay < int(s['SPECIAL_CARD'][card.name][3]):
                        card.power = card.power * int(s['SPECIAL_CARD'][str(card.name)][0])
                card.hp_power = card.hp + card.power
                card.cp =  card.hp_power / card.cost
                newcard = copy.deepcopy(card)
                atk_card.append(newcard)
        return sorted(atk_card, key=lambda x: getattr(x, by),
            reverse=reverse)[:limit]

    def _print(self,message):
        t = datetime.datetime.now()
        print "[%s] %s" % (t.ctime(),message)

    def msg_itemlist(self):
        fairy_reward = int(self.ma.fairy_select().xpath('//remaining_rewards/text()')[0])
        (count,ac) = (0,0)
        res = []
        for rewardboxeach in self.ma.rewardbox().xpath('//rewardbox_list/rewardbox'):
            if int(rewardboxeach.xpath('type/text()')[0]) == 4:
                count += int(rewardboxeach.xpath('point/text()')[0])
            ac += 1
        self._print( [self.ma.iterms[str(b)] for b in sorted([int(a) for a in self.ma.iterms.keys()])])
        self._print(self.ma.iterms)
        #1是AP，2是BC，3是假卡，4是次元因子，68是金灿灿的碎片，201是巧克力，202是七彩辉石, 111是半绿，112是半红，
        self._print( 'BC:%s/%s AP:%s/%s EX:%s' % (self.ma.bc,self.ma.bc_max,self.ma.ap,self.ma.ap_max,self.ma.ex_gauge))
        self._print( '绿茶:%s/%s个 红茶:%s/%s个 友情点:%s 蛋卷:%s 卡数:%s 未领卡:%s张' % (self.ma.iterms['1'],self.ma.iterms['111'],self.ma.iterms['2'],self.ma.iterms['112'],self.ma.friendship_point,self.ma.gacha_ticket,len(self.ma.cards),fairy_reward))
        self._print( '箱中友情点:%s点 箱子:%s 金钱:%s 等级:%s 加点:%s 妖精出现中:%s 我的妖精:%s' % (count,ac,self.ma.gold,self.ma.town_level,self.ma.free_ap_bc_point,self.ma.fairy_appearance,self.my_fairy))
        self._print( '已经遇到%s只妖精 其中有%s只觉醒' % (len(self.touched_fairies),len(self.touched_spe_fairies)))

    def msg_ranking(self, ranktype_id=0):
        s = self.db_config()
        if s['SHOW_RANKING']:
            ranktype_id = s['RANKING_TYPE']
            ranklist = self.ma.get("~/ranking/ranking", ranktype_id=ranktype_id, top=0, move=1)
            self._print( '排行榜类型:%s' % (ranklist.xpath('//ranking/ranktype_id/text()')[0]))
            rid = []
            for rl in ranklist.xpath('//ranking/ranktype_list/ranktype'):
                self._print( '%s %s'% (rl.xpath('id/text()')[0],rl.xpath('title/text()')[0]))
                rid.append(rl.xpath('id/text()')[0])
                #self._print(self.ma.user_id)
            ranklist = self.ma.get("~/ranking/ranking", ranktype_id=rid[-1], top=0, move=1)
            for fl in ranklist.xpath('//ranking/user_list/user'):
                if int(self.ma.user_id) == int(fl.xpath('id/text()')[0]):
                    self._print( '%s %s %s'% (fl.xpath('name/text()')[0],fl.xpath('rank/text()')[0],fl.xpath('battle_event_point/text()')[0]))

    def func_exploreSelect(self):
        s = self.db_config()
        area_id = []
        today = int(time.strftime("%w"))
        today_area_id = 50000 + today
        areas = self.ma.area()
        area_detail = {}
        for area in areas.xpath('//area_info'):
            if s['SHOW_AREA']:
                self._print('%s %s %s%%' % (area.xpath('id/text()')[0],area.xpath('name/text()')[0], area.xpath('prog_area/text()')[0]))
            area_detail[int(area.xpath('id/text()')[0])] = area.xpath('name/text()')[0].encode('utf8')
            area_id_c = int(area.xpath('id/text()')[0])
            area_name = area.xpath('name/text()')[0].encode('utf8')
            if '限时' in area_name and self.my_fairy != True and int(area.xpath('prog_area/text()')[0]) < 100 :
                area_id.append(area_id_c)
                #try:
                    #self.ma.explore(area_id_c+1,1)
                #except:
                    #pass
                continue
            if int(area.xpath('prog_area/text()')[0]) < 100:
                checkmonth = str(time.strftime("%b", time.localtime()))
                checkday = int(time.strftime("%d", time.localtime()))
                if checkmonth == 'Jul' and checkday in range(1,17):
                    if area_id_c in s['AREA_LIST']:
                        area_id.append(area_id_c)
                    elif len(area_id) == 0:
                        try:
                            self.ma.explore(area_id_c+1,1)
                        except:
                            pass
                else:
                    area_id.append(area_id_c)
        if len(area_id) == 0:
            area_id.append(int(max(areas.xpath('//area_info/id/text()'))))
        for area in area_id:
            if today_area_id in area_id:
                if today_area_id == 50001 or today_area_id == 50003:
                    area_id_final = today_area_id
                    break
            area_id_final = area
            break
        floor_id = 0
        floor_cost = 0
        for floor in self.ma.floor(area_id_final).xpath('//floor_info'):
            if s['SHOW_AREA']:
                self._print( "floor:%s progress:%s%% cost:%s" % (floor.xpath('id/text()')[0], floor.xpath('progress/text()')[0], floor.xpath('cost/text()')[0]))
            if int(floor.xpath('id/text()')[0]) > floor_id and not int(floor.xpath('boss_id/text()')[0]):
                (floor_id,floor_cost) = (int(floor.xpath('id/text()')[0]),int(floor.xpath('cost/text()')[0]))
        assert floor_id
        self._print( "选择秘境 %s 第%d层 cost:%d" % (area_detail[area_id_final], floor_id, floor_cost))
        res = []
        res.append(area_id_final)
        res.append(floor_id)
        return res
        #return 'area_id floor_id'

    def func_exploreArea(self):
        areaInfo = self.func_exploreSelect()
        self._print(areaInfo)
        if self.my_fairy:
            ap_limit = self.ma.ap_max - 10
        else:
            ap_limit = self.ma.ap_max / 2
            if self.ma.bc > 200:
                ap_limit = 10
        #self._print([self.ma.ap,ap_limit,self.my_fairy])
        while self.ma.ap >= ap_limit:
            explore = self.ma.explore(areaInfo[0],areaInfo[1])
            if explore.xpath('//special_item'):
                if int(explore.xpath('//special_item/after_count/text()')[0]) != 0:
                    special_item_c = (int(explore.xpath('//special_item/after_count/text()')[0]) - int(explore.xpath('//special_item/before_count/text()')[0]))

                else :
                    special_item_c = int(explore.xpath('//special_item/before_count/text()')[0])
                self._print( "exp+%s gold+%s=%s 活动物品+%s progress:%s" % (explore.xpath('.//get_exp/text()')[0],\
                        explore.xpath('.//gold/text()')[0], self.ma.gold, special_item_c,\
                        explore.xpath('.//progress/text()')[0]))
            else:
                self._print( "exp+%s gold+%s=%s progress:%s%%" % (explore.xpath('.//get_exp/text()')[0],
                                                        explore.xpath('.//gold/text()')[0], self.ma.gold,
                                                        explore.xpath('.//progress/text()')[0], ))
            if explore.xpath('explore/lvup/text()')[0] == '1':
                self._print( 'level up!')
            else:
                self._print( "%sexp to go." % explore.xpath('explore/next_exp/text()')[0])
            if explore.xpath('./explore/fairy'):
                self._print( "find a fairy: %s lv%s" % (explore.xpath('.//fairy/name/text()')[0], explore.xpath('.//fairy/lv/text()')[0]))
                self.my_fairy = True
                return
            if explore.xpath('./explore/next_floor') and explore.xpath('.//next_floor//boss_id/text()')[0] == '0':
                floor_id = int(explore.xpath('.//next_floor/floor_info/id/text()')[0])
                floor_cost = int(explore.xpath('.//next_floor/floor_info/cost/text()')[0])
                self._print( "goto next floor:%s cost:%s" % (floor_id, floor_cost))
            if explore.xpath('./explore/user_card'):
                self._print( "got a card")

            if int(explore.xpath('.//progress/text()')[0]) == 100:
                self._print( "切换秘境")
                res = self.func_exploreSelect()
                (area_id,floor_id) = (res[0],res[1])
        #return 'explore result'
    def func_forceSellCard(self):
        s = self.db_config()
        try:
            self.ma.card_sell(s['FS_ID'])
        except:
            pass

    def func_sellCard(self):
        s = self.db_config()
        if s['SELL_CARD_SWITCH']:
            card_sell_serial_id = []
            for card in self.ma.cards.values():
                if '亚瑟' in card.name.encode('utf8'):
                    continue
                if len(card_sell_serial_id) == 30:
                    break
                if int(card.rarity) >= 3 or int(card.rarity) == 0:
                    continue
                if int(card.holography) == 1:
                    continue
                if int(card.cost) == 2 or int(card.cost) >= 99:
                    continue
                if int(card.lv) > 10:
                    continue
                card_sell_serial_id.append(card)
            if len(card_sell_serial_id):
                self._print( "卖出%s张卡" % len(card_sell_serial_id))
                self.ma.card_sell(card_sell_serial_id)

    def func_forceItem(self):
        s = self.db_config()
        if s['FI']:
            self._print("有人请你喝茶")
            item = ['','绿茶','红茶']
            if int(self.ma.bc) < 20 :
                self._print("喝茶条件符合开始喝茶")
                try:
                    self.ma.item_use(s['FI_ITEM'])
                    msg = "喝了%s" % item[s['FI_ITEM']]
                    self._print(msg)
                except:
                    self._print("没喝成功或者已经喝多了")
                    pass
            else:
                self._print("你没带够钱")

    def func_forcesellCard(self):
        s = self.db_config()
        card_sell_serial_id = []
        for card in self.ma.cards.values():
            if card.name in s['AC_BLACK_LIST']:
                continue
            if len(card_sell_serial_id) == 30:
                break
            if int(card.rarity) > 3 or int(card.rarity) == 0:
                continue
            if int(card.holography) == 1:
                continue
            if int(card.cost) == 2 or int(card.cost) >= 90:
                continue
            if int(card.lv) > 10:
                continue
            card_sell_serial_id.append(card)
        if len(card_sell_serial_id):
            self._print( "卖出%s张卡" % len(card_sell_serial_id))
            self.ma.card_sell(card_sell_serial_id)

    def func_getRewardMoney(self):
        if self.ma.free_ap_bc_point != 0:
            self.ma.pointsetting(0,int(self.ma.free_ap_bc_point))
        for rewardboxeach in self.ma.rewardbox().xpath('//rewardbox_list/rewardbox'):
            #self.ma.get_rewards(rewardboxeach.xpath('id/text()')[0])
            if int(rewardboxeach.xpath('type/text()')[0]) == 3:
                self.ma.get_rewards(rewardboxeach.xpath('id/text()')[0])
                #print "领取%s金币,我真特么有钱" % rewardboxeach.xpath('point/text()')[0]
            elif int(rewardboxeach.xpath('type/text()')[0]) != 4:
                self.ma.get_rewards(rewardboxeach.xpath('id/text()')[0])

    def func_collect(self,lv,damage,fname):
        a = u'觉醒'
        if not isinstance(lv,int):
            lv = int(lv)
        if not isinstance(fname,unicode):
            fname = fname.decode('utf8')
        if a in fname:
            c = int((40*lv+1000)*damage/self.db_fairyDetail(lv,'hp',fname))
        else:
            c = int(10*lv*damage/self.db_fairyDetail(lv,'hp',fname))
        return math.ceil(c/10*10)

    def func_newcalc(self,strategy,flv,fhp,cardset,fname):
        fatk = self.db_fairyDetail(flv,'atk',fname)
        bc = int(self.ma.bc)
        time_start = datetime.datetime.now()
        card_num = len(cardset)
        for i in range(card_num):
            for j in range(i+1,card_num):
                while (k-1 > j):
                    pass

    def func_battleCalc(self,strategy,flv,fhp,cardset,fname):
        s = self.db_config()
        t1 = datetime.datetime.now()
        fatk = self.db_fairyDetail(flv,'atk',fname)
        bestChoice = []
        bestChoiceCost = 99
        maxcpr = 0
        maxcollect = 0
        maxcollectCost = 999
        maxcollectCard = []
        cprs = 0
        killcard = []
        killcost = 9999
        bc = int(self.ma.bc)
        for i in range(len(cardset)):
            k = len(cardset) -1
            if int(cardset[i].cost) > bc:
                continue
            else:
                simulateResult = self.func_battleSimulate(fatk,fhp,[cardset[i].power,],cardset[i].hp)
                if simulateResult["result"] == 'win':
                    if int(cardset[i].cost) < killcost:
                        killcard = [cardset[i].serial_id,]
                        killcost = int(cardset[i].cost)
                collectitem = self.func_collect(flv,simulateResult["damage"],fname)
                cprs = collectitem/cardset[i].cost
                if cprs > maxcpr:
                    maxcpr = cprs
                    bestChoice = [cardset[i].serial_id,]
                    bestChoiceCost = cardset[i].cost
                if collectitem >= maxcollect and int(cardset[i].cost) <= maxcollectCost:
                    maxcollect = collectitem
                    maxcollectCard = [cardset[i].serial_id,]
                    maxcollectCost = int(cardset[i].cost)

            for j in range(i+1,len(cardset)):
                totalhp = int(cardset[i].hp) + int(cardset[j].hp)
                totalatk = int(cardset[i].power) + int(cardset[j].power)
                totalcost = int(cardset[i].cost) + int(cardset[j].cost)
                if totalcost > bc:
                    continue
                simulateResult = self.func_battleSimulate(fatk,fhp,[totalatk,],totalhp)
                if simulateResult["result"] == 'win':
                    if totalcost < killcost:
                        killcost = totalcost
                        killcard = [cardset[i].serial_id,cardset[j].serial_id]
                collectitem = self.func_collect(flv,simulateResult["damage"],fname)
                cprs = collectitem/totalcost
                if cprs > maxcpr:
                    maxcpr = cprs
                    maxcollect = collectitem
                    bestChoice= [cardset[i].serial_id,cardset[j].serial_id]
                    bestChoiceCost = totalcost
                if collectitem >= maxcollect and totalcost <= maxcollectCost:
                    maxcollect = collectitem
                    maxcollectCard = [cardset[i].serial_id,cardset[j].serial_id]
                    maxcollectCost = totalcost
                while (k-1 > j):
                    totalhp = int(cardset[i].hp) + int(cardset[j].hp) + int(cardset[k].hp)
                    totalatk = int(cardset[i].power) + int(cardset[j].power) + int(cardset[k].power)
                    totalcost = int(cardset[i].cost) + int(cardset[j].cost) + int(cardset[k].cost)
                    if totalcost > bc:
                        k -= 1
                        continue
                    simulateResult = self.func_battleSimulate(fatk,fhp,[totalatk,],totalhp)
                    if simulateResult["result"] == 'win':
                        if totalcost < killcost:
                            killcost = totalcost
                            killcard = [cardset[i].serial_id,cardset[j].serial_id,cardset[k].serial_id]
                    collectitem = self.func_collect(flv,simulateResult["damage"],fname)
                    cprs = collectitem/totalcost
                    if cprs > maxcpr:
                        maxcpr = cprs
                        maxcollect = collectitem
                        bestChoice= [cardset[i].serial_id,cardset[j].serial_id,cardset[k].serial_id]
                        bestChoiceCost = totalcost
                    if collectitem >= maxcollect and totalcost <= maxcollectCost:
                        maxcollect = collectitem
                        maxcollectCard = [cardset[i].serial_id,cardset[j].serial_id,cardset[k].serial_id]
                        maxcollectCost = totalcost
                    k -= 1
        if bc > 90:
            count = 0
            for i in range(0,len(cardset)-6):
                card1 = cardset[i]
                card2 = cardset[i+2]
                card3 = cardset[i+4]
                card4 = cardset[i+1]
                card5 = cardset[i+3]
                card6 = cardset[i+5]
                totalhp = int(card1.hp) + int(card2.hp) + int(card3.hp) + int(card4.hp) + int(card5.hp) + int(card6.hp)
                totalatk = []
                totalatk.append (int(card1.power) + int(card2.power) + int(card3.power))
                totalatk.append (int(card4.power) + int(card5.power) + int(card6.power))
                totalcost = int(card1.cost) + int(card2.cost) + int(card3.cost) + int(card4.cost) + int(card5.cost) + int(card6.cost)

                if totalcost > bc:
                    continue
                count += 1
                simulateResult = self.func_battleSimulate(fatk,fhp,totalatk,totalhp)
                if simulateResult["result"]== 'win':
                    #print '%s %s' % (totalcost,killcost)
                    if totalcost < killcost:
                        killcost = totalcost
                        killcard = []
                        killcard.append(card1.serial_id)
                        killcard.append(card2.serial_id)
                        killcard.append(card3.serial_id)
                        killcard.append(card4.serial_id)
                        killcard.append(card5.serial_id)
                        killcard.append(card6.serial_id)
                collectitem = self.func_collect(flv,simulateResult["damage"],fname)
                cprs = collectitem/totalcost
                if cprs > maxcpr:
                    maxcpr = cprs
                    maxcollect = collectitem
                    bestChoice = []
                    bestChoice.append(card1.serial_id)
                    bestChoice.append(card2.serial_id)
                    bestChoice.append(card3.serial_id)
                    bestChoice.append(card4.serial_id)
                    bestChoice.append(card5.serial_id)
                    bestChoice.append(card6.serial_id)
                    bestChoiceCost = totalcost
                if collectitem >= maxcollect:
                    maxcollect = collectitem
                    maxcollectCard = []
                    maxcollectCard.append(card1.serial_id)
                    maxcollectCard.append(card2.serial_id)
                    maxcollectCard.append(card3.serial_id)
                    maxcollectCard.append(card4.serial_id)
                    maxcollectCard.append(card5.serial_id)
                    maxcollectCard.append(card6.serial_id)
                    maxcollectCost = totalcost
        if bc > 180:
            count = 0
            end = len(cardset) - 9
            for i in range(0,end):
                card1 = cardset[i]
                card2 = cardset[i+3]
                card3 = cardset[i+6]
                card4 = cardset[i+1]
                card5 = cardset[i+4]
                card6 = cardset[i+7]
                card7 = cardset[i+2]
                card8 = cardset[i+5]
                card9 = cardset[i+8]
                totalhp = int(card1.hp) + int(card2.hp) + int(card3.hp) + int(card4.hp) + int(card5.hp) + int(card6.hp) + int(card7.hp) + int(card8.hp) + int(card9.hp)
                totalatk = []
                totalatk.append (int(card1.power) + int(card2.power) + int(card3.power))
                totalatk.append (int(card4.power) + int(card5.power) + int(card6.power))
                totalatk.append (int(card7.power) + int(card8.power) + int(card9.power))
                totalcost = int(card1.cost) + int(card2.cost) + int(card3.cost) + int(card4.cost) + int(card5.cost) + int(card6.cost) + int(card7.cost) + int(card8.cost) + int(card9.cost)
                if totalcost > bc:
                    continue
                count += 1
                simulateResult = self.func_battleSimulate(fatk,fhp,totalatk,totalhp)
                if simulateResult["result"] == 'win':
                    if totalcost < killcost:
                        killcost = totalcost
                        killcard = []
                        killcard.append(card1.serial_id)
                        killcard.append(card2.serial_id)
                        killcard.append(card3.serial_id)
                        killcard.append(card4.serial_id)
                        killcard.append(card5.serial_id)
                        killcard.append(card6.serial_id)
                        killcard.append(card7.serial_id)
                        killcard.append(card8.serial_id)
                        killcard.append(card9.serial_id)
                collectitem = self.func_collect(flv,simulateResult["damage"],fname)
                cprs = collectitem/totalcost
                if cprs > maxcpr:
                    maxcpr = cprs
                    maxcollect = collectitem
                    bestChoice = []
                    bestChoice.append(card1.serial_id)
                    bestChoice.append(card2.serial_id)
                    bestChoice.append(card3.serial_id)
                    bestChoice.append(card4.serial_id)
                    bestChoice.append(card5.serial_id)
                    bestChoice.append(card6.serial_id)
                    bestChoice.append(card7.serial_id)
                    bestChoice.append(card8.serial_id)
                    bestChoice.append(card9.serial_id)
                    bestChoiceCost = totalcost
                if collectitem >= maxcollect:
                    maxcollect = collectitem
                    maxcollectCard = []
                    maxcollectCard.append(card1.serial_id)
                    maxcollectCard.append(card2.serial_id)
                    maxcollectCard.append(card3.serial_id)
                    maxcollectCard.append(card4.serial_id)
                    maxcollectCard.append(card5.serial_id)
                    maxcollectCard.append(card6.serial_id)
                    maxcollectCard.append(card7.serial_id)
                    maxcollectCard.append(card8.serial_id)
                    maxcollectCard.append(card9.serial_id)
                    maxcollectCost = totalcost
        self._print( '最高比率:%s %s 最大收集:%s %s 尾刀:%s' % (maxcpr,bestChoiceCost,maxcollect,maxcollectCost,killcost))
        t2 = datetime.datetime.now()
        self._print( '耗时：%s' % (t2-t1))
        res = {
                'bestChoice' : bestChoice,
                'maxcpr' : maxcpr,
                'killcost' : killcost,
                'killcard' : killcard,
                'maxcollect' : maxcollect,
                'maxcollectCard' : maxcollectCard,
                'maxcollectCost' : maxcollectCost
                }
        return res

    def func_battleSimulate(self,fatk,fhp,matk,mhp):
        ex = int(self.ma.ex_gauge)
        res = {}
        damage = 0
        cardround = int(len(matk))
        t_atk = 0
        for a in matk:
            t_atk += a
        co = 0
        while True:
            if ex == 100:
                damage = damage + t_atk
                ex = 0
            else:
                if damage > fhp:
                    res["result"] = 'win'
                    res["damage"] = fhp
                    res["hp"] = mhp
                    break
                else:
                    i = co%cardround
                    damage += matk[i]
                    mhp -= fatk
                    ex += 5
                    if mhp <= 0:
                        res["result"] = 'lose'
                        res["damage"] = damage
                        break
        return res

    def func_quickBattle(self,card,fairy_id):
        #try:
            #self.db_cardset(' | '.join([self.ma.cards[k].name for k in card]))
        #except:
            #pass
        #self._print(' | '.join([self.ma.cards[k].name for k in card]))
        self.ma.save_deck_card(card)
#        try:
 #           battle = self.ma.fairy_battle(fairy_id, fairy_event.xpath('user/id/text()')[0],2)
        counter = 0
        for fairy_event in self.ma.fairy_select().xpath('//fairy_event'):
            fairy_info = self.ma.fairy_floor(fairy_event.xpath('fairy/serial_id/text()')[0],
                        fairy_event.xpath('user/id/text()')[0],fairy_event.fairy.race_type)
            if fairy_event.xpath('fairy/serial_id/text()')[0] == fairy_id:
                user_name = fairy_event.xpath('user/name/text()')[0].encode('utf8')
                while counter < 10:
                    self._print('狼娘速舔')
                    if self.ma.bc > 2:
                        try:
                            battle = self.ma.fairy_battle(fairy_id, fairy_event.xpath('user/id/text()')[0],fairy_event.fairy.race_type)
                            self.ma.bc -= 2
                            self._print(self.ma.bc)
                            counter += 1
                        except:
                            pass
                    else:
                        return

    def func_battleResult(self,card,fairy_id):
        try:
            self.db_cardset(' | '.join([self.ma.cards[k].name for k in card]))
        except:
            pass
        battleData = {}
        battleData['card'] =  ' | '.join([self.ma.cards[k].name for k in card])
        battleData['card_origin'] = card
        self._print(' | '.join([self.ma.cards[k].name for k in card]))
        self.ma.save_deck_card(card)
        for fairy_event in self.ma.fairy_select().xpath('//fairy_event'):
            fairy_info = self.ma.fairy_floor(fairy_event.xpath('fairy/serial_id/text()')[0],
                        fairy_event.xpath('user/id/text()')[0],fairy_event.fairy.race_type)
            if fairy_event.xpath('fairy/serial_id/text()')[0] == fairy_id:
                user_name = fairy_event.xpath('user/name/text()')[0].encode('utf8')
                battle = self.ma.fairy_battle(fairy_id, fairy_event.xpath('user/id/text()')[0],fairy_event.fairy.race_type)
                result = []
                fairy = battle.xpath('//battle_vs_info/player')[1]
                battleData['f_name'] = fairy.xpath('name/text()')[0].encode('utf8')
                battleData['f_lv'] = fairy_event.xpath('fairy/lv/text()')[0]
                battleData['f_hp'] = fairy_info.xpath('//fairy/hp/text()')[0]
                battleData['f_atk'] = fairy.xpath('.//power/text()')[0].encode('utf8')
                result.append('LV%s by %s %s HP:%s ATK:%s -' % (fairy_event.xpath('fairy/lv/text()')[0],user_name,fairy.xpath('name/text()')[0].encode('utf8'), fairy_info.xpath('//fairy/hp/text()')[0],
                                             fairy.xpath('.//power/text()')[0].encode('utf8')))
                if battle.xpath('//battle_result/winner/text()')[0] != '0':
                    result.append('WINNER!')
                damage = 0
                for action in battle.xpath('//battle_action_list'):
                    if action.xpath('attack_damage') and action.xpath('action_player/text()')[0] == '0':
                        damage += int(action.xpath('attack_damage//text()')[0])
                battleData['damage'] = damage
                battleData['bc'] = self.ma.cost
                result.append('damage:%d' % damage)
                result.append('exp+%d' % (int(battle.xpath('//battle_result/before_exp/text()')[0]) \
                                - int(battle.xpath('//battle_result/after_exp/text()')[0])))
                result.append('gold+%d' % (int(battle.xpath('//battle_result/after_gold/text()')[0]) \
                                - int(battle.xpath('//battle_result/before_gold/text()')[0])))
                try:
                    if battle.xpath('//battle_result/special_item/after_count/text()')[0]:
                        coll = int(battle.xpath('//battle_result/special_item/after_count/text()')[0]) - int(battle.xpath('//battle_result/special_item/before_count/text()')[0])
                        result.append('活动物品+%d' % (int(battle.xpath('//battle_result/special_item/after_count/text()')[0]) \
                                        - int(battle.xpath('//battle_result/special_item/before_count/text()')[0])))
                        real_cp = coll/self.ma.cost
                        battleData['collect'] = coll
                        result.append('实际比率为:%s' % real_cp)
                except:
                    pass
                self._print( ' '.join(result))
                self.db_fairyCollect(fairy_event.xpath('fairy/lv/text()')[0],fairy.xpath('name/text()')[0],fairy.xpath('.//power/text()')[0],fairy_info.xpath('//fairy/hp_max/text()')[0])
                self.db_battledata(battleData)
                time.sleep(5)

    def func_battleFairy(self):
        s = self.db_config()
        strategy = s['STRATEGY']
        fc = 0
        fairy_set = []
        touch_fairy_set = []
        cardset = self.battleCard
        for fairy_event in self.ma.fairy_select().xpath('//fairy_event'):
            self.my_fairy = None
            if fairy_event.xpath('put_down/text()')[0] == '1':
                fairy_in = []
                fairy_info = self.ma.fairy_floor(fairy_event.xpath('fairy/serial_id/text()')[0],
                        fairy_event.xpath('user/id/text()')[0],fairy_event.fairy.race_type)
                fairy_id = fairy_event.xpath('fairy/serial_id/text()')[0]
                if fairy_id not in self.touched_fairies:
                    fairy_info = self.ma.fairy_floor(fairy_event.xpath('fairy/serial_id/text()')[0],
                            fairy_event.xpath('user/id/text()')[0],fairy_event.fairy.race_type)
                    if self.ma.user_id in fairy_info.xpath('//attacker/user_id/text()'):
                        self.touched_fairies.add(fairy_id)
                    else:
                        touch_fairy_set.append(fairy_id)
                if str(fairy_event.xpath('user/id/text()')[0]) == str(self.ma.user_id):
                    self.my_fairy = True
                fairy_hp = int(fairy_info.xpath('//fairy/hp/text()')[0])
                if fairy_hp == 0:
                    continue
                fairy_lv = int(fairy_event.xpath('fairy/lv/text()')[0])
                fairy_name = fairy_info.xpath('//fairy/name/text()')[0]
                user_name = fairy_event.xpath('user/name/text()')[0]
                fairy_limit_time = int(fairy_info.xpath('//fairy/time_limit/text()')[0])
                if '觉醒' in fairy_name.encode('utf8') and s['DA_MO_SHEN'] and fairy_limit_time > 1200:
                    continue
                if '觉醒' in fairy_name.encode('utf8') and fairy_id not in self.touched_spe_fairies:
                    self.touched_fairies.add(fairy_id)
                fairy_limit_time = int(fairy_limit_time/60)
                fc = fairy_id
                fairy_in = [fairy_id,fairy_lv,fairy_hp,fairy_name,user_name,fairy_limit_time]
                fairy_set.append(fairy_in)
        if fairy_set:
            fairy_sorted = sorted(fairy_set, key=lambda x: x[2])
            choice = []
            my_fairy_tag = 0
            for fairy_inner in fairy_sorted:
                if user_name == self.ma.name:
                    my_fairy_tag = 1
                (fairy_id,fairy_lv,fairy_hp,fairy_name,user_name,fairy_limit_time) = fairy_inner
                self._print( 'Lv%s %s by %s 余血:%s ATK:%s 时间:%s分钟 C:%s' % (fairy_lv,fairy_name.encode('utf8'),user_name.encode('utf8'),fairy_hp,self.db_fairyDetail(fairy_lv,'atk',fairy_name),fairy_limit_time,self.func_collect(fairy_lv,fairy_hp,fairy_name)))
                calc = self.func_battleCalc(strategy,fairy_lv,fairy_hp,cardset,fairy_name)
                calc['bestfairy'] = fairy_id
                if int(calc['killcost']) < s['LAST_HIT_BC']:
                    self._print( '%sBC内尾刀为先' % s['LAST_HIT_BC'])
                    self.func_battleResult(calc['killcard'],fairy_id)
                    if fairy_id in touch_fairy_set:
                        touch_fairy_set.remove(fairy_id)
                    break
                if strategy == 'kill' and fairy_event.xpath('user/id/text()') == self.ma.user_id:
                    self._print('秒自妖需要%s的BC' % calc['killcost'])
                    bestcard = calc['killcard']
                    bestfairy = fairy_id
                    break
                choice.append(calc)
                self._print(" ".join(self.ma.cards[a].name for a in calc['bestChoice']))
            if choice:
                choice_sorted = sorted(choice, key=lambda x: x['maxcpr'], reverse=True)
                if choice_sorted[0]['maxcpr'] >= s['COLLECTION_PER_BC']:
                    self._print( '最高比率:%s' % choice_sorted[0]['maxcpr'])
                    self.func_battleResult(choice_sorted[0]['bestChoice'],choice_sorted[0]['bestfairy'])
                    if choice_sorted[0]['bestfairy'] in touch_fairy_set:
                        touch_fairy_set.remove(choice_sorted[0]['bestfairy'])
                #else:
                    #self.func_quickBattle([193012765, ],choice_sorted[0]['bestfairy'])

            if my_fairy_tag:
                self.my_fairy = True
            else:
                self.my_fairy = False
            if touch_fairy_set:
                self._print( '舔妖')
                for a in touch_fairy_set:
                    self.func_touchFairy(a)
        else:
            self._print('没有妖精出现')

    def func_touchFairy(self,fairy_id):
        if not self.min_cost_card:
            self.min_cost_card = sorted(self.ma.cards.values(),
                    key=lambda x: (x.cost, -(x.hp+x.power)))[0]
        if int(self.ma.bc) < int(self.min_cost_card.cost):
            self._print('BC不足以舔妖')
        elif self.func_battleResult([self.min_cost_card.serial_id,],fairy_id):
            self.touched_fairies.add(fairy_event.xpath('fairy/serial_id/text()')[0])
        return

    def func_mostPowerful(self):
        if self.most_powerful == []:
           self.most_powerful = sorted(self.ma.cards.values(),key=lambda x:(x.hp+x.power),reverse=True)[:12]
        self.ma.save_deck_card(self.most_powerful)
        self._print( '%sBC卡组镇楼' % self.ma.cost)

    def func_autoCardCombination(self):
        s = self.db_config()
        if not s['AC_SWITCH']:
            return
        self._print( '自动合成开始')
        for a in s['AC_CARD']:
            mainCard = []
            addCard = []
            plus_limit_count = 0
            for b in self.ma.cards.values():
                if b.rarity == 0:
                    b.rarity = (int(b.lv_max) + int(b.plus_limit_count) * 10 - int(b.holography) * 10)/10 - 4
                    if b.rarity <= 0:
                        b.rarity = 2
                if a == b.name:
                    if not mainCard:
                        mainCard = [b.serial_id,b.lv,b.lv_max,b.plus_limit_count,b.name]
                    elif b.lv >= mainCard[1]:
                        plus_limit_count += 1
                        addCard.append(self.ma.cards[mainCard[0]])
                        mainCard = [b.serial_id,b.lv,b.lv_max,b.plus_limit_count,b.name]
                    else:
                        plus_limit_count += 1
                        addCard.append(b)
                if b.rarity != 0 and b.rarity <= s['AC_RARITY'] and b.holography == 0 and b.lv <= 5 \
                        and b.cost < 20 \
                        and b.name not in s['AC_BLACK_LIST'] \
                        and len(addCard) < s['AC_CARDS_PER_TIME']:
                            addCard.append(b)
                if b.name in s['AC_BL'] and b.lv == 1 and b.holography == 0 and b.cost < 20:
                    addCard.append(b)
            if not mainCard:
                continue
            if mainCard[2] > mainCard[1] and len(addCard):
                self._print('对 %s 进行合成'% mainCard[4].encode('utf8'))
                self._print(' '.join([k.name for k in addCard]))
                self.ma.card_compound(mainCard[0],addCard)
            if not len(addCard):
                self._print('%s 没有狗粮'% mainCard[4].encode('utf8'))
                continue
            if mainCard[2] == mainCard[1]:
                if mainCard[3] == 0:
                    self._print('%s 已经满级！' % mainCard[4].encode('utf8'))
                elif plus_limit_count:
                    self._print('限界突破！')
                    self.ma.card_compound(mainCard[0],addCard)
                else:
                    self._print('%s 已经满级，还需%s次限界突破！'%(mainCard[4].encode('utf8'),mainCard[3]))
        self._print('自动合成结束')
        return

    def func_forceCombination(self):
        s = self.db_config()
        if s['FC']:
            try:
                self.ma.card_compound(s['A'],s['B'])
            except:
                self._print("强制合成失败")
                pass
        return

    def func_forceExplore(self):
        s = self.db_config()
        if not s['FE']:
            return
        if self.my_fairy:
            return
        #self._print('%s' % time.strftime("%a", time.localtime()))
        if time.strftime("%a", time.localtime()) != 'Mon':
            return
        while self.ma.ap > 3 and self.ma.bc < 200:
            #self._print('强制跑图')
            explore = self.ma.explore(s['FE_AREA'],s['FE_FLOOR'])
            if explore.xpath('//special_item'):
                if int(explore.xpath('//special_item/after_count/text()')[0]) != 0:
                    special_item_c = (int(explore.xpath('//special_item/after_count/text()')[0]) - int(explore.xpath('//special_item/before_count/text()')[0]))

                else :
                    special_item_c = int(explore.xpath('//special_item/before_count/text()')[0])
                self._print( "exp+%s gold+%s=%s 活动物品+%s progress:%s" % (explore.xpath('.//get_exp/text()')[0],\
                        explore.xpath('.//gold/text()')[0], self.ma.gold, special_item_c,\
                        explore.xpath('.//progress/text()')[0]))
            else:
                self._print( "exp+%s gold+%s=%s progress:%s%%" % (explore.xpath('.//get_exp/text()')[0],
                                                        explore.xpath('.//gold/text()')[0], self.ma.gold,
                                                        explore.xpath('.//progress/text()')[0], ))
            if explore.xpath('explore/lvup/text()')[0] == '1':
                self._print( 'level up!')
            else:
                self._print( "%sexp to go." % explore.xpath('explore/next_exp/text()')[0])
            if explore.xpath('./explore/fairy'):
                self._print( "find a fairy: %s lv%s" % (explore.xpath('.//fairy/name/text()')[0], explore.xpath('.//fairy/lv/text()')[0]))
                self.my_fairy = True
                return
            if explore.xpath('./explore/next_floor') and explore.xpath('.//next_floor//boss_id/text()')[0] == '0':
                floor_id = int(explore.xpath('.//next_floor/floor_info/id/text()')[0])
                floor_cost = int(explore.xpath('.//next_floor/floor_info/cost/text()')[0])
                self._print( "goto next floor:%s cost:%s" % (floor_id, floor_cost))
            if explore.xpath('./explore/user_card'):
                self._print( "got a card")
        if self.ma.bc <= 10:
            try:
                self.ma.item_use(2)
            except:
                pass
        if self.ma.ap <= 3:
            try:
                self.ma.item_use(1)
            except:
                s['FE'] = False
                pass

    def func_autoGetReward(self):
        s = self.db_config()
        if time.strftime("%a", time.localtime()) != 'Fri':
            if s['AUTO_GET_REWARD'] and len(self.ma.cards) < 250:
                self.ma.fairy_rewards()
        elif len(self.ma.cards) < 250:
            self.ma.fairy_rewards()

    def func_pvpbattle(self):
        s = self.db_config()
        if not s['PVP_SWITCH'] or self.ma.bc < 5:
            return
        if self.ma.bc < s['PVP_BC']:
            return
        users = []
        random_str = random.choice(',.1234567890abcdefghijklmnopqrstuvwxyz!@#$^&*()')
        for user in self.ma.player_search(random_str).xpath('//user'):
            uid = user.xpath('id/text()')[0]
            friend = user.xpath('friends/text()')[0]
            level = user.xpath('town_level/text()')[0]
            if friend == '0' and level == '4':
                users.append(uid)

        checktime = int(time.strftime("%M", time.localtime()))
        checkmonth = str(time.strftime("%b", time.localtime()))
        checkday = int(time.strftime("%d", time.localtime()))
        if checkmonth == 'Feb' and checkday in range(22,24):
            self.ma.save_deck_card([self.ma.cards[23159851],])
            battle_result = self.ma.get("~/battle/battle", user_id=random.choice(users), event_id=54)
        else:
            battle_result = self.ma.get("~/battle/battle",lake_id=3,parts_id=3,user_id=random.choice(users))
        win = battle_result.xpath('//winner/text()')[0]
        if win == '1':
            get_exp = int(battle_result.xpath('//before_exp/text()')[0]) - int(battle_result.xpath('//after_exp/text()')[0])
            if get_exp > 0 :
                self._print( "You Win! Got %d exps ; left %s exps" % (get_exp, battle_result.xpath('//after_exp/text()')[0]))
            else :
                self._print( "You Win! Level Up!")
        else :
            self._print( "Oh! you lose")

    def func_autoGacha(self):
        s = self.db_config()
        if self.ma.friendship_point >= 48000 or s['GACHA_SWITCH']:
            try:
                self.ma.gacha_buy()
            except:
                pass

    def func_friendList(self):
        s = self.db_config()
        if not s['SHOW_FRIEND']:
            return
        fl = self.ma.friendlist()
        coo = 0
        login_day = []
        for fri in fl.xpath('//friend_list/user'):
            temp_day = fri.xpath('last_login/text()')[0].encode('utf8')
            if temp_day == '2日':
                login_day.append((temp_day,fri.xpath('id/text()')[0]))
            if s['SHOW_FRIEND']:
                self._print( 'No.%s %s %s %s LV%s'% (coo,fri.xpath('name/text()')[0],fri.xpath('id/text()')[0],fri.xpath('last_login/text()')[0],fri.xpath('town_level/text()')[0]))
            coo += 1
        for (a,b) in sorted(login_day, key=lambda x: len(x[0]), reverse=True):
            try:
                self.ma.remove_friend(b)
            except:
                pass
        if a['SHOW_FRIEND']:
            self._print( '-----------')
        noti = self.ma.friend_notice()
        ccc = 0
        for fri in noti.xpath('//friend_notice/user_list/user'):
            if s['SHOW_FRIEND']:
                self._print( 'NO.%s %s %s %s LV%s %s'% (ccc,fri.xpath('name/text()')[0],fri.xpath('id/text()')[0],fri.xpath('last_login/text()')[0],fri.xpath('town_level/text()')[0],fri.xpath('friends/text()')[0]))
            ccc += 1
            temp_day = fri.xpath('last_login/text()')[0].encode('utf8')
            if int(fri.xpath('town_level/text()')[0]) < 70 or int(fri.xpath('friends/text()')[0]) == 30 or temp_day != '今天':
                self.ma.refuse_friend(fri.xpath('id/text()')[0])
            elif coo <= 28:
                self.ma.approve_friend(fri.xpath('id/text()')[0])
                coo += 1
                if s['SHOW_FRIEND']:
                    self._print('新增好友%s' % fri.xpath('name/text()')[0].encode('utf8'))
