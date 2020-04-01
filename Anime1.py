#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests,os,sys
import datetime
import json
import Upload , Database
from bs4 import BeautifulSoup
from urllib.parse import unquote
from itertools import cycle 
from time import sleep

# 設定 Header 
headers = {
    "Accept": "*/*",
    "Accept-Language": 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    "DNT": "1",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "cookie": "__cfduid=d8db8ce8747b090ff3601ac6d9d22fb951579718376; _ga=GA1.2.1940993661.1579718377; _gid=GA1.2.1806075473.1579718377; _ga=GA1.3.1940993661.1579718377; _gid=GA1.3.1806075473.1579718377",
    "Content-Type":"application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3573.0 Safari/537.36",
    }

# 設定 Anime1.me 的驗證密碼
data = {
    "acpwd-pass": "anime1.me"
}

def Anime_title(url):
    r = requests.post(url,headers = headers,data = data)
    soup = BeautifulSoup(r.text, 'lxml')
    # 取得動漫標題
    Anime_Groups_title = soup.find("h1" , class_="page-title")
    Anime_Groups_title = str(Anime_Groups_title.text)
    return Anime_Groups_title
    

def Anime_Groups(url):
    Anime_Unit_title = []
    Anime_Unit_URL = []

    r = requests.post(url,headers = headers,data = data)
    soup = BeautifulSoup(r.text, 'lxml')

    # 獲取A所有集數連結
    h2_tag = soup.find_all("h2" , class_="entry-title")
    for i in range(len(h2_tag)):
        # 取得第i集的標題
        Anime_Unit_title.append(h2_tag[i].text)
        # 取得第i集的連結
        a_tag = h2_tag[i].find("a")
        Anime_Unit_URL.append(a_tag.get('href'))

    return Anime_Unit_URL , Anime_Unit_title


def Anime_Unit(url):
    r = requests.post(url,headers = headers,data = data)
    soup = BeautifulSoup(r.text, 'lxml') 

    try:
        return Anime_m3u8(soup)
    except:
        return Anime_mp4(soup)


def Anime_m3u8(anime):
    # 取得第i集的 .m3u8
    button_tag = anime.find("button", class_="loadvideo")
    data_src = button_tag.get('data-src')
    index = data_src.find("?")
    url_m3u8 = data_src[:index] + ".m3u8"
    return url_m3u8 


def Anime_mp4(anime):
    iframe_tag = anime.find("iframe", class_="vframe")
    src =  iframe_tag.get('src')
    # 訪問第i集的影片
    r = requests.post(src,headers = headers,data = data)   
    soup = BeautifulSoup(r.text, 'lxml')
    # 擷取 Javascript
    script = soup.find_all("script")
    script = script[1].text

    # 擷取 Javascript 需要的字串，設立起點與終點
    index = script.find("x.send('d=",10)
    end = script.find("');",index)
    formdata = script[index+10:end]
    formdata = "d="+formdata
    return APIv2(formdata)

def APIv2(formdata):
    # Post 影片資訊，得到影片位置
    r = requests.post('https://v.anime1.me/apiv2',headers = headers,data = formdata)
    url_mp4 = r.text
    index1 = url_mp4.find("file")
    index2 = url_mp4.find(".mp4")
    url_mp4 = url_mp4[index1+11:index2+4]
    # 判斷 Response 中 URL 數量(沒：回傳-1|有：回傳數量)
    url_count = url_mp4.find(".m3u8")
    # .mp4
    if(url_count == -1):
        url_mp4 = url_mp4.replace("\/","/")
    # .mp4 和 .m3u8
    else:
        find_m3u8 = url_count
        url_m3u8 = url_mp4[:find_m3u8+5]
        url_m3u8 = url_m3u8.replace("\/","/")
        find_file = url_mp4.find("file")
        url_mp4 = url_mp4[find_file+11:]
        url_mp4 = url_mp4.replace("\/","/")
    
    # 抓取 Cookies 資訊
    global Cookies
    set_cookie = r.headers['set-cookie']
    index1 = set_cookie.find("expires")
    index2 = set_cookie.find("HttpOnly,")
    index3 = set_cookie.find("expires",index2)
    index4 = set_cookie.find("HttpOnly,",index3)
    index5 = set_cookie.find("expires",index4)
    Cookies = str(set_cookie[:index1]+set_cookie[index2+10:index3]+set_cookie[index4+10:index5])

    url = "https://"+url_mp4
    # # .mp4 URL
    # print(url , end = " ")  
    return url

