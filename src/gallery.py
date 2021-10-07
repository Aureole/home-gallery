import os
import hashlib

from datetime import datetime
from sqlalchemy import create_engine
from database import db
from model import Media, create_tables
from dao import MediaDao

def sha256(path: str) -> str:
    hash = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            bytes = f.read(4096)
            if not bytes:
                break
            hash.update(bytes)
    return hash.hexdigest()

def extension(path: str) -> str:
    return os.path.splitext(path)[1]

def get_creation_time(path: str) -> datetime:
    timestamp = os.path.getmtime(path)
    return datetime.fromtimestamp(timestamp)

def traverse(directory):
    try:
        file_names = os.listdir(directory)
    except:
        file_names = []
        print(f'process {directory} failure')
    paths = [os.path.join(directory, name) for name in file_names]
    dirs = [path for path in paths if os.path.isdir(path)]
    files = [path for path in paths if os.path.isfile(path)]
    for d in dirs:
        files.extend(traverse(d))
    return files

def construct_db(db_uri, directory):
    db.init(db_uri)
    create_tables(db.engine())
    paths = traverse(directory)
    print(paths)
    for path in paths:
        hash = sha256(path)
        ext = extension(path)
        creation_time = get_creation_time(path)
        media = {'path': path, 'extension': ext, 'hash': hash, 'creation_time': creation_time}
        MediaDao.create(media)