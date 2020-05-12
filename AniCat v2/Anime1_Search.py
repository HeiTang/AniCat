#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests , mysql.connector
from bs4 import BeautifulSoup

# Connect MySQL
mydb = mysql.connector.connect(
  host = "127.0.0.1",    # DB 主機位置
  user = "root",         # DB 用戶名
  password = "1234567890", # DB 密碼
  database = "Anime1_DB",
  )

cursor=mydb.cursor()

# def Create_Database():
#   cursor.execute("CREATE DATABASE Anime1_db")

# def Create_Table():
#   cursor.execute("CREATE TABLE Anime1 (Name VARCHAR(255), ID INTEGER(99), Key_id INT AUTO_INCREMENT PRIMARY KEY)")

# ====================================================================================================

# 在DB中搜尋MAXID
def Search_Max_id(): 
  sql = "SELECT MAX(ID) FROM Anime1" 

  cursor.execute(sql)

  Max_id = cursor.fetchone()[0]

  Create_DB(Max_id)

# 更新DB
def Create_DB(i):
  count = 0
  while True:
    i = i+1
    
    url = "https://anime1.me?cat="+str(i)

    # print(i,end=' ')

    r = requests.get(url) 

    soup = BeautifulSoup(r.text, 'html.parser')

    h1_tag = soup.find_all("h1", class_="page-title")

    # print(h1_tag[0].string,end=' ')

    if(h1_tag[0].string == "Oops！找不到這個頁面！"):
        count = count +1
    else:
        count = 0
        sql = "INSERT INTO Anime1 (Name, ID) VALUES (%s, %s)"
        val = (h1_tag[0].string, i)

        cursor.execute(sql, val)
        mydb.commit()    # 資料表内容若有更新，必須使用到該語句
        print(cursor.rowcount, "紀錄插入成功。")  

    if(count == 5):
      print("        ➠ \033[1;33m 更新完畢！ \033[0m")
      break

# ====================================================================================================

# 在DB中搜尋AnimeID
def Search_Anime1_id(Keyword):
    sql = "SELECT Name,ID FROM Anime1 WHERE Name LIKE '%" + Keyword + "%'"
  
    cursor.execute(sql)
  
    result = cursor.fetchall()
  
    data={}
    
    for x in result:
        data.setdefault( x[0], x[1] )
        # print(data)
    return data

# if __name__ == '__main__': 
#   Create_DB(0)

