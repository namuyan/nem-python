#!/user/env python3
# -*- coding: utf-8 -*-

from threading import Lock
import queue
import copy
import atexit
import bjson
import logging
import os
import random


class QueueSystem:
    def __init__(self):
        self.que = list()
        self.lock = Lock()

    def create(self):
        que = queue.LifoQueue(maxsize=25)
        with self.lock:
            self.que.append(que)
        return que

    def remove(self, que):
        with self.lock:
            if que in self.que:
                self.que.remove(que)

    def broadcast(self, item):
        with self.lock:
            for q in copy.copy(self.que):
                try:
                    q.put_nowait(item)
                except queue.Full:
                    self.que.remove(q)


class PeerStorage:
    def __init__(self, path):
        self.path = path
        self.sets = set()
        self.load()
        atexit.register(self.save)
        atexit.register(self.load)
        self.lock = Lock()

    def __repr__(self):
        return "<PeerStorage num={} file={}>".format(len(self.sets), self.path)

    def save(self):
        with open(self.path, mode='bw') as fp:
            bjson.dump(self.sets, fp=fp)
        logging.info("JsonDataBase saved to {}".format(os.path.split(self.path)[1]))

    def load(self):
        try:
            with open(self.path, mode='br') as fp:
                with self.lock:
                    self.sets.update(bjson.load(fp=fp))
        except:
            with open(self.path, mode='bw') as fp:
                bjson.dump(self.sets, fp=fp)
        logging.info("JsonDataBase load from {}".format(os.path.split(self.path)[1]))

    def random(self):
        return random.choice(list(self.sets))

    def add(self, item):
        with self.lock:
            self.sets.add(item)

    def update(self, items):
        with self.lock:
            self.sets.update(items)

    def __delitem__(self, key):
        if key in self.sets:
            with self.lock:
                self.sets.remove(key)

    def __len__(self):
        return len(self.sets)

    def __contains__(self, item):
        return item in self.sets
