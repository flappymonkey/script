__author__ = 'gaonan'
#coding=utf-8
import sys
import json
from urllib import unquote
from send_tools import SendTools
import time

class Stat:
    def __init__(self,file_name,date_str,c_day,t_day1,t_day2):
        self.file_name = file_name
        self.date_str = date_str
        self.c_day = int(c_day)
        self.t_day1 = int(t_day1)
        self.t_day2 = int(t_day2)
        self.ignore_ua = ['JianKongBao']
        self.ignore_ip = ['122.224.126.']
        self.uniq_dict = {}


        self.total_pv_num = [0,0,0]
        self.total_uv_num = [0,0,0]

        self.total_clk_pv_num = [0,0,0]
        self.total_clk_uv_num = [0,0,0]

        self.feed_type_pv_dict = {}
        self.feed_page_pv_dict = {}
        self.seckill_type_pv_dict = {}
        self.seckill_page_pv_dict = {}

        self.feed_type_uv_dict = {}
        self.feed_page_uv_dict = {}
        self.seckill_type_uv_dict = {}
        self.seckill_page_uv_dict = {}

        self.feed_top_pv_dict = {}
        self.feed_top_uv_dict = {}
        self.seckill_top_pv_dict = {}
        self.seckill_top_uv_dict = {}
        self.feed_poi_pv_dict = {}
        self.feed_poi_uv_dict = {}

        self.feed_link_pv_dict = {}
        self.feed_link_uv_dict = {}
        self.seckill_link_pv_dict = {}
        self.seckill_link_uv_dict = {}

        self.total_keep_num = [0,0,0,0]
        self.feed_keep_num = [0,0,0,0]
        self.seckill_keep_num = [0,0,0,0]

    def get_process_day(self,range_day):
        cur_unix_time = int(time.mktime(time.strptime(self.date_str,'%Y-%m-%d')))
        last_unix_time = cur_unix_time - 86400 * (range_day - 1)
        value = time.localtime(last_unix_time)
        return time.strftime('%Y-%m-%d', value)
    def add_dict(self,dict,key,value):
        if key in dict:
            dict[key] += value
        else:
            dict[key] = value
    def process_home(self,count_pv,count_uv,count_list,line):
        i = 0
        key = 'process_home'
        for seg_str in count_list:
            key = key + seg_str
        for seg_str in count_list:
            if seg_str in line:
                seg = line.split(seg_str)
                break
            else:
                i += 1
        if i == len(count_list):
            return count_pv,count_uv
        if len(seg) != 2:
            return count_pv,count_uv
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cid'],'unknown') == 0:
            return count_pv,count_uv
        if 'ua' not in item or 'ip' not in item:
            return count_pv,count_uv
        for ua in self.ignore_ua:
            if ua in item['ua']:
                return count_pv,count_uv
        for ip in self.ignore_ip:
            if ip in item['ip']:
                return count_pv,count_uv
        key = key + item['cid']
        count_pv += 1
        if key not in self.uniq_dict:
            count_uv += 1
            self.uniq_dict[key] = 1
        return count_pv,count_uv
    def process_keep(self,count_list,c_day,count_day):

        last_day = self.get_process_day(c_day)

        #print last_day
        cookie_current = {}
        cookie_last = {}

        fp = open(self.file_name,'r')
        list_len = len(count_list)
        for line in fp:
            seg = line.split(' ')
            if cmp(seg[0],self.date_str) <=0 and cmp(seg[0],last_day) >=0:
                i = 0
                for seg_str in count_list:
                    if seg_str in line:
                        segr = line.split(seg_str)
                        break
                    else:
                        i += 1
                if i == list_len:
                    continue

                if len(segr) != 2:
                    continue
                cur_str = segr[1]
                item = json.loads(cur_str)
                if cmp(item['cid'],'unknown') == 0:
                    continue
                if 'ua' not in item or 'ip' not in item:
                    continue
                flag = False
                for ua in self.ignore_ua:
                    if ua in item['ua']:
                        flag = True
                for ip in self.ignore_ip:
                    if ip in item['ip']:
                        flag = True
                if flag:
                    continue
                key = '%s-%s'%(item['cid'],seg[0])
                '''if cmp(seg[0],last_day) >=0:
                    if key not in cookie_last_all:
                        if item['cid'] not in cookie_last_t:
                            cookie_last_t[item['cid']] = 1
                        else:
                            cookie_last_t[item['cid']] += 1
                    cookie_last_all[key] = 1'''

                if self.is_need_process(line):
                    if key not in cookie_current:
                        cookie_current[item['cid']] = 1
                    else:
                        cookie_current[item['cid']] += 1
                else:
                    if key not in cookie_last:
                        cookie_last[item['cid']] = 1
                    else:
                        cookie_last[item['cid']] += 1

                '''if key not in cookie_all:
                    if item['cid'] not in cookie_t:
                        cookie_t[item['cid']] = 1
                    else:
                        cookie_t[item['cid']] += 1
                    cookie_all[key] = 1'''
        '''count_cookie_num = 0
        #continue_cookie_num = 0
        all_cookie_num = 0
        for (key,value) in cookie_t.items():
            if value >= count_day:
                count_cookie_num += 1
            all_cookie_num += 1'''
        count_num = 0
        for (key,value) in cookie_current.items():
            if key in cookie_last and cookie_last[key] >= count_day:
                count_num += 1
        #for (key,value) in cookie_last_t.items():
        #    if value >= self.c_day:
        #        continue_cookie_num += 1
        fp.close()
        return count_num,len(cookie_current)

    def is_need_process(self,line):
        if self.date_str in line:
            return True
        else:
            return False

    def process_ajax_get(self,line,count_str,pv_dict,uv_dict,page_pv_dict,page_uv_dict):
        if count_str not in line:
            return
        seg = line.split(count_str)
        if len(seg) != 2:
            return
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cid'],'unknown') == 0:
            return
        if item['pn'] == 1:
            self.add_dict(pv_dict,item['type'],1)
            key = 'ajax_get_type' + count_str + str(item['type']) + item['cid']
            if key not in self.uniq_dict:
                self.add_dict(uv_dict,item['type'],1)
                self.uniq_dict[key] = 1
        else:
            self.add_dict(page_pv_dict,item['pn'],1)
            key = 'ajax_get_pn' + count_str + str(item['pn']) + item['cid']
            if key not in self.uniq_dict:
                self.add_dict(page_uv_dict,item['pn'],1)
                self.uniq_dict[key] = 1
    def process_clk_type(self,line,item_seg,show_type,pv_dict,uv_dict):
        seg = line.split('clk=')
        if len(seg) != 2:
            return
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cookie_id'],'unknown') == 0:
            return
        if 'ua' not in item or 'ip' not in item:
            return
        for ua in self.ignore_ua:
            if ua in item['ua']:
                return
        for ip in self.ignore_ip:
            if ip in item['ip']:
                return
        if 'show_type' not in item:
            return
        if show_type != item['show_type']:
            return
        if cmp('real_link',item_seg) == 0:
            dict_key = item[item_seg].encode('utf8')
        else:
            dict_key = item[item_seg]

        self.add_dict(pv_dict,dict_key,1)
        key = 'clk_type_' + item_seg  + '_' + str(show_type) + '_' + dict_key + '_' + item['cookie_id']
        if key not in self.uniq_dict:
            self.add_dict(uv_dict,dict_key,1)
            self.uniq_dict[key] = 1

    def process_clk_total(self,count_pv,count_uv,show_type,line):
        seg = line.split('clk=')
        if len(seg) != 2:
            return count_pv,count_uv
        cur_str = seg[1]
        item = json.loads(cur_str)
        if cmp(item['cookie_id'],'unknown') == 0:
            return count_pv,count_uv
        if 'ua' not in item or 'ip' not in item:
            return count_pv,count_uv
        for ua in self.ignore_ua:
            if ua in item['ua']:
                return count_pv,count_uv
        for ip in self.ignore_ip:
            if ip in item['ip']:
                return count_pv,count_uv
        if 'show_type' not in item:
            return count_pv,count_uv
        if show_type == 0 and item['show_type'] != 0:
                return count_pv,count_uv
        elif show_type == 1 and item['show_type'] != 1:
                return count_pv,count_uv
        count_pv += 1
        key = 'process_clk_total_' + str(show_type) + '_' + item['cookie_id']
        if key not in self.uniq_dict:
            count_uv += 1
            self.uniq_dict[key] = 1
        return count_pv,count_uv

    def process(self):
        fp = open(self.file_name,'r')
        for line in fp:
            line = line[:-1]
            if not self.is_need_process(line):
                continue
            #pv
            (self.total_pv_num[0],self.total_uv_num[0]) = self.process_home(self.total_pv_num[0],self.total_uv_num[0],['get_home=','get_seckill_home='],line)
            (self.total_pv_num[1],self.total_uv_num[1]) = self.process_home(self.total_pv_num[1],self.total_uv_num[1],['get_home='],line)
            (self.total_pv_num[2],self.total_uv_num[2]) =  self.process_home(self.total_pv_num[2],self.total_uv_num[2],['get_seckill_home='],line)
            #clk
            (self.total_clk_pv_num[0],self.total_clk_uv_num[0]) = self.process_clk_total(self.total_clk_pv_num[0],self.total_clk_uv_num[0],-1,line)
            (self.total_clk_pv_num[1],self.total_clk_uv_num[1]) = self.process_clk_total(self.total_clk_pv_num[1],self.total_clk_uv_num[1],0,line)
            (self.total_clk_pv_num[2],self.total_clk_uv_num[2]) = self.process_clk_total(self.total_clk_pv_num[2],self.total_clk_uv_num[2],1,line)
            # pv type
            self.process_ajax_get(line,'get_feed=',self.feed_type_pv_dict,self.feed_type_uv_dict,self.feed_page_pv_dict,self.feed_page_uv_dict)
            self.process_ajax_get(line,'get_seckills=',self.seckill_type_pv_dict,self.seckill_type_uv_dict,self.seckill_page_pv_dict,self.seckill_page_uv_dict)
            # clk type
            self.process_clk_type(line,'top_type',0,self.feed_top_pv_dict,self.feed_top_uv_dict)
            self.process_clk_type(line,'top_type',1,self.seckill_top_pv_dict,self.seckill_top_uv_dict)

            self.process_clk_type(line,'clk_position',0,self.feed_poi_pv_dict,self.feed_poi_uv_dict)

            self.process_clk_type(line,'real_link',0,self.feed_link_pv_dict,self.feed_link_uv_dict)
            self.process_clk_type(line,'real_link',1,self.seckill_link_pv_dict,self.seckill_link_uv_dict)
        fp.close()
        (self.total_keep_num[0],self.total_keep_num[1]) = self.process_keep(['get_home=','get_seckill_home='],self.t_day1,self.c_day)
        (self.feed_keep_num[0],self.feed_keep_num[1]) = self.process_keep(['get_home='],self.t_day1,self.c_day)
        (self.seckill_keep_num[0],self.seckill_keep_num[1]) = self.process_keep(['get_seckill_home='],self.t_day1,self.c_day)

        (self.total_keep_num[2],self.total_keep_num[3]) = self.process_keep(['get_home=','get_seckill_home='],self.t_day2,self.c_day)
        (self.feed_keep_num[2],self.feed_keep_num[3]) = self.process_keep(['get_home='],self.t_day2,self.c_day)
        (self.seckill_keep_num[2],self.seckill_keep_num[3]) = self.process_keep(['get_seckill_home='],self.t_day2,self.c_day)

    def output_uniq_key(self):
        for (key,value) in self.uniq_dict.items():
            print key,value
    def output_file(self,file_name):
        ofp = open(file_name, 'w')
        str = ''
        str = str + '网站总访问pv:%d uv:%d 点击pv:%d 点击uv:%d 点击率:%.3f uv点击率:%.3f\n'%(self.total_pv_num[0],self.total_uv_num[0],self.total_clk_pv_num[0],self.total_clk_uv_num[0],self.total_clk_pv_num[0]/float(self.total_pv_num[0]),self.total_clk_uv_num[0]/float(self.total_uv_num[0]))
        str = str + '优惠推荐总访问pv:%d uv:%d 点击pv:%d 点击uv:%d 点击率:%.3f uv点击率:%.3f\n'%(self.total_pv_num[1],self.total_uv_num[1],self.total_clk_pv_num[1],self.total_clk_uv_num[1],self.total_clk_pv_num[1]/float(self.total_pv_num[1]),self.total_clk_uv_num[1]/float(self.total_uv_num[1]))
        str = str + '限时秒杀总访问pv:%d uv:%d 点击pv:%d 点击uv:%d 点击率:%.3f uv点击率:%.3f\n'%(self.total_pv_num[2],self.total_uv_num[2],self.total_clk_pv_num[2],self.total_clk_uv_num[2],self.total_clk_pv_num[2]/float(self.total_pv_num[2]),self.total_clk_uv_num[2]/float(self.total_uv_num[2]))

        str = str + '网站最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day1,self.total_keep_num[0],self.total_keep_num[1],float(self.total_keep_num[0])/self.total_keep_num[1])
        str = str + '优惠推荐最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day1,self.feed_keep_num[0],self.feed_keep_num[1],float(self.feed_keep_num[0])/self.feed_keep_num[1])
        str = str + '限时秒杀最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day1,self.seckill_keep_num[0],self.seckill_keep_num[1],float(self.seckill_keep_num[0])/self.seckill_keep_num[1])

        str = str + '网站最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day2,self.total_keep_num[2],self.total_keep_num[3],float(self.total_keep_num[2])/self.total_keep_num[3])
        str = str + '优惠推荐最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day2,self.feed_keep_num[2],self.feed_keep_num[3],float(self.feed_keep_num[2])/self.feed_keep_num[3])
        str = str + '限时秒杀最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day2,self.seckill_keep_num[2],self.seckill_keep_num[3],float(self.seckill_keep_num[2])/self.seckill_keep_num[3])

        str = str + '****************分割线*****************************************'  + '\n'

        for (key,value) in self.feed_type_pv_dict.items():
            if key == 1:
                str = str +  '白菜价标签点击pv: %d uv: %d uv占比:%.3f'%(self.feed_type_pv_dict[1],self.feed_type_uv_dict[1],float(self.feed_type_uv_dict[1])/self.total_uv_num[1]) + '\n'
            elif key == 2:
                str = str +  '全网最低标签点击pv: %d uv: %d uv占比:%.3f'%(self.feed_type_pv_dict[2],self.feed_type_uv_dict[2],float(self.feed_type_uv_dict[2])/self.total_uv_num[1]) + '\n'
        sorted_list = sorted(self.feed_page_pv_dict.items(), key=lambda d:d[0],reverse=False)
        for(pn,value) in sorted_list:
            if value > 10:
                str = str +  '优惠推荐第 %d页 pv: %d uv: %d uv占比:%.3f'%(pn,value,self.feed_page_uv_dict[pn],float(self.feed_page_uv_dict[pn])/self.total_uv_num[1]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.seckill_type_pv_dict.items():
            if key == 1:
                str = str +  '限时秒杀 即将开始点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_type_pv_dict[1],self.seckill_type_uv_dict[1],float(self.seckill_type_uv_dict[1])/self.total_uv_num[2]) + '\n'
            elif key == 2:
                str = str +  '限时秒杀 即将结束点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_type_pv_dict[2],self.seckill_type_uv_dict[2],float(self.seckill_type_uv_dict[2])/self.total_uv_num[2]) + '\n'
            elif key == 3:
                str = str +  '限时秒杀 价格排序点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_type_pv_dict[3],self.seckill_type_uv_dict[3],float(self.seckill_type_uv_dict[3])/self.total_uv_num[2]) + '\n'
        sorted_list = sorted(self.seckill_page_pv_dict.items(), key=lambda d:d[0],reverse=False)
        for(pn,value) in sorted_list:
            if value > 10:
                str = str +  '限时秒杀第 %d页 pv: %d uv: %d uv占比:%.3f'%(pn,value,self.seckill_page_uv_dict[pn],float(self.seckill_page_uv_dict[pn])/self.total_uv_num[2]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.feed_top_pv_dict.items():
            if int(key) == 0:
                str = str +  '优惠推荐 非置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.feed_top_pv_dict["0"],self.feed_top_uv_dict["0"],float(self.feed_top_uv_dict["0"])/self.total_clk_uv_num[1]) + '\n'
            elif int(key) == 1:
                str = str +  '优惠推荐 置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.feed_top_pv_dict["1"],self.feed_top_uv_dict["1"],float(self.feed_top_uv_dict["1"])/self.total_clk_uv_num[1]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.feed_poi_pv_dict.items():
            if int(key) == 1:
                str = str +  '优惠推荐 标题点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["1"],self.feed_poi_uv_dict["1"],float(self.feed_poi_uv_dict["1"])/self.total_clk_uv_num[1]) + '\n'
            elif int(key) == 2:
                str = str +  '优惠推荐 图片点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["2"],self.feed_poi_uv_dict["2"],float(self.feed_poi_uv_dict["2"])/self.total_clk_uv_num[1]) + '\n'
            elif int(key) == 3:
                str = str +  '优惠推荐 直达链接点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["3"],self.feed_poi_uv_dict["3"],float(self.feed_poi_uv_dict["3"])/self.total_clk_uv_num[1]) + '\n'
            else:
                str = str +  '优惠推荐 文字链接点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["4"],self.feed_poi_uv_dict["4"],float(self.feed_poi_uv_dict["4"])/self.total_clk_uv_num[1]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.seckill_top_pv_dict.items():
            if int(key) == 0:
                str = str +  '限时秒杀 非置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_top_pv_dict["0"],self.seckill_top_uv_dict["0"],float(self.seckill_top_uv_dict["0"])/self.total_clk_uv_num[2]) + '\n'
            elif int(key) == 1:
                str = str +  '限时秒杀 置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_top_pv_dict["1"],self.seckill_top_uv_dict["1"],float(self.seckill_top_uv_dict["1"])/self.total_clk_uv_num[2]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        #str = str.decode('utf8')
        sorted_list = sorted(self.feed_link_pv_dict.items(), key=lambda d:d[1],reverse=True)
        index = 0
        for(key,value) in sorted_list:
            if index < 40:
                temp_key = unquote(key)
                temp_str = 'feed:%s 点击pv: %d uv: %d\n'%(temp_key,value,self.feed_link_uv_dict[key])
                #temp_str = u'feed: %' +key + u'  点击pv: %d uv: %d'%(value,self.feed_link_uv_dict[key]) + u'\n'
                str = str + temp_str
                index += 1
        str = str + '****************分割线*****************************************\n'
        sorted_list = sorted(self.seckill_link_pv_dict.items(), key=lambda d:d[1],reverse=True)
        index = 0
        for(key,value) in sorted_list:
            if index < 40:
                temp_key = unquote(key)
                temp_str = 'seckill:%s 点击pv: %d uv: %d\n'%(temp_key,value,self.seckill_link_uv_dict[key])
                #temp_str = u'seckill: %' +key + u'  点击pv: %d uv: %d'%(value,self.seckill_link_uv_dict[key]) + u'\n'
                str = str + temp_str
                index += 1
        ofp.write(str)
        ofp.close()
    def output(self):
        str = ''

        str = str + '网站总访问pv:%d uv:%d 点击pv:%d 点击uv:%d 点击率:%.3f uv点击率:%.3f\n'%(self.total_pv_num[0],self.total_uv_num[0],self.total_clk_pv_num[0],self.total_clk_uv_num[0],self.total_clk_pv_num[0]/float(self.total_pv_num[0]),self.total_clk_uv_num[0]/float(self.total_uv_num[0]))
        str = str + '优惠推荐总访问pv:%d uv:%d 点击pv:%d 点击uv:%d 点击率:%.3f uv点击率:%.3f\n'%(self.total_pv_num[1],self.total_uv_num[1],self.total_clk_pv_num[1],self.total_clk_uv_num[1],self.total_clk_pv_num[1]/float(self.total_pv_num[1]),self.total_clk_uv_num[1]/float(self.total_uv_num[1]))
        str = str + '限时秒杀总访问pv:%d uv:%d 点击pv:%d 点击uv:%d 点击率:%.3f uv点击率:%.3f\n'%(self.total_pv_num[2],self.total_uv_num[2],self.total_clk_pv_num[2],self.total_clk_uv_num[2],self.total_clk_pv_num[2]/float(self.total_pv_num[2]),self.total_clk_uv_num[2]/float(self.total_uv_num[2]))

        str = str + '网站最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day1,self.total_keep_num[0],self.total_keep_num[1],float(self.total_keep_num[0])/self.total_keep_num[1])
        str = str + '优惠推荐最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day1,self.feed_keep_num[0],self.feed_keep_num[1],float(self.feed_keep_num[0])/self.feed_keep_num[1])
        str = str + '限时秒杀最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day1,self.seckill_keep_num[0],self.seckill_keep_num[1],float(self.seckill_keep_num[0])/self.seckill_keep_num[1])

        str = str + '网站最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day2,self.total_keep_num[2],self.total_keep_num[3],float(self.total_keep_num[2])/self.total_keep_num[3])
        str = str + '优惠推荐最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day2,self.feed_keep_num[2],self.feed_keep_num[3],float(self.feed_keep_num[2])/self.feed_keep_num[3])
        str = str + '限时秒杀最近%d天内活跃用户数:%d, 总用户数:%d, 比例:%.4f\n'%(self.t_day2,self.seckill_keep_num[2],self.seckill_keep_num[3],float(self.seckill_keep_num[2])/self.seckill_keep_num[3])
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.feed_type_pv_dict.items():
            if key == 1:
                str = str +  '白菜价标签点击pv: %d uv: %d uv占比:%.3f'%(self.feed_type_pv_dict[1],self.feed_type_uv_dict[1],float(self.feed_type_uv_dict[1])/self.total_uv_num[1]) + '\n'
            elif key == 2:
                str = str +  '全网最低标签点击pv: %d uv: %d uv占比:%.3f'%(self.feed_type_pv_dict[2],self.feed_type_uv_dict[2],float(self.feed_type_uv_dict[2])/self.total_uv_num[1]) + '\n'
        sorted_list = sorted(self.feed_page_pv_dict.items(), key=lambda d:d[0],reverse=False)
        for(pn,value) in sorted_list:
            if value > 10:
                str = str +  '优惠推荐第 %d页 pv: %d uv: %d uv占比:%.3f'%(pn,value,self.feed_page_uv_dict[pn],float(self.feed_page_uv_dict[pn])/self.total_uv_num[1]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.seckill_type_pv_dict.items():
            if key == 1:
                str = str +  '限时秒杀 即将开始点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_type_pv_dict[1],self.seckill_type_uv_dict[1],float(self.seckill_type_uv_dict[1])/self.total_uv_num[2]) + '\n'
            elif key == 2:
                str = str +  '限时秒杀 即将结束点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_type_pv_dict[2],self.seckill_type_uv_dict[2],float(self.seckill_type_uv_dict[2])/self.total_uv_num[2]) + '\n'
            elif key == 3:
                str = str +  '限时秒杀 价格排序点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_type_pv_dict[3],self.seckill_type_uv_dict[3],float(self.seckill_type_uv_dict[3])/self.total_uv_num[2]) + '\n'
        sorted_list = sorted(self.seckill_page_pv_dict.items(), key=lambda d:d[0],reverse=False)
        for(pn,value) in sorted_list:
            if value > 10:
                str = str +  '限时秒杀第 %d页 pv: %d uv: %d uv占比:%.3f'%(pn,value,self.seckill_page_uv_dict[pn],float(self.seckill_page_uv_dict[pn])/self.total_uv_num[2]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.feed_top_pv_dict.items():
            if int(key) == 0:
                str = str +  '优惠推荐 非置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.feed_top_pv_dict["0"],self.feed_top_uv_dict["0"],float(self.feed_top_uv_dict["0"])/self.total_clk_uv_num[1]) + '\n'
            elif int(key) == 1:
                str = str +  '优惠推荐 置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.feed_top_pv_dict["1"],self.feed_top_uv_dict["1"],float(self.feed_top_uv_dict["1"])/self.total_clk_uv_num[1]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.feed_poi_pv_dict.items():
            if int(key) == 1:
                str = str +  '优惠推荐 标题点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["1"],self.feed_poi_uv_dict["1"],float(self.feed_poi_uv_dict["1"])/self.total_clk_uv_num[1]) + '\n'
            elif int(key) == 2:
                str = str +  '优惠推荐 图片点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["2"],self.feed_poi_uv_dict["2"],float(self.feed_poi_uv_dict["2"])/self.total_clk_uv_num[1]) + '\n'
            elif int(key) == 3:
                str = str +  '优惠推荐 直达链接点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["3"],self.feed_poi_uv_dict["3"],float(self.feed_poi_uv_dict["3"])/self.total_clk_uv_num[1]) + '\n'
            else:
                str = str +  '优惠推荐 文字链接点击pv: %d uv: %d uv占比:%.3f'%(self.feed_poi_pv_dict["4"],self.feed_poi_uv_dict["4"],float(self.feed_poi_uv_dict["4"])/self.total_clk_uv_num[1]) + '\n'
        str = str + '****************分割线*****************************************'  + '\n'
        for (key,value) in self.seckill_top_pv_dict.items():
            if int(key) == 0:
                str = str +  '限时秒杀 非置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_top_pv_dict["0"],self.seckill_top_uv_dict["0"],float(self.seckill_top_uv_dict["0"])/self.total_clk_uv_num[2]) + '\n'
            elif int(key) == 1:
                str = str +  '限时秒杀 置顶结果点击pv: %d uv: %d uv占比:%.3f'%(self.seckill_top_pv_dict["1"],self.seckill_top_uv_dict["1"],float(self.seckill_top_uv_dict["1"])/self.total_clk_uv_num[2]) + '\n'
        '''str = str + '****************分割线*****************************************'  + '\n'
        #str = str.decode('utf8')
        sorted_list = sorted(self.feed_link_pv_dict.items(), key=lambda d:d[1],reverse=True)
        index = 0
        for(key,value) in sorted_list:
            if index < 40:
                temp_key = unquote(key)
                temp_str = 'feed:%s 点击pv: %d uv: %d\n'%(temp_key,value,self.feed_link_uv_dict[key])
                #temp_str = u'feed: %' +key + u'  点击pv: %d uv: %d'%(value,self.feed_link_uv_dict[key]) + u'\n'
                str = str + temp_str
                index += 1
        str = str + '****************分割线*****************************************\n'
        sorted_list = sorted(self.seckill_link_pv_dict.items(), key=lambda d:d[1],reverse=True)
        index = 0
        for(key,value) in sorted_list:
            if index < 40:
                temp_key = unquote(key)
                temp_str = 'seckill:%s 点击pv: %d uv: %d\n'%(temp_key,value,self.seckill_link_uv_dict[key])
                #temp_str = u'seckill: %' +key + u'  点击pv: %d uv: %d'%(value,self.seckill_link_uv_dict[key]) + u'\n'
                str = str + temp_str
                index += 1'''
        return str

if __name__ == "__main__":
    my_stat = Stat(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    my_stat.process()
    out_str =  my_stat.output()
    file_name = 'stat_file.' + sys.argv[2] + '.txt'
    my_stat.output_file(file_name)
    print out_str
    st = SendTools('1111111','ops@maimiaotech.com','maimiaoops2013')
    subject = 'ztmhs数据统计' + sys.argv[2]
    address = '2c@maimiaotech.com'
    #address = 'gaonan@maimiaotech.com'
    #import pdb
    #pdb.set_trace()
    #st.send_email_with_text(addressee, out_str, subject)
    st.send_email_with_file(address,out_str,subject,[file_name])