def Download_mp4(url , download_path , Anime_Unit_title):
    headers1 ={
        "accept": "*/*",
        "accept-encoding": 'identity;q=1, *;q=0',
        "accept-language": 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        "cookie": Cookies,
        "dnt": '1',
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    r = requests.get(url,headers = headers1,data = data)   

    with open(os.path.join(download_path,  Anime_Unit_title + ".mp4"), 'ab') as f:
        f.write(r.content)
        f.flush()
        f.close()

    if(r.status_code == 200):
        print("\033[11D\033[0m",end= "", flush= True )
        print("\033[1;34mSuccess    \033[0m")  # 藍色成功
    else:
        print("\033[1;31mFailure    \033[0m")  # 紅色錯誤
    
def Download_m3u8(url , download_path , Anime_Unit_title):
    all_content = requests.get(url).text  # 獲取第一層M3U8文件內容
    
    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的鏈接")

    file_line = all_content.split("\n")
    unknow = True

    for index, line in enumerate(file_line): # 第二層
        if "EXTINF" in line: # 找ts地址並下載
            unknow = False
            pd_url = file_line[index + 1] # 拼出ts片段的URL
            # print(pd_url)
            
            res = requests.get(pd_url)

            c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
            with open(os.path.join(download_path, c_fule_name), 'ab') as f:
                f.write(res.content)
                f.flush()
                f.close() 

    if unknow:
        raise BaseException("未找到對應的下載鏈接")
    else:
        merge_file(download_path , Anime_Unit_title)

def merge_file(path , Anime_Unit_title):
    os.chdir(path)
    # count = len(os.listdir(path))

    count = 0

    fileExt = ".ts"
    for filename in os.listdir(path):
        if filename.endswith(fileExt):
            count = count +1

    # print("Count:",count)

    for i in range(count):
        cmd = "cat v"+repr(i)+".ts >> new.tmp"
        # print(cmd)
        os.system(cmd)

    os.system('rm *.ts')   
    os.rename("new.tmp", Anime_Unit_title + ".mp4")
    print("\033[11D\033[0m",end= "")
    print("\033[1;34mSuccess    \033[0m")  # 藍色成功

def Next_Page(url):
    try:
        r = requests.post(url,headers = headers,data = data)
        soup = BeautifulSoup(r.text, 'lxml')
        div_tag = soup.find("div" , class_="nav-previous")
        a_tag = div_tag.find("a")
        #a_tag = a_tag.string
        url_page = a_tag.get('href') 
        return str(True) , url_page
    
    except:
        return str(False) , 0

if __name__ == '__main__': 
    os.system('clear')  
    url_Anime = []

    print(
        '''
        #####################################
        # If u can't search , plz update db #
        #           Author:HeiTang          #            
        #####################################
        ''')

    # Mod1:Database.py #===============================================================================================#

    update_db = input("%8s\033[1;36mDo you want to update database ? (y/n) \033[0m" % " ")    
    if(update_db == "y"):
        Database.Search_Max_id()

    search_id = input("%8s\033[1;36mDo you want to search anime id ? (y/n) \033[0m" % " ")   
    if(search_id == "y"):
        Database.Search_Anime1_id()
    
    # 核心:Anime1.py #=================================================================================================#

    id = input("%8sEnter ID : " % " ")

    url_Anime = "https://anime1.me?cat="+str(id)

    print("\n%8s\033[0;30;42m[下載階段]\033[0m" % " ")

    # 回傳“動漫標題”
    title = Anime_title(url_Anime)

    # 建立檔案路徑
    download_path = os.getcwd() + "/Anime1_Download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    download_path = os.path.join(download_path, title)
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    # 主要
    while True:
        URL = []
        ttitle = []
        NextPage = str(False)
        
        # 回傳“子動漫標題(List)”、“子動漫URL(List)”
        URL , ttitle = Anime_Groups(url_Anime)
        # Loop 子動漫
        for i in range(len(ttitle)):
            print("%8s" % " "+ttitle[i] , end=" ", flush= True)
            
            URL[i] = Anime_Unit(URL[i])
            if(URL[i].find(".m3u8") == -1):
                print("\033[1;33mDownloading\033[0m",end= "", flush= True)  # 黃色下載中
                Download_mp4(URL[i] , download_path , ttitle[i]) 
            else:
                print("\033[1;33mDownloading\033[0m",end= "", flush= True)  # 黃色下載中
                Download_m3u8(URL[i] , download_path , ttitle[i])
                
        # 回傳“下頁狀態”、“下頁URL”
        NextPage , url_Anime = Next_Page(url_Anime)

        if(NextPage == str(False)):
            break

    print("\n%8s\033[0;30;42m[檢查階段]\033[0m" % " ")

    # Mod2:Upload.py #================================================================================================#
    
    Upload.main(is_update_file_function=bool(True), update_drive_service_folder_name='Anime1', update_drive_service_name=None, update_file_path=download_path)