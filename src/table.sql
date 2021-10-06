
CREATE UNIQUE INDEX media_hash_idx ON media(hash);
CREATE INDEX media_creation_time_idx ON media(creation_time);