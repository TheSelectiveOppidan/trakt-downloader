from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()
engine = None
session = None

class TorrentDownload(Base):
    __tablename__ = 'download_request'
    id = Column(String(255), primary_key=True)
    trakt_id = Column(String(255))
    name = Column(String(255))
    has_finished = Column(Boolean)
    comment = Column(String)
    active_time = Column(Integer)
    is_seed = Column(Boolean)
    move_completed_path = Column(String)
    private = Column(Boolean)
    total_payload_upload = Column(Integer)
    seed_rank = Column(Integer)
    seeding_time = Column(Integer)
    prioritize_first_last = Column(Boolean)
    download_payload_rate = Column(Integer)
    message = Column(String)
    num_peers = Column(Integer)
    max_connections = Column(Integer)
    compact = Column(Boolean)
    eta = Column(Integer)
    ratio = Column(Float)
    max_upload_speed = Column(Integer)
    save_path = Column(String)
    tracker_host = Column(String)
    total_uploaded = Column(Integer)
    files = Column(Integer)
    num_pieces = Column(Integer)
    total_seeds = Column(Integer)
    stop_at_ratio = Column(Boolean)
    move_on_completed_path = Column(String)
    num_seeds = Column(Integer)
    is_auto_managed = Column(Boolean)
    stop_ratio = Column(Float)
    max_download_speed = Column(Integer)
    upload_payload_rate = Column(Integer)
    remove_at_ratio = Column(Boolean)
    paused = Column(Boolean)
    all_time_download = Column(Integer)
    max_upload_slots = Column(Integer)
    total_wanted = Column(Integer)
    total_peers = Column(Integer)
    total_size = Column(Integer)
    state = Column(String)
    tracker = Column(String)
    progress = Column(Float)
    time_added = Column(Float)
    total_done = Column(Integer)
    hash = Column(String)
    next_announce = Column(Integer)
    move_completed = Column(Boolean)
    piece_length = Column(Integer)
    move_on_completed = Column(Boolean)
    seeds_peers_ration = Column(Float)
    tracker_status = Column(String)
    queue = Column(Integer)
    num_files = Column(Integer)
    distributed_copies = Column(Integer)
    total_payload_download = Column(Integer)

class TraktUser(Base):
    __tablename__ = 'authorized_user'
    id = Column(Integer, primary_key=True)
    access_token = Column(String(255))
    refresh_token = Column(String(255))
    expires_at = Column(DateTime)

class Configuration(Base):
    __tablename__= 'installation_configuration'
    key = Column(String(255), primary_key=True)
    value = Column(String(255))

