__author__ = 'qipanguan'
# !/usr/bin/python2.6
# coding=utf-8
# Thread Pool Manager

import threading
import Queue
import time
import traceback


class Worker(threading.Thread):
    worker_count = 0

    def __init__(self, work_queue, result_queue, err_queue, timeout):
        super(Worker, self).__init__()
        self.setDaemon(True)
        self.id = Worker.worker_count
        Worker.worker_count += 1
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.err_queue = err_queue
        self.timeout = timeout
        self.args = None
        #1 means my job is working, 0 means no job working
        self.job_working_flag = 0

    def run(self):
        while True:
            try:
                if self.timeout:
                    callable, args, kwds = self.work_queue.get(timeout=self.timeout)
                else:
                    callable, args, kwds = self.work_queue.get(False)
                self.job_working_flag = 1
                self.args = args
                res = callable(*args, **kwds)
                self.job_working_flag = 0
            except Queue.Empty:
                self.job_working_flag = 0
                continue
            except Exception:
                traceback.print_exc()
                self.job_working_flag = 0


class WorkerManager(object):
    def __init__(self, num_of_workers=10, timeout=None):
        self.work_num = num_of_workers
        self.work_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.err_queue = Queue.Queue()
        self.workers = []
        self.timeout = timeout
        self._recruitThreads()

    def _recruitThreads(self):
        for i in range(self.work_num):
            worker = Worker(self.work_queue, self.result_queue, self.err_queue, self.timeout)
            self.workers.append(worker)

    def wait_complete(self):
        # if not work_queue means the worker thread if free will destroy,
        while not self.work_queue.empty():
            time.sleep(1)
        working_workers = []
        for worker in self.workers:
            working_workers.append(worker)
        while len(working_workers) > 0:
            for worker in working_workers:
                if worker.job_working_flag == 0:
                    working_workers.remove(worker)

    def add_job(self, callable, *args, **kwds):
        self.work_queue.put((callable, args, kwds))

    def start_working(self):
        for work in self.workers:
            work.start()

    def get_fail_job(self):
        return [self.result_queue.get() for i in range(self.result_queue.qsize())]
