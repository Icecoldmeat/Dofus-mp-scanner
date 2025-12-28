import pandas as pd
from sqlalchemy import Column, String, DateTime, Integer, func
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

    def find_all(self) -> pd.DataFrame:
        df = pd.read_sql('SELECT * FROM dofus_prices', con=self.engine)
        return df
