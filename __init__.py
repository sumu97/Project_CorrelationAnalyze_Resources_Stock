from flask import Flask, request, render_template
import FinanceDataReader as fdr
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
from urllib import parse

@app.route('/') # 루트주소 (/) 에 접속했을때 실행하세용 / URL 에 따라 실행할 함수 지정
def index():
    return '''
     <html>
      <head>
        <title>
          HTML Page
        </title>
      </head>
      <body>
        <form name = "get_search" action = "/search" method = "get">
        <h1><주식-원자재> 상관관계 분석</h1>
        다음 정보를 입력하세요<br/>
        궁금한 주식 : <input type = 'text' name = 'stock' size = "10"> <input type = "submit" value = "확인">
      </body>
     </html>
     '''

@app.route('/search',methods=['GET'])
def search():
    a = request.args.get('stock')

    """3. SQLite3 데이터 가져오기 - krx"""
    import pandas as pd
    import sqlite3
    import os
    db_path = os.getcwd() + "/data.db" # db 경로
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    name = "'%" + a + "%'"
    query = cur.execute(f"SELECT Symbol,Name FROM krx WHERE name LIKE {name}")
    cols = [column[0] for column in query.description]
    df_krx = pd.DataFrame.from_records(data=query.fetchall(), columns = cols)
    con.close()
    return render_template('main.html') + df_krx.to_html()

@app.route('/result',methods=['GET'])
def result():
    b = request.args.get('Symbol')
    """1. 주식 데이터 뽑기"""
    df_stock = fdr.DataReader(symbol=b,start='20161208',end='20211208')

    """2. SQLite3 데이터 가져오기 - resources"""
    import pandas as pd
    import sqlite3
    import os
    db_path = os.getcwd() + "/data.db" # db 경로
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    query = cur.execute("SELECT * FROM resources")
    cols = [column[0] for column in query.description]
    df_resources = pd.DataFrame.from_records(data=query.fetchall(), columns = cols)
    df_resources['Date'] = pd.to_datetime(df_resources['Date'], format='%Y-%m-%d', errors='raise')
    df_resources.set_index(df_resources.Date,inplace=True)
    df_resources.drop(['Date'],axis=1, inplace=True)
    con.close()

    """3. Resources + Stock"""
    df_merge = pd.merge(df_resources,df_stock.Close, how='outer',on='Date')
    df = df_merge.interpolate()

    """4. 특성중요도 뽑기"""
    target = 'Close'
    features = df.drop(columns=[target]).columns
    X_train = df[features]
    y_train = df[target]
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
    #plt.show()

    return plt.show()




    """ UnicodeEncodeError: 'ascii' codec can't encode characters in position 11-12: ordinal not in range(128)
    html = df_krx.to_html()
    print(type(html))
    html = html.encode('utf-8')
    print(type(html))
    return f'검색 : {a}',f'결과 : {html}'
    """

if __name__ == "__main__":
    app.run(debug=True)