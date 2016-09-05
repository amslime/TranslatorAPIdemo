import os
import sys
import wave
import uuid
import StringIO
import struct
import thread
import time
import websocket
import json
from Tkinter import *
from translator_auth import OAuth
from translator_recorder import TranslateRecorder

def get_wave_header():
    nchannels = 1
    bytes_per_sample = 2
    frame_rate = 16000
    output = StringIO.StringIO()
    output.write('RIFF')
    output.write(struct.pack('<L', 0))
    output.write('WAVE')
    output.write('fmt ')
    output.write(struct.pack('<L', 18))
    output.write(struct.pack('<H', 0x0001))
    output.write(struct.pack('<H', nchannels))
    output.write(struct.pack('<L', frame_rate))
    output.write(struct.pack('<L', frame_rate * nchannels * bytes_per_sample))
    output.write(struct.pack('<H', nchannels * bytes_per_sample))
    output.write(struct.pack('<H', bytes_per_sample * 8))
    output.write(struct.pack('<H', 0))
    output.write('data')
    output.write(struct.pack('<L', 0))

    data = output.getvalue()

    output.close()

    return data


class TranslateHandler:
    def __init__(self, t_frame, c_id, c_secret):
        self.t_frame = t_frame
        self.token_generator = OAuth(c_id, c_secret)
        self.is_recording = False
        self.recorder = TranslateRecorder()

    def on_open(self, ws):
        print 'Connected. Server generated request ID = ', ws.sock.headers['x-requestid']
        def run(*args):
            """Background task which streams audio."""
            headdata = get_wave_header()
            ws.send(headdata, websocket.ABNF.OPCODE_BINARY)
            self.recorder.start()
            print 'You can test your speak now'
            # Stream audio one chunk at a time
            while self.is_recording:
                #sys.stdout.write('.')
                data = self.recorder.pop_chunk()
                if (data <> None):
                    #sys.stdout.write('.')
                    ws.send(data, websocket.ABNF.OPCODE_BINARY)
                time.sleep(0.02)
            ws.keep_running = False;
            #ws.close()
            self.recorder.halt()
            self.t_frame.start_button.configure(state=NORMAL)
            print 'Background thread terminating...'
        
        thread.start_new_thread(run, ())

    def on_close(self):
        print 'connection closed'
        
    def on_data(self, ws, message, message_type, fin):
        if message_type == websocket.ABNF.OPCODE_TEXT:
            data = json.loads(message)
            print '\n', message, '\n'
            if (data['type'] == 'final'):
                self.t_frame.insert_final(data['recognition'], data['translation'])
                
    def on_error(self, ws, error):
        print error

    def try_start_record(self):
        def start_record(*args):
            self.is_recording = True
            self.client_trace_id = str(uuid.uuid4())
            self.translate_from =  self.t_frame.get_from_id()
            self.translate_to = self.t_frame.get_to_id()
            self.features = "Partial"
            self.request_url = "wss://dev.microsofttranslator.com/speech/translate?from={0}&to={1}&features={2}&api-version=1.0".format(self.translate_from, self.translate_to, self.features)
            token = self.token_generator.get_token()
            self.ws_client = websocket.WebSocketApp(
                self.request_url,
                header=[
                    'Authorization: Bearer ' + token,
                    'X-ClientTraceId: ' + self.client_trace_id
                ],
                on_open=self.on_open,
                on_data=self.on_data,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.t_frame.end_button.configure(state=NORMAL)
            self.ws_client.run_forever()
        thread.start_new_thread(start_record, ())

    def try_stop_record(self):
        self.is_recording = False
  
    
    
    

