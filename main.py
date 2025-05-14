# 導入 FastAPI 框架，這是一個現代、快速（高效能）的 Web 框架，用於建構 API。
# "from fastapi import FastAPI" 的意思是從 "fastapi" 這個套件中，引入 "FastAPI" 這個類別。
from fastapi import FastAPI

# 導入 PyMongo 套件中的 MongoClient，這是 MongoDB 官方推薦的 Python 驅動程式。
# 它允許我們的 Python 應用程式與 MongoDB 資料庫進行互動。
from pymongo import MongoClient
from pydantic import BaseModel

# 設定資料庫名稱的變數。在 MongoDB 中，資料庫是集合 (collections) 的容器。
# 將資料庫名稱存儲在變數中，方便後續重複使用和修改。
dc_name = "swenbao"

# 設定 MongoDB 的連接 URI (Uniform Resource Identifier)。
# URI 是一個字串，指定了如何連接到資料庫，包含了協議、認證資訊、主機位置、資料庫名稱以及其他連接選項。
# f-string (格式化字串字面值) 是一種方便的字串格式化方法，可以直接在字串中嵌入變數。
# - "mongodb+srv://" : 表示使用 DNS Seedlist Connection Format，這是一種推薦的連接方式，可以提高可用性和彈性。
# - "{dc_name}:{dc_name}" : 提供使用者名稱和密碼進行認證。這裡使用者名稱和密碼剛好與資料庫名稱相同。
# - "@gdg-mongodb.chih-hao.xyz/" : 指定 MongoDB 伺服器的主機名稱和域名。
# - "{dc_name}" : 指定要連接的目標資料庫。
# - "?authMechanism=SCRAM-SHA-256&tls=true" : 指定額外的連接選項。
#   - "authMechanism=SCRAM-SHA-256": 設定認證機制為 SCRAM-SHA-256，這是一種安全的挑戰-回應認證機制。
#   - "tls=true": 啟用 TLS/SSL 加密，確保客戶端和伺服器之間的通訊是加密的，防止竊聽。
uri = f"mongodb+srv://{dc_name}:{dc_name}@gdg-mongodb.chih-hao.xyz/{dc_name}?authMechanism=SCRAM-SHA-256&tls=true"

# 指定 TLS/SSL 憑證檔案的路徑。
# 為了進行安全的 TLS 連線，有時需要客戶端提供一個 CA (Certificate Authority) 憑證檔案。
# 這個檔案包含了受信任的憑證頒發機構的資訊，用於驗證伺服器憑證的真實性。
tls_ca_file = "mongodb-bundle.pem"

# 建立 MongoClient 物件，這是與 MongoDB 伺服器建立連線的入口點。
# 我們傳入連接 URI 和 TLS CA 檔案路徑。
# `tlsCAFile` 參數指定了 CA 憑證檔案。
client = MongoClient(uri, tlsCAFile=tls_ca_file)

# 連接到指定的資料庫。
# 一旦建立了 MongoClient 物件，就可以透過類似字典取值的方式來存取特定的資料庫。
# `db` 這個變數現在代表了名為 "swenbao" 的資料庫物件。
db = client[dc_name]

# 存取資料庫中的特定集合 (collection)。
# 在 MongoDB 中，集合類似於關聯式資料庫中的資料表，用於儲存文件 (documents)。
# `users` 這個變數代表了名為 "users" 的集合物件。
users = db["users"]

# 建立 FastAPI 應用程式的實例。
# `app` 這個變數是 FastAPI 應用程式的核心，我們將會用它來定義路由 (routes) 和處理請求。
app = FastAPI()


class User(BaseModel):
    username: str

# 定義一個 GET 請求的路由，用於獲取用戶數量。
# "@app.get(\"/user_count\")" 是一個裝飾器，它將下面的 `get_user_count` 函數與 HTTP GET 請求的 "/user_count" 路徑綁定。
# 當伺服器收到一個對 "/user_count" 路徑的 GET 請求時，`get_user_count` 函數將會被執行。
@app.get("/user_count")
# 定義一個異步 (asynchronous) 函數 `get_user_count`。
async def get_user_count():
    # 執行資料庫查詢來計算 "users" 集合中的文件數量。
    # `users.count_documents({})` 會計算集合中所有文件（由空查詢 "{}" 指定）。
    # 這是一個高效的方法來獲取集合中的總項目數，而不需要檢索所有文件。
    user_count = users.count_documents({})
    # 返回一個包含用戶數量的 JSON 回應。
    # FastAPI 會自動將這個字典轉換為 JSON。
    return {"total_users": user_count}

