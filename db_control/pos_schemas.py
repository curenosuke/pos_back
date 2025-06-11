# ファイル名: db_control/pos_schemas.py

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, List
from datetime import datetime

# 商品登録用のリクエストスキーマ
class ProductCreate(BaseModel):
    CODE: Annotated[str, StringConstraints(max_length=13)]
    NAME: Annotated[str, StringConstraints(max_length=50)]
    PRICE: Annotated[int, Field(ge=0)]  # 0以上の整数（負の価格は禁止）
    TAX_CD: Annotated[str, StringConstraints(max_length=2)]  # 税区分コード（例: "01", "10"）

# 検索結果用のスキーマ（1件分）
class ProductSearchResult(BaseModel):
    PRD_ID: int
    CODE: str
    NAME: str
    PRICE: int

    model_config = {"from_attributes": True}  # ✅ Pydantic v2対応

# 商品データ1件分（購入用）
class PurchasedItem(BaseModel):
    PRD_ID: int
    CODE: str
    NAME: str
    PRICE: int
    TAX_CD: str
    
    model_config = {"from_attributes": True}  # ✅ ここが必要！

# 購入リクエスト（tradeとtrd_detail両方に該当）
class PurchaseRequest(BaseModel):
    EMP_CD: str                                # レジ担当者コード（任意）
    STORE_CD: str        # 店舗コード
    POS_NO: str          # POS端末番号
    items: list[PurchasedItem]                               # 購入した商品一覧

    # ✅ 明示的にJSON Bodyとする（Swaggerに誤認させない）
    model_config = {"json_schema_extra": {
        "examples": [
            {
                "EMP_CD": "9999",
                "STORE_CD": "30",
                "POS_NO": "90",
                "items": [
                    {
                        "PRD_ID": 6,
                        "CODE": "4901681237036",
                        "NAME": "フィラー3C 0.7（黒）",
                        "PRICE": 2200,
                        "TAX_CD": "10"
                    }
                ]
            }
        ]
    }}

# 購入後のレスポンス（合計金額や成功フラグ）
class PurchaseResponse(BaseModel):
    success: bool
    total_amt: int
