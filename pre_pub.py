#coding=utf-8
import datetime
import pymongo

def change_stat():
    connection = pymongo.Connection('localhost', 27017)
    db = connection['scrapy']
    cur_date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    items = db['ztmhs'].find({'stat':5,'pre_pub_time':{"$lte":cur_date_str}})
    count = 0
    for item in items:
        save_dict={}
        save_dict['stat'] = 1
        save_dict['pub_time'] = item['pre_pub_time']
        db['ztmhs'].update({'id': item['id']}, { '$set': dict(save_dict) },upsert=True, safe=True)
        count += 1
    print cur_date_str,"change number:",count
if __name__ == "__main__":
    change_stat()