from typing import Optional
from base import BaseDAO
from model import Media

class MediaDao(BaseDAO):
    model_cls = Media

    @staticmethod
    def find_by_hash(hash: str) -> Optional[Media]:
        return MediaDao.find_by(Media.hash == hash)
