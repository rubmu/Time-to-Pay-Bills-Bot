from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import InstrumentedAttribute

# Connecting to a database:
engine = create_engine('postgresql:...', echo=True)

# Defining tables inside the MetaData directory.
# MetaData is a container object that keeps together many different
# features of a database (or multiple databases) being described.


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    first_name = Column(String(60))
    last_name = Column(String(60))
    username = Column(String(60), unique=True)

    def __init__(self, telegram_id, first_name, last_name, username):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    @property
    def __repr__(self):
        return "<User('%i','%s', '%s', '%s')>" % (self.telegram_id,
                                                  self.first_name,
                                                  self.last_name,
                                                  self.username)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('user.id'))
    content_type = Column(String(20))
    date = Column(DateTime)

    def __init__(self, user, content_type, date):
        self.user = user
        self.content_type = content_type
        self.date = date

    @property
    def __repr__(self):
        return "<Message('%i', '%s', '%s')>" % (self.user,
                                                self.content_type,
                                                self.date)


class Text(Base):
    __tablename__ = 'text'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('message.id'))
    content = Column(String(150))
    length = Column(Integer)
    type = Column(String(20))

    def __init__(self, message_id, content, length, type):
        self.message_id = message_id
        self.content = content
        self.length = length
        self.type = type

    @property
    def __repr__(self):
        return "<Text('%i', '%s', '%i', '%s')>" % (self.message_id,
                                                   self.content,
                                                   self.length,
                                                   self.type)


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('message.id'))
    full_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    file_id = Column(String(150), unique=True)

    def __init__(self, message_id, full_size, width, height, file_id):
        self.message_id = message_id
        self.full_size = full_size
        self.width = width
        self.height = height
        self.file_id = file_id

    @property
    def __repr__(self):
        return "<Image('%i', '%i', '%i', '%i', '%s')>" % (self.message_id,
                                                          self.full_size,
                                                          self.width,
                                                          self.height,
                                                          self.file_id)


class Indicator(Base):
    __tablename__ = 'indicator'

    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    date = Column(DateTime)
    meter_numbers = Column(Integer)

    def __init__(self, id, name, date, meter_numbers):
        self.id = id
        self.name = name
        self.date = date
        self.meter_numbers = meter_numbers

    def update(self, session):
        mapped_values = {}
        for item in Indicator.__dict__.items():
            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)
            if is_column:
                mapped_values[field_name] = getattr(self, field_name)

        session.query(Indicator).filter(Indicator.id == self.id).update(mapped_values)
        session.commit()

    @property
    def __repr__(self):
        return "<Indicator('%s', '%s', '%i')>" % (self.name,
                                                  self.date,
                                                  self.meter_numbers)


Base.metadata.create_all(engine)
