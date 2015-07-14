import random
import time
import urllib2
import Queue
import threading
import logging


class Requests(object):
    def __init__(self, min, max, addr, recorder):
        self._min = min
        self._max = max
        self._keyrange = 'abcdefghijklmnopqrstuvwxyz'
        #http://10.18.207.107:8091/search/api/getResult?type=0&start=0&rows=35&search_key=
        self._addr = addr
        self._recorder = recorder

    def _key2url(self, key):
        return self._addr + key

    def _get_key(self, min, max):
        ken_len = random.randint(min, max)
        return ''.join(random.sample(self._keyrange, ken_len))


    def get_request(self):
        key = self._get_key(self._min, self._max)
        url = self._key2url(key)
        return url

    def get_requests(self):
        ret = []
        for key_len in range(self._min, self._max + 1):
            ret.append(self._key2url(self._get_key(key_len, key_len)))

        return ret

    def record(self, start_ts, end_ts):
        self._recorder.add((start_ts, end_ts))
    def record_failure(self):
        self._recorder.add(('failure', None))

    def send(self):
        start_ts = time.time()
        url = self.get_request()
        try:
            ret = urllib2.urlopen(url, timeout=30).read()
        except:
            self.record_failure()
        #print ret
        end_ts = time.time()
        #print 'time used ',(end_ts-start_ts), 'for ',url
        self.record(start_ts, end_ts)
        #send out result for analysis

# class RequestSender(object):
#     def __init__(self):
#         pass
#     def send(self):
#         self._start_ts = time.time()
#         ret = urllib2.urlopen(url, timeout=3).read()
#         self._end_ts = time.time()
class MeasureThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._queue = queue
        self._result = {}
        self._total_request = 0
        self._total_failed = 0
        self._total_time = 0

    def run(self):
        while True:
           result = self._queue.get()
           #print 'measure result ',result
           if result[0] == 'failure':
                self._total_failed =self._total_failed + 1
                continue
           start = result[0] * 1000
           end = result[1] * 1000
           duration = int(end - start)

           self._total_time = self._total_time + duration
           self._total_request = self._total_request + 1
           
           idx = duration / 50 + 1   #50ms
           #print 'measure duration ', duration, idx
           if not self._result.get(idx):
                self._result[idx] = 1
           else:
                self._result[idx] = self._result[idx] + 1

           self.dump()

    def dump(self):
        if self._total_request == 0:
            return
        if self._total_request % 500 != 0:
            return
        print ('result for total request %d, %d failed, %d ms used'%(self._total_request,self._total_failed,self._total_time))
        r = self._result
        sorted_result = [(k, r[k]) for k in sorted(r.keys())]
        for i in sorted_result:
            print 'response time between ', (i[0]-1)*50, ' and ',i[0]*50,' ms:', i[1]

class ResultRecorder(object):
    def __init__(self):
        self._queue = Queue.Queue()

    def add(self, result):
        #print 'adding result ',result
        self._queue.put(result)

    def start(self):
        t = MeasureThread(self._queue)
        t.start()

class TestLoop(threading.Thread):
    def __init__(self, recorder,num):
        threading.Thread.__init__(self)
        self._recorder = recorder
        self._num = num
        pass
    def run_tight_loop(self):
        requests = Requests(1, 5, 'http://10.18.207.107:8091/search/api/getResult?type=0&start=0&rows=35&search_key=', self._recorder)
        for i in range(self._num):
            #print 'starting test ', i
            requests.send()
    def run(self):
        self.run_tight_loop()


g_result_queue = Queue
if __name__ == '__main__':
    threadnum = 100
    loopnum = 1000
    r = ResultRecorder()
    r.start()
    for i in range(threadnum):
       tl = TestLoop(r,loopnum)
       tl.start()

