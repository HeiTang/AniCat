## Anime1 Video Download By Python Script

### 架構圖
```
 -------------------------------------  -
|       Create / Update Database      |  |
 -------------------------------------   |-- Mod1:Database.py
 -------------------------------------   |
|           Search Database           |  |
 -------------------------------------  -
 -------------------------------------  - 
|  --------------   ----------------  |  |
| |              | | .M3U8 Download | |  |
| |     .MP4     |  ----------------  |  |-- Anime1.py (核心)
| |   Download   |  ----------------  |  |
| |              | |    .ts Merge   | |  |
|  --------------   ----------------  |  |
 -------------------------------------  -
 -------------------------------------  - 
|        Upload to Google Drive       |  |-- Mod2:Upload.py
 -------------------------------------  -
```

### Usage

1. 建立 MySQL 資料庫
  
   - 建立 Database
     ```
     cursor.execute("CREATE DATABASE Anime1_db")
     ```
   - 建立 Table
     ```
     cursor.execute("CREATE TABLE Anime1 (Name VARCHAR(255), ID INTEGER(99), Key_id INT AUTO_INCREMENT PRIMARY KEY)")
     ```

2. 取得Google Drive API

   - https://developers.google.com/drive/api/v3/quickstart/python
  
   - 點擊 Enable the Drive API ，會提供下載 credentials.json 的按鈕。

   - 可以參考「[Python 上傳檔案到 Google Drive](https://shareboxnow.com/python-google-drive-1/)」

3. `pip3 install -r requirement.txt`

4. `pip3 Anime1.py`

### 注意
資料庫的功能主要是紀錄動漫的名稱與其對應的 ID，例如：達爾文遊戲，ID 為 651。

