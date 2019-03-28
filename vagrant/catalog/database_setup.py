import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Store(Base):
	__tablename__ = 'store'
	id = Column(Integer, primary_key=True)
	name = Column(String(150), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'))


class Tv(Base):
	__tablename__ = 'tv'

	id = Column(Integer, primary_key=True)
	brand = Column(String(150), nullable=False)
	size = Column(String(150))
	price = Column(String(10))
	series = Column(String(150))
	year = Column(String(10))
	description = Column(String(150))
	email = Column(String(150))
	store_id = Column(Integer, ForeignKey('store.id'))
	user_id = Column(Integer, ForeignKey('user.id'))



# serializable format

	@property
	def serialize(self):
		return {
			'id': self.id,
			'brand': self.brand,
			'size': self.size,
			'price': self.price,
			'series': self.series,
			'year': self.year,
			'description': self.description,
			'email': self.email,
			'store': self.store
		}


engine = create_engine('sqlite:///tvcatalog.db')
Base.metadata.create_all(engine)