@app.get("/user_name_list")
async def get_user_name_list():
    # 查詢 "users" 集合中的所有文件，並且只選取 "username" 欄位。
    # `users.find({}, {"username": 1, "_id": 0})`
    # - `{}`: 空的查詢條件，表示選取所有文件。
    # - `{"username": 1, "_id": 0}`: 投影 (projection)，指定要返回的欄位。
    #   - `"username": 1`: 表示包含 "username" 欄位。
    #   - `"_id": 0": 表示不包含 "_id" 欄位 (MongoDB 預設會包含 "_id")。
    # `cursor` 是一個指向查詢結果的游標物件。
    cursor = users.find({}, {"username": 1, "_id": 0})
    # 使用列表推導式 (list comprehension) 從游標中提取所有用戶名。
    # `doc["username"] for doc in cursor` 會迭代游標中的每個文件 (doc)，並取出 "username" 欄位的值。
    # 結果會是一個包含所有用戶名的列表。
    user_list = [doc["username"] for doc in cursor]
    # 返回一個包含用戶名列表的 JSON 回應。
    return {"usernames": user_list}


# 定義一個 POST 請求的路由，路徑是 "/delete-user"。
# POST 請求通常用來傳送資料給伺服器，以建立或修改資源。在這裡，我們用它來請求刪除一個用戶。
# "@app.post(...)" 是一個裝飾器，它告訴 FastAPI 當有 POST 請求送到 "/delete-user" 時，就執行下面的 `delete_user` 函數。
@app.post("/delete-user")
# 定義一個異步函數 `delete_user`。
# `async def` 表示這是一個協程，它可以暫停和恢復執行，讓其他任務在等待時可以運行，適合處理像資料庫操作這樣的 I/O 綁定任務。
# `user: User` 這裡的 `User` 是我們之前用 Pydantic 定義的資料模型。
# FastAPI 會自動驗證請求的 body 是否符合 `User` 模型 (即包含一個 `username` 字串)。
# 如果符合，`user` 參數就會是一個 `User` 物件，我們可以透過 `user.username` 來取得傳入的使用者名稱。
async def delete_user(user: User):
    # 執行 MongoDB 的 `delete_one` 操作，嘗試從 "users" 集合中刪除一個文件。
    # `{"username": user.username}` 是一個查詢條件，它會尋找 "username" 欄位與客戶端傳來的 `user.username` 相符的文件。
    # `delete_one` 只會刪除第一個匹配到的文件。
    # `result` 會是一個 `DeleteResult` 物件，包含了刪除操作的結果，例如刪除了多少文件。
    result = users.delete_one({"username": user.username})
    # 檢查 `result.deleted_count` 是否等於 1。
    # 如果 `deleted_count` 是 1，表示成功找到並刪除了一個用戶。
    if result.deleted_count == 1:
        # 如果刪除成功，返回一個 JSON 物件，包含 `state: True` 和一條成功訊息。
        # f-string (例如 `f"User {user.username} deleted."`) 允許我們在字串中嵌入變數的值。
        return {"state": True, "message": f"User {user.username} deleted."}
    else:
        # 如果 `deleted_count` 不是 1 (通常是 0)，表示沒有找到指定用戶名的用戶，所以沒有文件被刪除。
        # 返回一個 JSON 物件，包含 `state: False` 和一條用戶未找到的訊息。
        return {"state": False, "message": f"User {user.username} not found."}

# 定義一個 POST 請求的路由，路徑是 "/add-user"。
# 這個端點用來接收資料並新增一個用戶到資料庫。
@app.post("/add-user")
# 定義一個異步函數 `add_user`。
# `user: User` 與上面 `delete_user` 函數中的一樣，FastAPI 會驗證請求 body 並將其轉換為 `User` 物件。
async def add_user(user: User):
    # 在新增用戶之前，先檢查該用戶名是否已經存在於資料庫中。
    # `users.find_one({"username": user.username})` 會在 "users" 集合中查找 "username" 欄位與傳入的 `user.username` 相符的文件。
    # 如果找到了，`find_one` 會返回該文件 (一個字典)，否則返回 `None`。
    if users.find_one({"username": user.username}):
        # 如果 `find_one` 返回了文件 (不是 `None`)，表示用戶已存在。
        # 返回一個 JSON 物件，包含 `state: False` 和一條用戶已存在的訊息。
        return {"state": False, "message": f"User {user.username} already exists."}
    # 如果用戶不存在，就執行 MongoDB 的 `insert_one` 操作，將新用戶的資料插入到 "users" 集合中。
    # 我們插入一個只包含 "username" 欄位的文件，其值來自 `user.username`。
    users.insert_one({"username": user.username})
    # 插入成功後，返回一個 JSON 物件，包含 `state: True` 和一條用戶已新增的訊息。
    return {"state": True, "message": f"User {user.username} added."}
