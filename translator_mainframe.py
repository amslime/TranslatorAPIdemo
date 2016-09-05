#coding=utf-8
from Tkinter import *
import translator_languages
from translator_API_caller import TranslateHandler
FONT = '黑体'
VIEW_LOCALE = 'zh-Hans'
INIT_FROM = "英语"
INIT_TO = "英语"
CLIENT_ID = 'YOUR_ID'
CLIENT_SECRET = 'YOUR_SECRET'

class TranslateFrame:
    def __init__(self):
        self.root = Tk()
        self.root.title("在线实时翻译v0.01")
        self.root.geometry('600x400')

        Label(self.root, text='实时翻译API调用', font=(FONT, 20)).pack()
        self.load_support()
        self.frm = Frame(self.root)
        
        #Left

        self.frm_L = Frame(self.frm)
        self.frm_LT = Frame(self.frm_L)
        self.var_char = StringVar()
    
        Label(self.frm_LT, text = '待翻译的语言', font =(FONT,12)).pack(side=LEFT)
        self.frm_LT.pack()

        self.var_L = StringVar()
        self.lb_from = Listbox(self.frm_L, selectmode=SINGLE, listvariable=self.var_L, font =(FONT,12), width=10, height=18)
        self.lb_from.bind('<ButtonRelease-1>', self.set_from_language,)
        for (k, v) in self.trans_from.iteritems():
            self.lb_from.insert(END, k)
        self.scrl_char = Scrollbar(self.frm_L)
        self.scrl_char.pack(side=RIGHT, fill=Y)
        self.lb_from.configure(yscrollcommand = self.scrl_char.set)
        self.lb_from.pack(side=LEFT, fill=BOTH)
        self.scrl_char['command'] = self.lb_from.yview

        self.frm_L.pack(side = LEFT)

        #Mid
        self.frm_M = Frame(self.frm)
        self.frm_M_FROM = Frame(self.frm_M)
        Label(self.frm_M_FROM, text = '识别文本:', font =(FONT,12)).pack(side=LEFT)
        self.from_label = Label(self.frm_M_FROM, text = INIT_FROM, font =(FONT,12))
        self.from_label.pack(side=LEFT)
        self.frm_M_FROM.pack(side=TOP)
        self.detected_text = Text(self.frm_M, width=30, height=6, font =(FONT,15))
        self.detected_text.insert('1.0', '')
        self.detected_text.pack()

        self.frm_M_TO = Frame(self.frm_M)
        Label(self.frm_M_TO, text = '翻译文本:', font =(FONT,12)).pack(side=LEFT)
        self.to_label = Label(self.frm_M_TO, text = INIT_TO, font =(FONT,12))
        self.to_label.pack(side=LEFT)
        self.frm_M_TO.pack(side=TOP)
        self.translated_text = Text(self.frm_M, width=30, height=6, font =(FONT,15))
        self.translated_text.insert('1.0', '')
        self.translated_text.pack()

        self.frm_MB = Frame(self.frm_M)
        Button(self.frm_MB, text="清除", command=self.clear_text, width=6, height=1, font=(FONT,10)).pack(side=LEFT)
        self.frm_MB.pack(side=BOTTOM)

        self.frm_M.pack(side=LEFT)

        #Right
        self.frm_R = Frame(self.frm)
        self.frm_RT = Frame(self.frm_R)
        self.var_int = StringVar()
        Label(self.frm_RT, text='要翻译的语言', font =(FONT,12)).pack(side=RIGHT)
        self.frm_RT.pack()
        
        self.var_R = StringVar()
        self.lb_to = Listbox(self.frm_R, selectmode=SINGLE, listvariable=self.var_R, font =(FONT,12), width=10, height=18)
        self.lb_to.bind('<ButtonRelease-1>', self.set_to_language,)
        for (k, v) in self.trans_to.iteritems():
            self.lb_to.insert(END, k)
        self.scrl_int = Scrollbar(self.frm_R)
        self.scrl_int.pack(side=RIGHT, fill=Y)
        self.lb_to.configure(yscrollcommand = self.scrl_int.set)
        self.lb_to.pack(side=LEFT, fill=BOTH)
        self.scrl_int['command'] = self.lb_to.yview

        self.frm_R.pack(side = LEFT)

        #BOTTOM
        self.frm_B = Frame(self.root)
        self.frm_BL = Frame(self.frm_B)
        self.start_button = Button(self.frm_BL, text="重新翻译", command=self.start_record, width=12, height=1, font=(FONT,10))
        self.start_button.pack(side=LEFT)
        self.frm_BL.pack(side=LEFT)
        self.frm_BR = Frame(self.frm_B)
        self.end_button = Button(self.frm_BR, text="停止录制", command=self.stop_record, width=12, height=1, font=(FONT,10))
        self.end_button.pack(side=RIGHT)
        self.end_button.configure(state=DISABLED)
        self.frm_BR.pack(side=RIGHT)
        self.frm_B.pack(side = BOTTOM)
        
        #PACK
        self.api_handler = TranslateHandler(self, CLIENT_ID, CLIENT_SECRET)
        self.frm.pack()

        self.is_recording = False

    def load_support(self):
        data = translator_languages.get_supported_languages('speech,text', locale=VIEW_LOCALE)
        self.trans_from = {}
        for k, v in data['speech'].iteritems():
            self.trans_from[v['name']] = k
        self.trans_to = {}
        for k, v in data['text'].iteritems():
            self.trans_to[v['name']] = k
        
    def clear_text(self):
        self.detected_text.delete('1.0', END)
        self.translated_text.delete('1.0', END)
    def start_record(self):
        self.is_recording = True
        self.start_button.configure(state=DISABLED)
        self.api_handler.try_start_record()
    def stop_record(self):
        self.is_recording = False
        self.end_button.configure(state=DISABLED)
        self.api_handler.try_stop_record()
    def show(self):
        self.root.mainloop()
    def set_from_language(self, event):
        if (not self.is_recording):
            ans = self.lb_from.get(self.lb_from.curselection())
            self.from_label.configure(text=ans)
    def set_to_language(self, event):
        if (not self.is_recording):
            ans = self.lb_to.get(self.lb_to.curselection())
            self.to_label.configure(text=ans)
    def get_from_id(self):
        k = self.from_label.cget("text")
        return self.trans_from[k]
    def get_to_id(self):
        k = self.to_label.cget("text")
        return self.trans_to[k]
    def insert_final(self, from_text, to_text):
        self.detected_text.insert(END, from_text)
        self.translated_text.insert(END, to_text)
        

if __name__== "__main__":
    frame = TranslateFrame()
    frame.show()
