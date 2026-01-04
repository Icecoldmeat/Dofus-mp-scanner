from datetime import datetime

import pandas as pd
from sqlalchemy import Column, String, DateTime, Integer, func, select, UniqueConstraint
from sqlalchemy.dialects.mysql import insert

from sqlalchemy.orm import DeclarativeBase, Session

from connect import SqlAlchemyConnector


class Base(DeclarativeBase):
       pass

class DofusPriceModel(Base):
    __tablename__ = "dofus_prices"

    id = Column(Integer, primary_key=True)
    name= Column(String(255), nullable=False)
    price_type= Column(String(255), nullable=True)
    price= Column(Integer, nullable=True)
    auction_number = Column(Integer, nullable=True)
    image_file_path= Column(String(255), nullable=True)
    creation_date = Column(DateTime, nullable=False)
    update_date = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "image_file_path",
            "auction_number",
            name="uq_image_auction",
        ),)


class ExternalDofusPriceRepository:

    def __init__(self):
        self.engine = SqlAlchemyConnector().connect('mysql')
        DofusPriceModel.__table__.create(self.engine, checkfirst=True)

    def insert(self, price_model: DofusPriceModel):
        with Session(self.engine) as session:
            q = session.query(DofusPriceModel.id).filter_by(image_file_path=price_model.image_file_path, auction_number=price_model.auction_number)
            if not session.query(q.exists()).scalar():
                session.add(price_model)
                session.commit()

    def upsert(self, price_model: DofusPriceModel):
        stmt = insert(DofusPriceModel).values(
            id=price_model.id,
            name=price_model.name,
            price_type=price_model.price_type,
            price=price_model.price,
            auction_number=price_model.auction_number,
            image_file_path=price_model.image_file_path,
            creation_date=price_model.creation_date,
            update_date=datetime.now(),
        )

        stmt

    #    stmt = stmt.on_duplicate_key_update(name=price_model.name
    #        index_elements=["image_file_path", "auction_number"],
    #        set_={
    #            "name": price_model.name,
    #            "price_type": price_model.price_type,
    #            "price": price_model.price,
    #            "auction_number": price_model.auction_number,
    #            "update_date": datetime.now(),
    #        }
    #    )

        with Session(self.engine) as session:
            session.execute(stmt)
            session.commit()


    def find_by_image_file_path(self, image_file_path, auction_number: int):
        with Session(self.engine) as session:
            stmt = select(DofusPriceModel).where(DofusPriceModel.image_file_path == image_file_path, DofusPriceModel.auction_number == auction_number)
            item = session.execute(stmt)

            if item:
                return item

            return DofusPriceModel()

    def find_all(self) -> pd.DataFrame:
        df = pd.read_sql('SELECT * FROM dofus_prices', con=self.engine)
        return df

    def find_last_id(self) -> pd.DataFrame:
        df = pd.read_sql('SELECT id,image_file_path FROM dofus_prices order by id desc limit 1 ', con=self.engine)
        return df