engine = create_engine('sqlite:///torrenter.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))

def get_config_item(key):
    session = scoped_session(sessionmaker(bind=engine))
    return session.query(Configuration).filter_by(key=key).all()


def config_exists(key):
    session = scoped_session(sessionmaker(bind=engine))
    return session.query(Configuration).filter_by(key=key).count() > 0

def set_config_item(key, value, overwrite=False):
    if overwrite or not config_exists(key):
        session = scoped_session(sessionmaker(bind=engine))
        entry = Configuration(key=key, value=value)
        session.merge(entry)
        session.commit()

def add_user(access_token, refresh_token, expires):
    user = TraktUser(access_token=access_token, refresh_token=refresh_token, expires_at=expires)

    session = scoped_session(sessionmaker(bind=engine))
    try:
        session.add(user)
        session.commit()
    except:
        pass

def remove_user(user):
    try:
        found_user = session.query(TraktUser).filter_by(id=user.id).one()
        session.delete(found_user)
        session.commit()
    except Exception as e:
        print(e)
        pass

def update_user(user):
    remove_user(user)
    try:
        session.add(user)
        session.commit()
    except Exception as e:
        print(e)
        pass

def get_all_users():
    session = scoped_session(sessionmaker(bind=engine))
    return session.query(TraktUser).all()


def set_finished(change_id, finished):
    session = scoped_session(sessionmaker(bind=engine))
    entry = session.query(TorrentDownload).filter_by(id=change_id).first()
    entry.has_finished = finished

    session.commit()


def get_all_active():
    session = scoped_session(sessionmaker(bind=engine))
    return session.query(TorrentDownload).filter_by(has_finished=0).all()


def film_already_added(trakt_id):
    session = scoped_session(sessionmaker(bind=engine))
    return session.query(TorrentDownload).filter_by(trakt_id=trakt_id).all()


def add_to_db(id, torrent):
    session = scoped_session(sessionmaker(bind=engine))
    print("Adding " + str(torrent.name) + " with id " + str(id))
    new_entry = TorrentDownload(id= id, name=torrent.name, has_finished=0, trakt_id=torrent.trakt_id)

    try:
        session.add(new_entry)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def safe_get(obj, key):
    try:
        return obj[key]
    except Exception as e:
        print("failed getting " + str(key))
        print(e)
        return None


def update_with_live_data(torrent, live_check):
    session = scoped_session(sessionmaker(bind=engine))
    new_torrent = TorrentDownload(id=torrent.id, trakt_id=torrent.trakt_id, name=torrent.name)

    new_torrent.progress = safe_get(live_check, b'progress')
    new_torrent.has_finished = safe_get(live_check, b'is_finished')
    new_torrent.comment = safe_get(live_check, b'comment')
    new_torrent.active_time = safe_get(live_check, b'active_time')
    new_torrent.is_seed = safe_get(live_check, b'is_seed')
    new_torrent.move_completed_path = safe_get(live_check, b'move_completed_path')
    new_torrent.private = safe_get(live_check, b'private')
    new_torrent.total_payload_upload = safe_get(live_check, b'total_payload_upload')
    new_torrent.seed_rank = safe_get(live_check, b'seed_rank')
    new_torrent.seeding_time = safe_get(live_check, b'seeding_time')
    new_torrent.prioritize_first_last = safe_get(live_check, b'prioritize_first_last')
    new_torrent.download_payload_rate = safe_get(live_check, b'download_payload_rate')
    new_torrent.message = safe_get(live_check, b'message')
    new_torrent.num_peers = safe_get(live_check, b'num_peers')
    new_torrent.max_connections = safe_get(live_check, b'max_connections')
    new_torrent.compact = safe_get(live_check, b'compact')
    new_torrent.eta = safe_get(live_check, b'eta')
    new_torrent.ratio = safe_get(live_check, b'ratio')
    new_torrent.max_upload_speed = safe_get(live_check, b'max_upload_speed')
    new_torrent.save_path = safe_get(live_check, b'save_path')
    new_torrent.tracker_host = safe_get(live_check, b'tracker_host')
    new_torrent.total_uploaded = safe_get(live_check, b'total_uploaded')
    new_torrent.num_pieces = safe_get(live_check, b'num_pieces')
    new_torrent.total_seeds = safe_get(live_check, b'total_seeds')
    new_torrent.stop_at_ratio = safe_get(live_check, b'stop_at_ratio')
    new_torrent.move_on_completed_path = safe_get(live_check, b'move_on_completed_path')
    new_torrent.num_seeds = safe_get(live_check, b'num_seeds')
    new_torrent.is_auto_managed = safe_get(live_check, b'is_auto_managed')
    new_torrent.stop_ratio = safe_get(live_check, b'stop_ratio')
    new_torrent.max_download_speed = safe_get(live_check, b'max_download_speed')
    new_torrent.upload_payload_rate = safe_get(live_check, b'upload_payload_rate')
    new_torrent.remove_at_ratio = safe_get(live_check, b'remove_at_ratio')
    new_torrent.paused = safe_get(live_check, b'paused')
    new_torrent.all_time_download = safe_get(live_check, b'all_time_download')
    new_torrent.max_upload_slots = safe_get(live_check, b'max_upload_slots')
    new_torrent.total_wanted = safe_get(live_check, b'total_wanted')
    new_torrent.total_peers = safe_get(live_check, b'total_peers')
    new_torrent.total_size = safe_get(live_check, b'total_size')
    new_torrent.state = safe_get(live_check, b'state')
    new_torrent.tracker = safe_get(live_check, b'tracker')
    new_torrent.time_added = safe_get(live_check, b'time_added')
    new_torrent.total_done = safe_get(live_check, b'total_done')
    new_torrent.hash = safe_get(live_check, b'hash')
    new_torrent.next_announce = safe_get(live_check, b'next_announce')
    new_torrent.move_completed = safe_get(live_check, b'move_completed')
    new_torrent.piece_length = safe_get(live_check, b'piece_length')
    new_torrent.move_on_completed = safe_get(live_check, b'move_on_completed')
    new_torrent.seeds_peers_ration = safe_get(live_check, b'seeds_peers_ratio')
    new_torrent.tracker_status = safe_get(live_check, b'tracker_status')
    new_torrent.queue = safe_get(live_check, b'queue')
    new_torrent.num_files = safe_get(live_check, b'num_files')
    new_torrent.distributed_copies = safe_get(live_check, b'distributed_copies')
    new_torrent.total_payload_download = safe_get(live_check, b'total_payload_download')

    session.merge(new_torrent)
    session.commit()
