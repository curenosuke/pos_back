# ファイル名: app.py

print("✅ FastAPI 起動しています（app.py）")

from fastapi import FastAPI, Body, Depends, Query, Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import Annotated, Optional



app = FastAPI()

print("✅ OPTIONS 定義済み")

## ✅ CORS設定（検証用にオリジンはワイルドカード、認証なし）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # 明示的なプリフライトレスポンス（これが必要）
# @app.options("/purchase")
# def preflight_handler(request: Request):
#     print("✅ OPTIONS /purchase に到達しました") 
#     return Response(
#         status_code=200,
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "POST, OPTIONS",
#             "Access-Control-Allow-Headers": "*"
#         }
#     )


# from db_control.connect_MySQL_local import engine, get_db        # ローカル用
from db_control.connect_MySQL_azure import engine, get_db          # Azure用
from db_control.mymodels_MySQL import Product, Base, Trade, TrdDetail
from db_control.pos_schemas import ProductCreate, ProductSearchResult, PurchaseRequest, PurchaseResponse  # ← Annotated記法のPydanticモデル
from db_control import pos_schemas as schemas  # ← schemasをインポート

# データベースにテーブルがなければ作成
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "POS API is running"}

# 商品一覧取得API（GET）
@app.get("/products")
def read_products(db: Session = Depends(get_db)):
    # データベースから全ての商品を取得して返す
    return db.query(Product).all()

# 商品登録API（POST）
@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # ProductCreateスキーマのデータからProductインスタンスを作成
    new_product = Product(
        CODE=product.CODE,
        NAME=product.NAME,
        PRICE=product.PRICE,
        TAX_CD=product.TAX_CD
    )
    # データベースに追加してコミット
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # 登録された商品を返す
    return new_product

# 商品マスタ検索API
@app.get("/products/search", response_model=Optional[ProductSearchResult])
def search_product(code: Annotated[str, Query(...)], db: Annotated[Session, Depends(get_db)]):
    product = db.query(Product).filter(Product.CODE == code).first()
    return product  # ヒットしなければNoneが返る


# 購入APIエンドポイント
@app.post("/purchase")
def make_purchase(
    request: Annotated[PurchaseRequest, Body(...)],                 # ✅ リクエストボディをPurchaseRequestとして受け取る（Pydanticで自動バリデーション）
    db: Session = Depends(get_db)              # ✅ DBセッションを注入
):
    print("✅ /purchase に到達しました")

    # 1-1. レジ担当者コードが空ならダミーコードを補完
    emp_cd = request.EMP_CD if request.EMP_CD else '9999999999'

    # 1-2. 取引テーブル（trade）に新規取引レコードを作成
    new_trade = Trade(
        DATETIME=datetime.now(),               # 現在日時
        EMP_CD=emp_cd,                         # レジ担当者コード
        STORE_CD=request.STORE_CD,             # 店舗コード（リクエストで受け取る）
        POS_NO=request.POS_NO,                 # POS端末番号（リクエストで受け取る）
        TOTAL_AMT=0,                           # 初期状態では0（あとで更新）
        TTL_AMT_EX_TAX=0                       # ※今回は未使用、0で固定
    )
    db.add(new_trade)                          # データベースに追加
    db.commit()                                # コミットして TRD_ID を確定させる
    db.refresh(new_trade)                      # new_tradeにDB反映後の値を反映（TRD_IDを取得するため）

    trd_id = new_trade.TRD_ID                  # 新しく発行された取引ID
    total = 0                                   # 合計金額の初期値

    # 1-3. 商品リストをループし、取引明細（trd_detail）に1件ずつ登録
    for idx, item in enumerate(request.items, start=1):
        trd_detail = TrdDetail(
            TRD_ID=trd_id,                     # 取引ID（外部キー）
            DTL_ID=idx,                        # 明細番号（取引内での連番）
            PRD_ID=item.PRD_ID,                # 商品ID
            PRD_CODE=item.CODE,                # 商品コード
            PRD_NAME=item.NAME,                # 商品名
            PRD_PRICE=item.PRICE,              # 商品価格（税込）
            PRD_TAX_CD=item.TAX_CD             # 税区分コード（例: "10"）
        )
        db.add(trd_detail)                     # 明細を追加
        total += item.PRICE                    # 合計金額を加算

    # 1-4. 取引テーブルに合計金額を反映して再コミット
    new_trade.TOTAL_AMT = total
    db.commit()

    # 1-5. レスポンスとして成功フラグと合計金額を返す
    return {"success": True, "total_amt": total}

import logging
logger = logging.getLogger("uvicorn.error")

from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("🔴 バリデーションエラー:", exc.errors())  # コンソール出力
    logger.error("🔴 バリデーションエラー: %s", exc.errors())  # Uvicornログ出力
    return await request_validation_exception_handler(request, exc)