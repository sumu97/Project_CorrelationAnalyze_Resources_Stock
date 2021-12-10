"""SQLite DB 생성 파일"""

import sqlite3
import os

# 현재 파일 이름, 파일 경로
print(__file__)
print(os.path.realpath(__file__))
print(os.path.abspath(__file__))

# 현재 파일의 디렉토리(폴더) 경로
print(os.getcwd())
print(os.path.dirname(os.path.realpath(__file__)) )

# 현재 디렉토리에 있는 파일 리스트
print(os.listdir(os.getcwd()))

# 작업 디렉토리 변경

print("before: %s"%os.getcwd())
os.chdir("C:\Users\dbxow\code") # 해당 디렉토리
print("after: %s"%os.getcwd())