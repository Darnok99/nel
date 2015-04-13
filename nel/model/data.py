import os
import redis
import json

from pymongo import MongoClient

import logging
log = logging.getLogger()

class Store(object):
    def fetch(self, oid):
        raise NotImplementedError

    def save(self, obj):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def delete(self, oid):
        raise NotImplementedError

    def fetch_all(self):
        raise NotImplementedError

    # naive bulk get/set methods expected to be overridden
    def fetch_many(self, oid_iter):
        for oid in oid_iter:
            yield self.get(oid)

    def save_many(self, obj_iter):
        for obj in obj_iter:
            self.save(obj)

    def batched_inserter(self, batch_size):
        return BatchInserter(self, batch_size)

    @staticmethod
    def Get(store_id):
        url = os.environ.get('NEL_DATASTORE_URI', 'mongodb://localhost')

        print "datastore in os is", url

        if url.startswith('mongodb'):
            log.debug("Using mongo data store for (%s)...", store_id)
            db, collection = store_id.split(':')
            return MongoStore(db, collection, url=url)
        elif url.startswith('redis'):
            log.debug("Using redis data store for (%s)...", store_id)
            return RedisStore(store_id, url=url)
        else:
            log.error('Unsupported data store')
            raise NotImplementedError

class BatchInserter(object):
    def __init__(self, store, batch_size):
        self.store = store
        self.batch_size = batch_size
        self.batch = []

    def flush(self):
        if self.batch:
            self.store.save_many(self.batch)
            self.batch = []

    def save(self, obj):
        self.batch.append(obj)
        if len(self.batch) > self.batch_size:
            self.flush()

    def __enter__(self):
        self.batch = []
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

class RedisStore(Store):
    def __init__(self, namespace, url='redis://localhost'):
        self.kvs = redis.from_url(url)
        self.ns = namespace
        self.fmt = json # msgpack, pickle

    def to_key(self, oid):
        return self.ns + ':' + oid

    def fetch(self, oid):
        key = self.to_key(oid)
        data = self.kvs.get(key)
        return self.deserialise(data) if data != None else None

    def fetch_all(self):
        for data in self.kvs.mget(self.keys()):
            yield self.deserialise(data)

    def save(self, obj):
        key = self.to_key(obj['_id'])
        data = self.serialise(obj)
        self.kvs.set(key, data)

    def save_many(self, obj_iter):
        self.kvs.mset({
            self.to_key(obj['_id']) : self.serialise(obj) 
            for obj in obj_iter})

    def flush(self):
        # todo: is there a better way to do this?
        keys = self.keys()
        if keys:
            self.kvs.delete(keys)

    def delete(self, oid):
        self.kvs.delete(self.to_key(oid))

    def keys(self):
        return self.kvs.keys(self.to_key('*'))

    def deserialise(self, data):
        return self.fmt.loads(data)
    
    def serialise(self, obj):
        return self.fmt.dumps(obj)

class MongoStore(Store):
    def __init__(self, db, collection, url='mongodb://localhost'):
        self.collection = MongoClient(url)[db][collection]

    def fetch(self, oid):
        return self.collection.find_one({'_id':oid})

    def fetch_all(self):
        return self.collection.find()

    def save(self, obj):
        self.collection.save(obj)        
   
    def save_many(seld, obj_iter):
        self.collection.insert(obj_iter)    

    def flush(self):
        self.collection.drop()

    def delete(self, oid):
        return self.collection.drop({'_id':oid})
