import os
import hashlib

from datetime import datetime
from sqlalchemy import create_engine
from database import db
from model import create_tables
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
    timestamp = os.path.getctime(path)
    return datetime.fromtimestamp(timestamp)

def traverse(directory):
    file_names = os.listdir(directory)
    paths = [os.path.join(directory, name) for name in file_names]
    dirs = [path for path in paths if os.path.isdir(path)]
    files = [path for path in paths if os.path.isfile(path)]
    for d in dirs:
        files.extend(traverse(d))
    return files
