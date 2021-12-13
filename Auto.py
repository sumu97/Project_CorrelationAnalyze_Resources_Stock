import time
import schedule

def job():
    exec(open("data_resources.py").read())
    #print('wow')

schedule.every().day.at('00:00').do(job) # 매일 00:00 실행 data_resources.py
#schedule.every(1).seconds.do(job) 

while True:
    schedule.run_pending()
    #print('running')
    time.sleep(1)


# Err : AttributeError: partially initialized module 'schedule' has no attribute 'every' (most likely due to a circular import)
# 원인 : schedule.py 라고 이름을 지어버리면 에러가 발생