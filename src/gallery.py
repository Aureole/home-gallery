import os
import hashlib
import shutil

from datetime import datetime
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
    timestamp = os.path.getmtime(path)
    return datetime.fromtimestamp(timestamp)

def traverse(directory):
    try:
        file_names = os.listdir(directory)
    except:
        file_names = []
        print(f'process {directory} failure')
    if 'lost+found' in file_names:
        file_names.remove('lost+found')
    paths = [os.path.join(directory, name) for name in file_names]
    dirs = [path for path in paths if os.path.isdir(path)]
    files = [path for path in paths if os.path.isfile(path)]
    for d in dirs:
        files.extend(traverse(d))
    return files

def strftime(time: datetime):
    return time.strftime('%Y%m%d_%H%M%S_%f')

def folder_name(time: datetime):
    return time.strftime('%Y-%m')

def construct_db(db_uri, directory):
    db.init(db_uri)
    create_tables(db.engine())
    paths = traverse(directory)
    for path in paths:
        hash = sha256(path)
        ext = extension(path)
        creation_time = get_creation_time(path)
        media = {'path': path, 'extension': ext, 'hash': hash, 'creation_time': creation_time}
        MediaDao.create(media)

WAIT_FOR_PROCESS_EXTENSIONS = ['.zip', '.rar', '.7z', '.pdf', '.gzip']
KNOWN_USELESS_EXTENSIONS = ['.txt', '.vmg', '.vcf', '.info', '.db', '.mtd', '.doc', '.xlsx', '.ini', '.py', '.js', '.xml', '.c', '.obj', '.py', '.cpp', '.h', '.exe', '.dll', '.tmp', '.lrv', '.thm', '.sav', '.momedia']
MEDIA_EXTENSIONS = ['.aae', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.avi', '.mp4', '.3gp', '.rmvb', '.amr', '.flv', '.mov', '.npo', '.wmv']

def conflict_copy(src, folder, name, index, extension):
    dst = os.path.join(folder, name + '_' + str(index) + extension)
    if not os.path.isfile(dst):
        shutil.copy2(src, dst)
    else:
        if sha256(src) == sha256(dst):
            return
        else:
            conflict_copy(src, folder, name, index + 1, extension)

def rearrange_images(src, dist):
    paths = traverse(src)
    size = len(paths)
    count = 0
    print('total: ', size)
    for path in paths:
        count += 1
        if count % 100 == 0:
            print(count, '/', size)
        #hash = sha256(path)
        ext = extension(path)
        if ext in WAIT_FOR_PROCESS_EXTENSIONS:
            print(path)
            continue
        if ext.lower() in KNOWN_USELESS_EXTENSIONS:
            continue
        if ext.lower() not in MEDIA_EXTENSIONS:
            print('unknown:', path)
            continue

        creation_time = get_creation_time(path)

        folder = os.path.join(dist, folder_name(creation_time))
        if not os.path.isdir(folder):
            os.mkdir(folder)

        dst_path = os.path.join(folder, strftime(creation_time) + ext)
        if not os.path.isfile(dst_path):
            shutil.copy2(path, dst_path)
        else:
            if sha256(path) == sha256(dst_path):
                continue
            conflict_copy(path, folder, strftime(creation_time), 1, ext)
