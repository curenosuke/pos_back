# ファイル名: db_control/mymodels_MySQL.py

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Date, CHAR, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
from sqlalchemy.dialects.mysql import INTEGER
import sys
import os

# db_controlへのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'db_control'))

Base = declarative_base()

class Product(Base):
    __tablename__ = "product"

    PRD_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CODE = Column(String(13), unique=True)
    NAME = Column(String(50))
    PRICE = Column(Integer)
    TAX_CD = Column(CHAR(2))

# 取引テーブル
class Trade(Base):
    __tablename__ = "trade"

    TRD_ID = Column(Integer, primary_key=True, autoincrement=True)  # 取引一意キー
    DATETIME = Column(TIMESTAMP, default=datetime.now)  # 現在日時を自動設定
    EMP_CD = Column(CHAR(10), nullable=False)  # レジ担当者コード
    STORE_CD = Column(CHAR(5), nullable=False)  # 店舗コード
    POS_NO = Column(CHAR(3), nullable=False)  # POS機ID
    TOTAL_AMT = Column(Integer, default=0)  # 合計金額
    TTL_AMT_EX_TAX = Column(Integer, default=0)  # 税抜金額

    # 取引明細へのリレーション（オプション）
    trd_details = relationship("TrdDetail", back_populates="trade")

# 取引明細テーブル
class TrdDetail(Base):
    __tablename__ = "trd_detail"

    TRD_ID = Column(Integer, ForeignKey("trade.TRD_ID"), primary_key=True)  # 取引ID（複合主キー）
    DTL_ID = Column(Integer, primary_key=True)  # 明細番号（複合主キー）
    PRD_ID = Column(Integer, ForeignKey("product.PRD_ID"))
    PRD_CODE = Column(String(13))
    PRD_NAME = Column(String(50))
    PRD_PRICE = Column(Integer)
    PRD_TAX_CD = Column(CHAR(2))

    # リレーション（オプション）
    trade = relationship("Trade", back_populates="trd_details")