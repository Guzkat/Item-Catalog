from flask import url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Store, Base, Tv, User

engine = create_engine ('sqlite:///tvcatalog.db')
Base.metadata.bind = engine 

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Electronic Depot catalog 

User1 = User(name="Johnny Guzman", email="jcguz58@gmail.com")

session.add(User1)
session.commit()

store1 = Store( user_id=1, name="Tech World")

session.add(store1)
session.commit()

tv1 = Tv(user_id=1,
        brand="Samsung", 
        size="65", 
        price="$4,999.99", 
        series="Q900", 
        description="Smart 8K UHD TV", 
        year="2019",
)

session.add(tv1)
session.commit()

tv2 = Tv(user_id=1,
        brand="LG",
        size="65",
        price="$2,799.99",
        series="C8 Series",
        description="Smart 4K UHD TV with HDR",
        year="2018",
)

session.add(tv2)
session.commit()

tv3 = Tv(user_id=1,
        brand="Sony",
        size="65",
        price="$3,499.99",
        series="Z9F Master Series",
        description="Smart 4K UHD TV with HDR",
        year="2018",
)

session.add(tv3)
session.commit()


tv4 = Tv(user_id=1,
        brand="Vizio",
        size="75",
        price="$1,648.99",
        series="XLED",
        description="4K Ultra HD SmartCast Home Theater Display - E75-E1/E3",
        year="2017",
)

session.add(tv4)
session.commit()


tv5 = Tv(user_id=1,
        brand="TCL",
        size="40",
        price="$199.99",
        series="40S325",
        description="1080p Smart LED Roku TV",
        year="2018",
)

session.add(tv5)
session.commit()


tv6 = Tv(user_id=1,
        brand="Hisense",
        size="65",
        price="$649.99",
        series="65H9080E ",
        description=" 4K Ultra HD Smart LED TV ",
        year="2018",
)

session.add(tv6)
session.commit()


tv7 = Tv(user_id=1,
        brand="Mitsubishi",
        size="73",
        price="$2,231.99",
        series="WD-73640",
        description="1080p Projection TV",
        year="2011",
)

session.add(tv7)
session.commit()


tv8 = Tv(user_id=1,
        brand="Toshiba",
        size="43",
        price="$329.99",
        series="43LF621U19",
        description="4K Ultra HD Smart LED TV HDR - Fire TV Edition",
        year="2017",
)

session.add(tv8)
session.commit()


print ("TV's added!")
