import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.models import Base
from model.models import User, Link

engine = create_engine('sqlite:///db.db', echo=True)
# Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)

def get_or_create_user(id):
  session = Session()
  user = session.query(User).filter(User.id == id).first()
  if user:
    session.close()
    return user
  else:
    newUser = User()
    newUser.id = id
    session.add(newUser)
    session.commit()
    session.close()
    return newUser

def get_user_links(id):
  session = Session()
  links = session.query(Link).filter(Link.creator_id == id).all()
  session.close()
  return links


def save_link(url, creator_id, visibility='public'):
  session = Session()
  link = session.query(Link).filter(Link.url == url).first()

  if link:
    session.close()
    return link
  else:
    link = Link(
      creator_id=creator_id,
      url=url,
      short_id=str(uuid.uuid4())[:8],
      visibility=visibility,
      counter=0)

    session.add(link)

    # in case got existed short_id
    while True:
      try:
        session.commit()
        break
      except Exception:
        link.short_id = str(uuid.uuid4())[:8]
        session.commit()

    link = session.query(Link).filter(Link.url == url).first()
    session.close()
    return link

def update_link_counter(short_id):
  session = Session()
  link = session.query(Link).filter(Link.short_id == short_id).first()
  link.counter += 1
  session.commit()
  session.close()

def get_link(short_id):
  session = Session()
  link = session.query(Link).filter(Link.short_id == short_id).first()
  session.close()
  return link

def delete_link(user_id, short_id):
  session = Session()
  link = session.query(Link).filter(Link.short_id == short_id).first()
  if link and link.creator_id == user_id:
    session.delete(link)
    session.commit()

  session.close()
  return link

def update_link(user_id, new_link, short_id):
  session = Session()
  link = session.query(Link).filter(Link.short_id == short_id).first()

  if link and link.creator_id == user_id:
    link.short_id = new_link["short_id"]
    link.visibility = new_link["visibility"]
    session.commit()

  session.close()
  return link
