"""1. 국내 주식 테이블 생성"""
# 이름으로 검색하면 관련된걸 HTML에 쫙 뿌려주고, Symbol 입력 받아야 함.
import FinanceDataReader as fdr
from pandas.core.indexes.base import InvalidIndexError

krx = fdr.StockListing('KRX')

columns = ['Symbol', 'Market', 'Name', 'Sector', 'Industry','ListingDate']
marketFilter = (krx['Market'] == 'KOSPI') | (krx['Market'] == 'KOSDAQ')
dateFilter = (krx['ListingDate'] <= '2010-01-01')
krx = krx[marketFilter & dateFilter][columns]
#print(krx)
#print(type(krx)) # 개꿀 데이터프레임이네?

import sqlite3
import os
db_path = os.getcwd() + "/data.db" # db 경로
con = sqlite3.connect(db_path)
cur = con.cursor()
try: # 테이블 드랍, 테이블 생성
    query = "drop table krx"
    cur.execute(query)
    krx.to_sql('krx', con)
except: # 테이블 드랍 안되면(테이블 없으면) 테이블 생성
    krx.to_sql('krx', con)

"""2. SQLite3 데이터 가져오기 - resources"""
import pandas as pd
query = cur.execute("SELECT * FROM resources")
cols = [column[0] for column in query.description]
df_resources = pd.DataFrame.from_records(data=query.fetchall(), columns = cols)
df_resources['Date'] = pd.to_datetime(df_resources['Date'], format='%Y-%m-%d', errors='raise')
df_resources.set_index(df_resources.Date,inplace=True)
df_resources.drop(['Date'],axis=1, inplace=True)
#con.close()

print(df_resources)

"""3. SQLite3 데이터 가져오기 - krx"""
import pandas as pd
name = "'%" + '흥국' + "%'"
#print(name)
#query_str = f"SELECT Symbol,Name FROM krx WHERE name LIKE {name}"
#print(query_str)
query = cur.execute(f"SELECT Symbol,Name FROM krx WHERE name LIKE {name}")
cols = [column[0] for column in query.description]
df_krx = pd.DataFrame.from_records(data=query.fetchall(), columns = cols)
#con.close()

print(df_krx)

"""1. 국내 주식 가격 확인"""
# 이름으로 검색하면 관련된걸 HTML에 쫙 뿌려주고, Symbol 입력 받아야 함.
"""
input = '흥국'
#input = '%' + input + '%'
import pandas as pd
query = cur.execute("SELECT Symbol FROM krx WHERE Name = {}".format(input))
cols = [column[0] for column in query.description]
df_search = pd.DataFrame.from_records(data=query.fetchall(), columns = cols)
print(df_search)
#cols = [column[0] for column in query.description]
#df_stock = pd.DataFrame.from_records(data=query.fetchall(), columns = cols)

"""
#krx = fdr.StockListing('KRX')


#columns = ['Symbol', 'Market', 'Name', 'Sector', 'Industry','ListingDate']
#marketFilter = (krx['Market'] == 'KOSPI') | (krx['Market'] == 'KOSDAQ')
#dateFilter = (krx['ListingDate'] <= '2010-01-01')
#krx = krx[marketFilter & dateFilter][columns]
#print(krx)
#print(type(krx)) # 개꿀 데이터프레임이네?

"""2. 상관관계 분석"""
import pandas as pd
import numpy as np
"""
commodity = pd.read_excel('CMOHistoricalDataMonthly.xlsx', sheet_name="Monthly Prices", header=4)
commodity.drop([0, 1], inplace=True) # 불필요한 행 삭제
commodity.rename(columns = {'Unnamed: 0' : 'Date'}, inplace=True) # column 이름을 date로 변경

# 2010년 이후로만 분석한다
monthFilter = (df_resources['Date'] >= '2010')
commodity = df_resources[monthFilter]

# 데이터를 숫자로 변환 시킨 뒤 Nan 열 삭제 
coe = pd.DataFrame(columns=commodity.columns)
print(coe)
"""

"""3. 주식 데이터 뽑기"""
df_stock = fdr.DataReader(symbol='000540',start='20161208',end='20211208')
print(df_stock.Close)

print(df_resources.index)
#df_stock = df_stock.rename(index='Date')
#print(df_resources.columns)
print(df_stock.index)
"""4. Resources + Stock"""
df_merge = pd.merge(df_resources,df_stock.Close, how='outer',on='Date')
df = df_merge.interpolate()
print(df)

"""4. 특성중요도 뽑기"""
# 기존 모델 (RandomForestClassifier) 학습 
target = 'Close'
features = df.drop(columns=[target]).columns
X_train = df[features]
y_train = df[target]

""" Classifier 모델로는 분석 불가 : ValueError: Unknown label type: 'continuous'
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from category_encoders import OrdinalEncoder
pipe = make_pipeline(
    OrdinalEncoder(),  
    SimpleImputer(), 
    RandomForestClassifier(n_jobs=-1, max_depth=25, min_samples_leaf=3, random_state=2, oob_score=True)
)

pipe.fit(X_train, y_train)
print('훈련 정확도: ', pipe.score(X_train, y_train))
"""
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from scipy.stats import randint, uniform
from category_encoders import TargetEncoder
from sklearn.ensemble import RandomForestRegressor

pipe = make_pipeline(
    TargetEncoder(min_samples_leaf=1,smoothing=50), 
    SimpleImputer(strategy='mean'), 
    RandomForestRegressor(max_depth=10, max_features=0.95,n_estimators=300)
)

pipe.fit(X_train, y_train);
print('훈련 정확도: ', pipe.score(X_train, y_train)) #원래는 특성공학, 이것저것 해야되지만 일단 특성중요도만 궁금하기때문에

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
font_path = "C:/Windows/Fonts/NGULIM.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

model_rfr = pipe.named_steps['randomforestregressor']

importances = pd.Series(model_rfr.feature_importances_, X_train.columns)
plt.figure(figsize=(10,30))
importances.sort_values().plot.barh();
plt.show()