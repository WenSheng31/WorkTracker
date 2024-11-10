# 簡易工時記錄

一個簡單的工時記錄系統，使用 Flask 開發，可以記錄每日工作時間並自動計算薪資。

## 功能

- 按月份記錄和查看工時
- 自動扣除午休時間（12:00-13:00）
- 自動計算月薪
- 支援跨日工時記錄
- RWD設計，支援手機瀏覽

## 使用技術

- Python 3.x
- Flask
- SQLAlchemy
- SQLite
- Bootstrap 5

## 安裝

1. Clone專案：

```bash
git clone https://github.com/WenSheng31/WorkTracker.git
cd WorkTracker
```

2. 安裝套件：

```bash
pip install flask flask-sqlalchemy
```

## 專案結構

```
WorkTracker/
├── app/
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── settings.html
│   │   └── edit_hours.html
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
└── run.py
```

## 執行

1. 設置環境變數後，運行：

```bash
flask run
```

2. 在瀏覽器前往：

```
http://127.0.0.1:5000
```

3. 使用預設密碼登入：

```
預設密碼：password123
```

## 使用說明

1. 系統功能：
    - 按月份記錄工時
    - 自動計算總工時和薪資
    - 編輯和刪除工時記錄
    - 設定時薪和修改密碼

2. 工時計算規則：
    - 自動扣除午休時間（12:00-13:00）
    - 支援跨日工時記錄
    - 工時會自動四捨五入到小數點後兩位

3. 注意事項：
    - 工時不能超過24小時
    - 結束時間必須大於開始時間
    - 建議定期更改密碼
    - 請定期備份資料庫檔案

## 開發說明

1. 資料庫：
    - 使用 SQLite
    - 資料庫文件：workhours.db
    - 包含兩個表：WorkHours 和 Settings

2. 路由結構：
    - `/`: 主頁
    - `/login`: 登入頁面
    - `/settings`: 設定頁面
    - `/add`: 新增工時記錄
    - `/edit/<id>`: 編輯工時記錄
    - `/delete/<id>`: 刪除工時記錄

## 更新紀錄

- v1.0.0 (2024/11/10)
    - 初始版本
    - 基本工時記錄功能
    - RWD支援

## 聯絡方式

wensheng@evo-techlab.com

## 注意事項

- 這是一個開發版本，不建議直接用於正式環境
- 使用前請確保已經備份所有重要數據
- 建議定期備份資料庫檔案
