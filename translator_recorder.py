import collections
import threading

from time import sleep
from array import array
from struct import pack
from sys import byteorder

import pyaudio
import wave
import time


THRESHOLD = 500
CHUNK_SIZE = 1000
FORMAT = pyaudio.paInt16
RATE = 16000
MAX_CHUNK_COUNT = 10000
MAX_SILENT_CHUNK_LIMIT = 10

def is_silent(data):
    #Returns 'True' if below the 'silent' threshold
    return max(data) < THRESHOLD

class TranslateRecorder(object):
    def __init__(self):
        self.slient_count = 0
        self.is_active = False
        #make a deque to store and transfer sound in chunk unit 
        self.queue = collections.deque()

        #open a pyaudio stream to read sound stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

        #the thread to record sound wav
        self.record_thread = threading.Thread(target=self.appender)
        self.record_thread.start()
    
    def pop_chunk(self):
        #get and pop the first unhandled chunk data(in order to transfer to speech detector API)  
        if (len(self.queue) > 0):
            return self.queue.popleft()
        return None

    def append_chunk(self, data):
        #append chunk data to the tail of the queue, but avoid too many continues silent chunk be appended
        if (len(self.queue) < MAX_CHUNK_COUNT):
            if (is_silent(data)):
                if (self.silent_count < MAX_SILENT_CHUNK_LIMIT):
                    self.silent_count = self.silent_count + 1
		    self.queue.append(data)
	    else:
		self.queue.append(data)
                self.silent_count = 0

    def appender(self):
        #the way that record thread handles
        while True:
            #read a chunk data repeatly
            if (self.is_active):
                data = self.stream.read(CHUNK_SIZE)
                self.append_chunk(data)
            else:
                time.sleep(0.5)
        
    def halt(self):
        self.is_active = False
        self.queue.clear()

    def start(self):
        self.is_active = True

if __name__ == '__main__':
    recorder_main = TranslateRecorder()
    recorder_main.run()
    sleep(5)
    recorder_main.stop()
    

