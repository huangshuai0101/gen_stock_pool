import json
import urllib.request
import requests
import csv
import xml.dom.minidom
import sys
import openpyxl
from openpyxl.styles import Font
import tushare as ts
#import pudb; pu.db



## sample data:
## var bDQXYwir = {pages:1,data:[{"SCode":"603331"

link_found_add = '''http://data.eastmoney.com/zlsj/zlsj_list.aspx?type=ajax&st=6&sr=-1&p=1&ps=3500&jsObj=aJlEvHvx&stat=1&cmd=1&date=2017-12-31'''

tmpstr = '''{"pages":1,"data":'''
endstr = '''}'''

def get_found_json(url):
    wp = urllib.request.urlopen(url)
    data = wp.read().decode("gbk")

    start_pos = data.index('[')
    end_pos = data.index('dataUrl')
    json_data = tmpstr+ data[start_pos + 0:end_pos-1] +endstr
    #print(json_data)
    with open('found_add.json','w',encoding='utf-8') as f:
        f.write(json_data)

    dict = json.loads(json_data)
    return dict

##sample data:
## var wCrEHHpy={"success":true,"pages":1,"data":[{"SecurityCode":"300626"

link_min = '''http://data.eastmoney.com/DataCenter_V3/gdhs/GetList.ashx?reportdate=&market=&changerate=<0&range==&pagesize=3500&page=1&sortRule=-1&sortType=NoticeDate'''
def test_session(url):
    s = requests.Session()
    data = s.get(url)
    text = data.text
    #start_pos = text.index('=')
    #json_data = text[start_pos+1:]
    json_data = text
    #print(json_data)
    with open('holding_dec.json','w',encoding='utf-8') as f:
        f.write(json_data)
    dict = json.loads(json_data)
    return dict

d = get_found_json(link_found_add)
l = d['data']
print("基金增仓数量3000：",len(l))

num = test_session(link_min)
num_list = num['data']
#pprint(num_list)
print("股东人数减少2000：",len(num_list))

'''增仓比例   RateChange             && 
   流通占比   LTZB >5 '''

#持股比例大于5，并且增仓的.
ltzb = 5
add_percent = 5
holdingValue = 100000000

result = []
ltzb5plus = []
addrate=[]
yi=[]
good = []
for s in l:
    if s['LTZB'] > ltzb:
        #ltzb5plus.append(int(s['SCode']))
        ltzb5plus.append((s['SCode']))
    if s['RateChange'] > add_percent:
	    addrate.append((s['SCode']))
    if s['VPosition'] > holdingValue:
	    yi.append((s['SCode']))
for i in ltzb5plus:
    if i in addrate:
        if i in yi:
            result.append(i)	

for s in l:
    if s['VPosition'] > holdingValue*3:
        if s['RateChange'] > add_percent*7:
            good.append(s['SCode'])
	
#print(result)
print("add > 5%:",len(addrate))
print("ltzb > 5%:",len(ltzb5plus))
print("value > 1亿:",len(yi))
print("增仓", len(result))
print("持股3亿并且增仓35%以上",len(good))


dec_percent = -5

result2 = []
for n in num_list:
    x = n['HolderNumChangeRate']
    if (x != "" and float(x) <= dec_percent): #15
            result2.append((n['SecurityCode']))

print("dec < -5%:",len(result2))

finalresult = []
for s in result:
    for n in result2:
        if s == n:
            finalresult.append(s)

print("all:",len(finalresult))



'''write data to csv'''

def write(name,list):
    with open(name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerows(map(lambda x: [x], list))

write('inc.txt',result)
write('dec.txt',result2)
write('fin.txt',finalresult)

write('流通占比超过5%.txt',ltzb5plus)
write('持股大于1亿.txt',yi)
write('增仓大于5%.txt',addrate)
write('持股3亿并且增仓35%以上.txt',good)

## get basic information
info = ts.get_stock_basics()
ind = info['industry']

'''{"SCode":"601318","SName":"中国平安","RDate":"\/Date(1514649600000)\/","LXDM":"基金","LX":"1","Count":868,"CGChange":"增持","ShareHDNum":704730584,"VPosition":49317046268.32,"TabRate":3.85514919,"LTZB":6.50560691999999,"ShareHDNumChange":76644912,"RateChange":12.2029390920416}'''

wb = openpyxl.Workbook()
sheet = wb.get_active_sheet()
sheet.title = "股票池"

sheet.freeze_panes = 'A2'

sheet['A1'] = "代码"
sheet['B1'] = "名称"
sheet['C1'] = "变化"
sheet['D1'] = "流通占比"
sheet['E1'] = "金额(亿元)"
sheet['F1'] = "增加百分比(%)"
sheet['G1'] = "基金家数"
sheet['H1'] = "股东减少%"
sheet['I1'] = "股东减少人数"
sheet['J1'] = "股东更新日期"
sheet['K1'] = "行业"
sheet.column_dimensions['J'].width = 20
sheet.column_dimensions['F'].width = 20
sheet.column_dimensions['K'].width = 20

for i in range(1,len(l)):
    sheet["A%d" %(1+i)].value= l[i]['SCode']
    sheet["B%d" %(1+i)].value= l[i]['SName']
    sheet["C%d" %(1+i)].value= l[i]['CGChange']
    sheet["D%d" %(1+i)].value= l[i]['LTZB']
    sheet["E%d" %(1+i)].value= l[i]['VPosition']/100000000
    sheet["F%d" %(1+i)].value= l[i]['RateChange']
    sheet["G%d" %(1+i)].value= l[i]['Count']
    for n in num_list:
        x = n['HolderNumChangeRate']
        y = n['HolderNumChange']
        date = n['NoticeDate']
        if l[i]['SCode'] == n['SecurityCode']:
            sheet["H%d" %(1+i)].value= x
            sheet["I%d" %(1+i)].value= y
            sheet["J%d" %(1+i)].value= date
    for x in info:
        if l[i]['SCode'] == x[0]:
            sheet["K%d" %(1+i)].value= x[2]

wb.save('股票池.xlsx')
