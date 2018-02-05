#!/user/env python3
# -*- coding: utf-8 -*-

import threading
import queue
import copy


class QueueSystem:
    def __init__(self):
        self.que = list()
        self.lock = threading.Lock()

    def create(self):
        que = queue.LifoQueue(maxsize=10)
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
