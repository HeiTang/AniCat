# -*- coding:utf-8 -*-  
import os
import sys
import requests
import datetime
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

# reload(sys)
# sys.setdefaultencoding('utf-8')

def download(url):
    download_path = os.getcwd() + "/Download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
        
    #新建日期文件夾
    download_path = os.path.join(download_path, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    #print download_path
    os.mkdir(download_path)
        
    all_content = requests.get(url).text  # 獲取第一層M3U8文件內容
    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的鏈接")

    if "EXT-X-STREAM-INF" in all_content:  # 第一層
        file_line = all_content.split("\n")
        print(file_line)
        for line in file_line:
            if '.m3u8' in line:
                url = url.rsplit("/", 1)[0] + "/" + line # 拼出第二層m3u8的URL
                all_content = requests.get(url).text

    file_line = all_content.split("\n")

    unknow = True
    key = ""

    # for index, line in enumerate(file_line): # 第二層
    #     if "#EXT-X-KEY" in line:  # 找解密Key
    #         method_pos = line.find("METHOD")
    #         comma_pos = line.find(",")
    #         method = line[method_pos:comma_pos].split('=')[1]
    #         print("Decode Method：", method)
            
    #         uri_pos = line.find("URI")
    #         quotation_mark_pos = line.rfind('"')
    #         key_path = line[uri_pos:quotation_mark_pos].split('"')[1]
            
    #         key_url = url.rsplit("/", 1)[0] + "/" + key_path # 拼出key解密密鑰URL
    #         res = requests.get(key_url)
    #         key = res.content
    #         print("key：" , key)
            
    #     if "EXTINF" in line: # 找ts地址並下載
    #         unknow = False
    #         pd_url = url.rsplit("/", 1)[0] + "/" + file_line[index + 1] # 拼出ts片段的URL
    #         pd_url1 = file_line[index + 1] # 拼出ts片段的URL
    #         print(pd_url1)
            
    #         res = requests.get(pd_url1)
    #         c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
            
    #         if len(key): # AES 解密
    #             cryptor = AES.new(key, AES.MODE_CBC, key)  
    #             with open(os.path.join(download_path, c_fule_name + ".mp4"), 'ab') as f:
    #                 f.write(cryptor.decrypt(res.content))
    #         else:
    #             with open(os.path.join(download_path, c_fule_name), 'ab') as f:
    #                 f.write(res.content)
    #                 f.flush()
    if unknow:
        raise BaseException("未找到對應的下載鏈接")
    else:
        print("下載完成")

    merge_file(download_path)

def merge_file(path):
    os.chdir(path)

    count = len(os.listdir(path))

    for i in range(count-1):
        cmd = "cat v"+repr(i)+".ts >> new.tmp"
        print(cmd)
        os.system(cmd)

    os.system('rm *.ts')
    # os.system('rm *.mp4')  
    os.rename("new.tmp", "new.mp4")
        
        
if __name__ == '__main__': 
    url = "https://i.animeone.me/WWvQx.m3u8"
    download(url)