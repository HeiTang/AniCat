from __future__ import print_function
import os
import io
import time
from os.path import join

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools

# 權限必須
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


def delete_drive_service_file(service, file_id):
    service.files().delete(fileId=file_id).execute()

def update_file(service, update_drive_service_name, local_file_path, update_drive_service_folder_id):
    """
    將本地端的檔案傳到雲端上
    :param update_drive_service_folder_id: 判斷是否有 Folder id 沒有的話，會上到雲端的目錄
    :param service: 認證用
    :param update_drive_service_name: 存到 雲端上的名稱
    :param local_file_path: 本地端的位置
    :param local_file_name: 本地端的檔案名稱
    """
    if update_drive_service_folder_id is None:
        file_metadata = {'name': update_drive_service_name}
    else:
        # print("雲端資料夾id: %s" % update_drive_service_folder_id)
        file_metadata = {'name': update_drive_service_name,
                         'parents': update_drive_service_folder_id}

    media = MediaFileUpload(local_file_path, )
    file_metadata_size = media.size()
    start = time.time()
    file_id = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    end = time.time()

    print('%10s\033[0;34mλ 雲端檔案名稱：\033[0m' % " " + str(file_metadata['name']))
    print('%10s\033[0;34mλ 雲端檔案 ID：\033[0m' % " " + str(file_id['id']))
    print('%10s\033[0;34mλ 檔案大小：\033[0m' % " " + str(file_metadata_size) + ' byte')
    print("%10s\033[0;34mλ 上傳時間：\033[0m" % " " + str(end-start) + '\n')

    return file_metadata['name'], file_id['id']

def search_folder(service, update_drive_folder_name=None):
    """
    如果雲端資料夾名稱相同，則只會選擇一個資料夾上傳，請勿取名相同名稱
    :param service: 認證用
    :param update_drive_folder_name: 取得指定資料夾的id，沒有的話回傳None，給錯也會回傳None
    :return:
    """
    get_folder_id_list = []
    # print(len(get_folder_id_list))
    if update_drive_folder_name is not None:
        response = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive',
                                       q = "name = '" + update_drive_folder_name + "' and mimeType = 'application/vnd.google-apps.folder' and trashed = false").execute()
        for file in response.get('files', []):
            # Process change
            # print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            get_folder_id_list.append(file.get('id'))
        if len(get_folder_id_list) == 0:
            print("你給的資料夾名稱沒有在你的雲端上！，因此檔案會上傳至雲端根目錄")
            return None
        else:
            return get_folder_id_list
    return None


def search_file(service, update_drive_service_name, is_delete_search_file=False):
    """
    本地端
    取得到雲端名稱，可透過下載時，取得file id 下載
    :param service: 認證用
    :param update_drive_service_name: 要上傳到雲端的名稱
    :param is_delete_search_file: 判斷是否需要刪除這個檔案名稱
    :return:
    """
    # Call the Drive v3 API
    results = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive',
                                   q="name = '" + update_drive_service_name + "' and trashed = false",
                                   ).execute()
    items = results.get('files', [])
    if not items:
        print('%10s雲端中未發現「' % " " + update_drive_service_name + '」檔案.' )
    else:
        # print('搜尋的檔案: ')
        for item in items:
            times = 1
            # print(u'{0} ({1})'.format(item['name'], item['id']))
            print('%10s雲端中發現「' % " " + u'{0} ({1})'.format(item['name'], item['id']) + '」檔案.' , end = ' ')
            if is_delete_search_file is True:
                print("\033[0;31m進行刪除\033[0m")
                delete_drive_service_file(service, file_id=item['id'])

            if times == len(items):
                return item['id']
            else:
                times += 1

def get_update_files_path_list(update_files_path):
    """
    將上傳檔案的資料夾內的路徑以及名稱，全部放到 list 內
    :param update_files_path: 要上傳檔案的資料夾
    """
    UploadFilesPathList = []
    UploadFilesNameList = []
    for root, dirs, files in os.walk(update_files_path):
        for f in files:
            fullPath = join(root, f)
            UploadFilesPathList.append(fullPath)
            UploadFilesNameList.append(f)
    print("%8s尋找本地檔案路徑: " % " ")
    for i in UploadFilesPathList:
        print("%10s" % " " + i)
    return UploadFilesNameList, UploadFilesPathList


def main(is_update_file_function=False, update_drive_service_folder_name=None, update_drive_service_name=None, update_file_path=None):
    """
    :param update_drive_service_folder_name: 給要上傳檔案到雲端的資料夾名稱，預設則是上傳至雲端目錄
    :param is_update_file_function: 判斷是否執行上傳的功能
    :param update_drive_service_name: 要上傳到雲端上的檔案名稱
    :param update_file_path: 要上傳檔案的位置以及名稱
    """

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))

    if is_update_file_function is True:
        
        if update_drive_service_name is None:  # 上傳資料夾內的所有檔案會跑這裡
            UploadFilesName, UploadFilesPath = get_update_files_path_list(update_files_path = update_file_path)
            print("\n%8s比對重複檔案: " % " ")
            get_folder_id = search_folder(service = service, update_drive_folder_name = update_drive_service_folder_name)
            
            #  搜尋上傳的檔案名稱是否有在雲端上並且刪除
            for UploadFileName in UploadFilesName:
                search_file(service = service, update_drive_service_name = UploadFileName, is_delete_search_file = True)
            
            # 檔案上傳到雲端上
            print("\n%8s\033[0;30;42m[上傳階段]\033[0m" % " ")
            for i in range(len(UploadFilesPath)): 
                update_file(service=service, update_drive_service_name=UploadFilesName[i],
                            local_file_path=UploadFilesPath[i], update_drive_service_folder_id=get_folder_id)
            # print("%8s=====上傳檔案完成=====" % " ")
            print("%8s\033[0;31;42m[  完成  ]\033[0m" % " ")

        else:  # 單純上傳一個檔案會跑這裡
            print(update_file_path + update_drive_service_name)
            print("\n%8s比對重複檔案: " % " ")
            
            get_folder_id = search_folder(service = service, update_drive_folder_name = update_drive_service_folder_name)
            # 搜尋要上傳的檔案名稱是否有在雲端上並且刪除
            search_file(service=service, update_drive_service_name=update_drive_service_name, is_delete_search_file=True)
            # 檔案上傳到雲端上
            update_file(service=service, update_drive_service_name=update_drive_service_name,
                        local_file_path=update_file_path + update_drive_service_name, update_drive_service_folder_id=get_folder_id)
            print("%8s\033[0;31;42m[  完成  ]\033[0m" % " ")
