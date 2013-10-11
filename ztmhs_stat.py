__author__ = 'gaonan'
#coding=utf-8
import sys
import json
import logging
from send_tools import SendTools
import time
import datetime

class Stat:
    def __init__(self,file_name,date_str,c_day,t_day):
        self.file_name = file_name
        self.date_str = date_str
        self.c_day = int(c_day)
        self.t_day = int(t_day)
        self.total_home_num = 0
        self.home_user = {}
        self.feed_pv = {}
        self.feed_uv = {}

        self.feed_page_pv = {}
        self.feed_page_uv = {}
        self.clk_pv = {}
        self.clk_uv = {}
        self.clk_page_pv = {}
        self.clk_page_uv = {}
        self.clk_poi_pv = {}
        self.clk_poi_uv = {}

        self.clk_uniq = {}

        self.idx_page = {}
        self.idx_idx = {}

        self.one_feed_pv = {}
        self.one_feed_uv = {}
        self.one_feed_link = {}
        self.all_cookie_num = 0
        self.count_cookie_num = 0
        self.continue_cookie_num = 0


        self.all_num = 0
        self.all_user = {}
        self.seckill_num = 0
        self.seckill_user = {}

        self.ignore_ua = ['JianKongBao']
    def is_need_process(self,line):
        if self.date_str in line:
            return True
        else:
            return False
    def process_home(self,line):
        seg = line.split('get_home=')
        if len(seg) != 2:
            return
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cid'],'unknown') == 0:
            return
        if 'ua' not in item:
            return
        for ua in self.ignore_ua:
            if ua in item['ua']:
                return
        self.total_home_num += 1
        if item['cid'] not in self.home_user:
            self.home_user[item['cid']] = 1
        else:
            self.home_user[item['cid']] += 1

    def process_feed(self,line):
        seg = line.split('get_feed=')
        if len(seg) != 2:
            return
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cid'],'unknown') == 0:
            return
        #统计点击子标签
        if item['type'] != 0 and item['pn'] == 1:
            self.add_dict(self.feed_pv,item['type'],1)
            key = 'feed type' + str(item['type']) + item['cid']
            if key not in self.clk_uniq:
                self.add_dict(self.feed_uv,item['type'],1)
                self.clk_uniq[key] = 1

        #统计点击翻页
        if item['pn'] > 1:
            self.add_dict(self.feed_page_pv,item['pn'],1)
            key = 'feed pn' + str(item['pn']) + item['cid']
            if key not in self.clk_uniq:
                self.add_dict(self.feed_page_uv,item['pn'],1)
                self.clk_uniq[key] = 1

    def add_dict(self,dict,key,value):
        if key in dict:
            dict[key] += value
        else:
            dict[key] = value
    def add_dict_double_key(self,dict,key1,key2,value):
        if key1 in dict:
            if key2 in dict[key1]:
                dict[key1][key2] += value
            else:
                dict[key1][key2] = value
        else:
            temp_dict = {}
            temp_dict[key2] = value
            dict[key1] = temp_dict

    def _process_type_clk(self,type,item):

        self.add_dict(self.clk_pv,"-1",1)
        key = 'all' + item['cookie_id']
        if key not in self.clk_uniq:
            self.add_dict(self.clk_uv,"-1",1)
            self.clk_uniq[key] = 1
        self.add_dict(self.clk_pv,type,1)
        key = 'type' + type + item['cookie_id']
        if key not in self.clk_uniq:
            self.add_dict(self.clk_uv,type,1)
            self.clk_uniq[key] = 1

        if int(item['top_type']) == 1:
            top_type = "40"
        else:
            top_type = "50"
        self.add_dict(self.clk_pv,top_type,1)
        key = 'type' + top_type + item['cookie_id']
        if key not in self.clk_uniq:
            self.add_dict(self.clk_uv,top_type,1)
            self.clk_uniq[key] = 1

        feed_idx = (int(item['page_num'])-1)*10 + int(item['index_num'])
        self.idx_page[feed_idx] = int(item['page_num'])
        self.idx_idx[feed_idx] = int(item['index_num']) + 1

        self.add_dict(self.clk_page_pv,feed_idx,1)
        key = 'page' + str(feed_idx) + item['cookie_id']
        if key not in self.clk_uniq:
            self.add_dict(self.clk_page_uv,feed_idx,1)
            self.clk_uniq[key] = 1

        self.add_dict(self.clk_poi_pv,item['clk_position'],1)
        key = 'poi' + item['clk_position'] + item['cookie_id']
        if key not in self.clk_uniq:
            self.add_dict(self.clk_poi_uv,item['clk_position'],1)
            self.clk_uniq[key] = 1

        self.add_dict(self.one_feed_pv,item['feed_id'],1)
        key = 'feed' + item['feed_id'] + item['cookie_id']
        if key not in self.clk_uniq:
            self.add_dict(self.one_feed_uv,item['feed_id'],1)
            self.clk_uniq[key] = 1
        #print item['real_link'],item['real_link'][:-2]
        if not item['real_link'][-1].isalnum():
            self.one_feed_link[item['feed_id']] = item['real_link'][:-2]
        else:
            self.one_feed_link[item['feed_id']] = item['real_link']
        self.one_feed_link[item['feed_id']] = self.one_feed_link[item['feed_id']]
    def process_clk(self,line):
        seg = line.split('clk=')
        if len(seg) != 2:
            return
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cookie_id'],'unknown') == 0:
            return
        self._process_type_clk(item['search_type'],item)
    def get_process_day(self,range_day):
        cur_unix_time = int(time.mktime(time.strptime(self.date_str,'%Y-%m-%d')))
        #print cur_unix_time
        last_unix_time = cur_unix_time - 86400 * (range_day - 1)
        #print last_unix_time
        value = time.localtime(last_unix_time)
        return time.strftime('%Y-%m-%d', value)
    def process_keep(self):
        cut_day = self.get_process_day(self.t_day)
        last_day = self.get_process_day(self.c_day)

        #print last_day
        cookie_all = {}
        cookie_t = {}

        cookie_last_all = {}
        cookie_last_t = {}
        fp = open(self.file_name,'r')
        for line in fp:
            seg = line.split(' ')
            if cmp(seg[0],self.date_str) <=0 and cmp(seg[0],cut_day) >=0 and 'get_home=' in line:
                segr = line.split('get_home=')
                if len(segr) != 2:
                    continue
                cur_str = segr[1]
                item = json.loads(cur_str)
                if cmp(item['cid'],'unknown') == 0:
                    continue
                if 'ua' not in item:
                    continue
                flag = False
                for ua in self.ignore_ua:
                    if ua in item['ua']:
                        flag = True
                if flag:
                    continue
                key = '%s-%s'%(item['cid'],seg[0])
                if cmp(seg[0],last_day) >=0:
                    if key not in cookie_last_all:
                        if item['cid'] not in cookie_last_t:
                            cookie_last_t[item['cid']] = 1
                        else:
                            cookie_last_t[item['cid']] += 1
                    cookie_last_all[key] = 1
                if key not in cookie_all:
                    if item['cid'] not in cookie_t:
                        cookie_t[item['cid']] = 1
                    else:
                        cookie_t[item['cid']] += 1
                    cookie_all[key] = 1
        for (key,value) in cookie_t.items():
            if value >= self.c_day:
                self.count_cookie_num += 1
            self.all_cookie_num += 1
        for (key,value) in cookie_last_t.items():
            if value >= self.c_day:
                self.continue_cookie_num += 1
        fp.close()

    def process(self):
        fp = open(self.file_name,'r')
        for line in fp:
            line = line[:-1]

            if not self.is_need_process(line):
                continue
            if 'get_home=' in line:
                self.process_home(line)
            elif 'get_feed=' in line:
                self.process_feed(line)
            elif 'clk=' in line:
                self.process_clk(line)
            else:
                continue
        fp.close()
    def output_txt(self):
        str = ''
        str = str + '首页(总)访问pv: %d uv:%d'%(self.total_home_num,len(self.home_user)) + '\n'
        str = str + '总点击pv: %d uv: %d'%(self.clk_pv["-1"],self.clk_uv["-1"]) + '\n'
        str = str + '点击率:%.3f uv点击率:%.3f'%(float(self.clk_pv["-1"])/self.total_home_num,float(self.clk_uv["-1"])/len(self.home_user))  + '\n'
        str = str + '%d天内总用户:%d, 至少访问%d天用户数:%d, 活跃度:%.4f\n'%(self.t_day,self.all_cookie_num,self.c_day,self.count_cookie_num,float(self.count_cookie_num)/self.all_cookie_num)
        str = str + '最近%d天内连续活跃用户数:%d, 当天总用户数:%d, 比例:%.4f\n'%(self.c_day,self.continue_cookie_num,len(self.home_user),float(self.continue_cookie_num)/self.total_home_num)
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.feed_pv.items():
            if key == 1:
                str = str +  '白菜价标签点击pv: %d uv: %d'%(self.feed_pv[1],self.feed_uv[1]) + '\n'
            else:
                str = str +  '全网最低标签点击pv: %d uv: %d'%(self.feed_pv[2],self.feed_uv[2]) + '\n'
        sorted_list = sorted(self.feed_page_pv.items(), key=lambda d:d[0],reverse=False)
        for (pn,value) in sorted_list:
            str = str +  '第 %d页 pv: %d uv: %d'%(pn,value,self.feed_page_uv[pn]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.clk_pv.items():
            if int(key) == 0:
                str = str + '全部结果状态下点击pv: %d uv: %d'%(self.clk_pv["0"],self.clk_uv["0"]) + '\n'
            elif int(key) == 1:
                str = str + '白菜价状态下点击pv: %d uv: %d'%(self.clk_pv["1"],self.clk_uv["1"]) + '\n'
            elif int(key) == 2:
                str = str + '全网最低状态下点击pv: %d uv: %d'%(self.clk_pv["2"],self.clk_uv["2"]) + '\n'
            elif int(key) == 40:
                str = str + '置顶结果点击pv: %d uv: %d'%(self.clk_pv["40"],self.clk_uv["40"]) + '\n'
            elif int(key) == 50:
                str = str + '非置顶结果点击pv: %d uv: %d'%(self.clk_pv["50"],self.clk_uv["50"]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        sorted_list = sorted(self.clk_page_pv.items(), key=lambda d:d[0],reverse=False)
        for (pn,value) in sorted_list:
            if pn < 0:
                str = str + '置顶第 %d项(%d页%d项) 点击pv: %d 点击uv: %d'%(pn+10,self.idx_page[pn]+1,self.idx_idx[pn],value,self.clk_page_uv[pn]) + '\n'
            else:
                str = str + '第 %d项(%d页%d项) 点击pv: %d 点击uv: %d'%(pn,self.idx_page[pn],self.idx_idx[pn],value,self.clk_page_uv[pn]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.clk_poi_pv.items():
            if int(key) == 1:
                str = str + '标题点击pv: %d uv: %d'%(self.clk_poi_pv["1"],self.clk_poi_uv["1"]) + '\n'
            elif int(key) == 2:
                str = str + '图片点击pv: %d uv: %d'%(self.clk_poi_pv["2"],self.clk_poi_uv["2"]) + '\n'
            elif int(key) == 3:
                str = str + '直达链接点击pv: %d uv: %d'%(self.clk_poi_pv["3"],self.clk_poi_uv["3"]) + '\n'
            else:
                str = str + '文字链接点击pv: %d uv: %d'%(self.clk_poi_pv["4"],self.clk_poi_uv["4"]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        str = str.decode('utf8')
        sorted_list = sorted(self.one_feed_pv.items(), key=lambda d:d[1],reverse=True)
        #import pdb
        #pdb.set_trace()
        for (key,value) in sorted_list:
            #continue
            temp_str = u'feed: %d' + self.one_feed_link[key] + u'  点击pv: %d uv: %d'%(value,self.one_feed_uv[key]) + u'\n'
            # self.one_feed_link[key]
            str = str + temp_str
        return str

    '''def output(self):
        print '首页(总)访问pv: %d uv:%d'%(self.total_home_num,len(self.home_user))
        print '总点击pv: %d uv: %d'%(self.clk_pv["-1"],self.clk_uv["-1"])
        print '点击率:%.3f uv点击率:%.3f'%(float(self.clk_pv["-1"])/self.total_home_num,float(self.clk_uv["-1"])/len(self.home_user))

        print '****************分割线*****************************************'
        for (key,value) in self.feed_pv.items():
            if key == 1:
                print '白菜价标签点击pv: %d uv: %d'%(self.feed_pv[2],self.feed_uv[2])
            else:
                print '全网最低标签点击pv: %d uv: %d'%(self.feed_pv[1],self.feed_uv[1])

        sorted_list = sorted(self.feed_page_pv.items(), key=lambda d:d[0],reverse=False)
        for (pn,value) in sorted_list:
            print '第 %d页 pv: %d uv: %d'%(pn,value,self.feed_page_uv[pn])

        print '****************分割线*****************************************'
        for (key,value) in self.clk_pv.items():
            if int(key) == 0:
                print '全部结果状态下点击pv: %d uv: %d'%(self.clk_pv["0"],self.clk_uv["0"])
            elif int(key) == 1:
                print '白菜价状态下点击pv: %d uv: %d'%(self.clk_pv["1"],self.clk_uv["1"])
            elif int(key) == 2:
                print '全网最低状态下点击pv: %d uv: %d'%(self.clk_pv["2"],self.clk_uv["2"])
        print '****************分割线*****************************************'
        sorted_list = sorted(self.clk_page_pv.items(), key=lambda d:d[0],reverse=False)
        for (pn,value) in sorted_list:
            if pn < 0:
                print '置顶第 %d项(%d页%d项) 点击pv: %d 点击uv: %d'%(pn+10,self.idx_page[pn]+1,self.idx_idx[pn],value,self.clk_page_uv[pn])
            else:
                print '第 %d项(%d页%d项) 点击pv: %d 点击uv: %d'%(pn,self.idx_page[pn],self.idx_idx[pn],value,self.clk_page_uv[pn])
        print '****************分割线*****************************************'
        for (key,value) in self.clk_poi_pv.items():
            if int(key) == 1:
                print '标题点击pv: %d uv: %d'%(self.clk_poi_pv["1"],self.clk_poi_uv["1"])
            elif int(key) == 2:
                print '图片点击pv: %d uv: %d'%(self.clk_poi_pv["2"],self.clk_poi_uv["2"])
            elif int(key) == 3:
                print '直达链接点击pv: %d uv: %d'%(self.clk_poi_pv["3"],self.clk_poi_uv["3"])
            else:
                print '文字链接点击pv: %d uv: %d'%(self.clk_poi_pv["4"],self.clk_poi_uv["4"])
        print '****************分割线*****************************************'  + '\n'
        sorted_list = sorted(self.feed_pv.items(), key=lambda d:d[1],reverse=True)
        for (key,value) in sorted_list:
            print 'feed:%s 点击pv: %d uv: %d'%(self.feed_link[key],value,self.feed_uv[key]) + '\n'
        return str'''

if __name__ == "__main__":

    logger = logging.getLogger('stat_log')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    st = SendTools('1111111','ops@maimiaotech.com','maimiaoops2013')
    my_stat = Stat(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    my_stat.process_keep()
    my_stat.process()
    out_str = my_stat.output_txt()
    subject = 'ztmhs数据统计' + sys.argv[2]
    #addressee = '2c@maimiaotech.com'
    addressee = 'gaonan@maimiaotech.com'
    #import pdb
    #pdb.set_trace()
    st.send_email_with_text(addressee, out_str, subject)
