from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# =====================
# デバッグ：どこで None になっているかログ出力
# =====================
print("[DEBUG] connect_MySQL_Azure.py loaded")
print("[DEBUG] ENV - DATABASE_URL:", os.getenv("DATABASE_URL"))
print("[DEBUG] ENV - SSL_CA:", os.getenv("SSL_CA"))

# ローカル用
# load_dotenv()
# import os

# ------------------------------------
# ▼ ① ローカルPCからAzure接続する場合
# （使う場合はコメントアウトを外す）
# ------------------------------------
DATABASE_URL = "mysql+pymysql://tech0sql1:step4pos-1@rdbs-step4-north-europe.mysql.database.azure.com:3306/pos_app"
SSL_CA_PATH = os.getenv("SSL_CA", "C:\\Users\\yuya2\\tech0\\STEP3-2\\zukiraku_backend\\DigiCertGlobalRootCA.crt.pem") # 山野内のセキュリティ証明書の場所
connect_args = {"ssl": {"ca": SSL_CA_PATH}}

# ------------------------------------
# ▼ ② GitHub Actions などからAzure接続する場合（GitHubには証明書がない想定）
# ------------------------------------
# DATABASE_URL = os.getenv("DATABASE_URL")
# connect_args = {"ssl": {"ca": os.getenv("SSL_CA", "/etc/ssl/certs/DigiCertGlobalRootCA.crt.pem")}}

# ------------------------------------
# 共通設定（起動時に接続）
# ------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def get_db() -> Session:　→警告があったのでchatGPTの助言をもとに上記に変更
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# ============================
# ✅ 遅延接続に切り替えたい場合はこちらを使う（※未使用）
# ============================
# def get_engine():
#     return create_engine(
#         DATABASE_URL,
#         connect_args={
#             "ssl": {"ca": SSL_CA_PATH},
#             "connect_timeout": 5
#         }
#     )
# def get_db() -> Session:
#     engine = get_engine()
#     SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


