"""[Parameters for this file]"""

start_date = "2016/12/08"
end_date = "2021/12/08" # 2일 이전까지는 가능함
Frequency = "Daily" # "Weekly"

"""--------------------------"""

import requests, re, time
from bs4 import BeautifulSoup
import pandas as pd
import datetime

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'X-Requested-With' : 'XMLHttpRequest'
}

# Raw 문자열 생성 (R String)
url = r"https://kr.investing.com/commodities/real-time-futures"
baseURL = r"https://kr.investing.com"

''' 1. 원자재 리스트 뽑기 '''
commodities = [] # 원자재 리스트

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

commodityDiv = soup.find('div', {'id': 'cross_rates_container'})

for a_tag in commodityDiv.find('tbody').find_all('a'):
    href = a_tag.get("href") # ex) /commodities/gold
    title = a_tag.get("title") # ex) 금 선물
    
    if "commodities" in href:
        commodities.append((baseURL + href, title)) # url, title 튜플로 저장

#for i,l in commodities:
#    print(i,l)
#commodities 의 각 값을 가져와서 데이터베이스에 추가하는 함수 필요




''' 2. 각 히스토리컬 데이터 접근을 위한 curr_id와 smlID를 추출 '''


ids = []

for URL, _ in commodities:
    historicalURL = URL + "-historical-data"
    response = requests.get(historicalURL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    for script in soup.findAll('script'):
        if script.string and "window.histDataExcessInfo" in script.string:
            histData = script.string.strip().replace("\n", "").replace(" ", "")
            print(historicalURL)
            curr_id = re.findall("\d+", histData)[0]
            smlId = re.findall("\d+", histData)[1]
            ids.append((curr_id, smlId)) # 투플로 저장
                    
    #break # Debug 용도.. 긴 한데 안풀어도 정상작동 할듯? -> 응아니야~
    time.sleep(0.01)



''' 3. HistoricalDataAjax 5년치 데이터를 추출 '''
# 현재일로부터 천천히 바꾸는걸로 ...
formData = {
    "curr_id" : "",
    "smlID" : "",
    "header" : "",
    "st_date" : start_date,
    "end_date" : end_date,
    "interval_sec" : Frequency,
    "sort_col" : "date",
    "sort_ord" : "DESC",
    "action" : "historical_data"
}

POSTURL = r"https://kr.investing.com/instruments/HistoricalDataAjax"

""" 3. 데이터 랭글링 """
for (_, title), (curr_id, smlID) in zip(commodities, ids):
    formData["curr_id"] = curr_id
    formData["smlID"] = smlID
    formData["header"] = title + " 내역"
    
    response = requests.post(POSTURL, headers=headers, data=formData)
    #f = open(title, "w")
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    tr = soup.find_all('tr')
    list_data = []
    for t in tr[1:-1]:
        temp_list = []
        #print(t)
        d = t.find(class_="first left bold noWrap")
        #print(d.text) # 날짜 텍스트
        date_text = d.text
        date_text = date_text.replace('년','')
        date_text = date_text.replace('월','')
        date_text = date_text.replace('일','')
        date_text = date_text.replace(' ','/')
        date_text = datetime.datetime.strptime(date_text, '%Y/%m/%d').date()
        temp_list.append(date_text) # 정제된 Date 를 리스트에 추가

        s = t.find(class_="redFont")
        try:
            #print(s.text) # 가격 텍스트
            temp = s.text.replace(',','') # ',' 때문에 float 안되서 추가
            temp_list.append(float(temp)) # interpolate 안되서 float 화 추가
        except:
            s = t.find(class_="greenFont")
            #print(s.text) # 가격 텍스트
            temp = s.text.replace(',','')
            temp_list.append(float(temp))
        list_data.append(temp_list)
        #print("###single T has done###")
    #print(list_data,title)
    df_temp = pd.DataFrame(list_data, columns=['Date','Price' + '_' + title])
    df_temp.set_index(df_temp.Date,inplace=True)
    del df_temp['Date']
    #print(df_temp)
    #print(df_temp.index)
    #print(df_temp.columns)
    #print(title)
    if title == '금 선물':
        gold = df_temp.copy()
        print('gold worked')
    elif title == '은 선물':
        silv = df_temp.copy()
        print('silv worked')
    elif title == '구리 선물':
        copr = df_temp.copy()
        print('copr worked')
    elif title == '백금 선물':
        plat = df_temp.copy()
        print('plat')
    elif title == '팔라듐 선물':
        plad = df_temp.copy()
        print('plad')
    elif title == 'WTI유 선물':
        wtio = df_temp.copy()
        print('wtio')
    elif title == '브렌트유 선물':
        brto = df_temp.copy()
        print('brto')
    elif title == '천연가스 선물':
        ngas = df_temp.copy()
        print('ngas')
    elif title == '난방유 선물':
        hoil = df_temp.copy()
        print('hoil')
    elif title == '가솔린 RBOB 선물':
        gsol = df_temp.copy()
        print('gsol')
    elif title == '런던 가스 오일 선물':
        lgas = df_temp.copy()
        print('lgas')
    elif title == '알미늄':
        alum = df_temp.copy()
        print('alum')
    elif title == '아연 선물':
        ayen = df_temp.copy()
        print('ayen')
    elif title == '납 선물':
        napp = df_temp.copy()
        print('napp')
    elif title == '니켈 선물':
        nikl = df_temp.copy()
        print('nikl')
    elif title == '주석 선물':
        ston = df_temp.copy()
        print('ston')
    elif title == '미국 소맥 선물':
        mack = df_temp.copy()
        print('mack')
    elif title == '현미 선물':
        seed = df_temp.copy()
        print('seed')
    elif title == '미국 옥수수 선물':
        corn = df_temp.copy()
        print('corn')
    elif title == '미국 대두 선물':
        bean = df_temp.copy()
        print('bean')
    elif title == '미국 대두유 선물':
        beol = df_temp.copy()
        print('beol')
    elif title == '미국 대두박 선물':
        bebk = df_temp.copy()
        print('bebk')
    elif title == '미국 원면 No.2 선물':
        silk = df_temp.copy()
        print('silk')
    elif title == '미국 코코아 선물':
        coco = df_temp.copy()
        print('coco')
    elif title == '미국 커피 C 선물':
        uscp = df_temp.copy()
        print('uscp')
    elif title == '런던 커피 선물':
        ldcp = df_temp.copy()
        print('ldcp')
    elif title == '미국 설탕 No.11 ':
        ussg = df_temp.copy()
        print('ussg')
        # 에러 발생
    elif title == '오렌지 주스 선물':
        orjs = df_temp.copy()
        print('orjs')
    elif title == '생우 선물':
        licw = df_temp.copy()
        print('licw')
    elif title == '돈육 선물':
        pgmt = df_temp.copy()
        print('pgmt')
        # 에러 발생
    elif title == '육우 선물':
        cwmt = df_temp.copy()
        print('cwmt')
        # 에러 발생
    elif title == '원목':
        wood = df_temp.copy()
        print('wood')
        # 에러 발생
    elif title == '귀리 선물':
        giri = df_temp.copy()
        print('giri')
        # 에러 발생
    else:
        print("먼가.. 먼가 ㅈ됬음....")
    # 데이터프레임으로 먼저 완성하고, DB에 적용하는거로. (결측치 다수)



    #price = soup.find('tr')
    #print(price)
    #list 형태로 HTML 바꿔줘야 데이터베이스 넣기 쉬움
    # 날짜 / 가격 / 변동 으로 (변동은 빼도 됨)


    #titles = table.select('tbody > tr > td > first left bold noWrap')
    #for title in titlese:
    #    print(title.get_text())
    
    #print(soup)
    #f.write(response.text)
    #f.close()
    
    time.sleep(0.01)
    #break # Debug 용도
#print('GOLD',gold)
#print('SILV',silv)
#df1 = pd.merge(gold,silv,copr,plat,plad,wtio,brto,ngas,how='outer')
#df2 = pd.merge(hoil,gsol,lgas,alum,ayen,napp,nikl,ston,how='outer')
#df3 = pd.merge(mack,seed,corn,bean,beol,bebk,silk,coco,how='outer')
#df4= pd.merge(uscp,ldcp,ussg,orjs,licw,pgmt,cmt,wood,giri,how='outer')
#df = pd.merge(gold,silv,copr,plat,plad,wtio,brto,ngas,hoil,gsol,lgas,alum,ayen,napp,nikl,ston,mack,seed,corn,bean,beol,bebk,silk,coco,uscp,ldcp,ussg,orjs,licw,pgmt,cwmt,wood,giri,how='outer')
#print(gold,silv,copr,plat,plad,wtio,brto,ngas,hoil,gsol,lgas,alum,ayen,napp,nikl,ston,mack,seed,corn,bean,beol,bebk,silk,coco,uscp,ldcp,orjs,licw)

df = gold.join(silv,how='outer').join(copr, how='outer').join(plat, how='outer').join(plad, how='outer').join(wtio, how='outer').join(brto, how='outer').join(ngas, how='outer').join(hoil, how='outer').join(gsol, how='outer').join(lgas, how='outer').join(alum, how='outer').join(ayen, how='outer').join(napp, how='outer').join(nikl, how='outer').join(ston, how='outer').join(mack, how='outer').join(seed, how='outer').join(corn, how='outer').join(bean, how='outer').join(beol, how='outer').join(bebk, how='outer').join(silk, how='outer').join(coco, how='outer').join(uscp, how='outer').join(ldcp, how='outer').join(orjs, how='outer').join(licw, how='outer')
print(df)

df = df.interpolate()

print('\n','[Duplicated check]','\n')
df.T.duplicated()

# 왜 멀지가 안되는건지 멀르겠지
# 데이터가 빠져있는데 joIN을 하니 될리가 있나..

"""데이터를 SQLite DB에 저장하기"""
import sqlite3
import os
db_path = os.getcwd() + "/data.db" # db 경로
con = sqlite3.connect(db_path)
try: # 테이블 드랍, 테이블 생성
    cur = con.cursor()
    query = "drop table resources"
    cur.execute(query)
    df.to_sql('resources', con)
except: # 테이블 드랍 안되면(테이블 없으면) 테이블 생성
    df.to_sql('resources', con)
