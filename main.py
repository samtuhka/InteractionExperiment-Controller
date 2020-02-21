import logger
import tkinter as tk
from tkinter.ttk import Frame
from multiprocessing import Process
import zmq
import msgpack
import marker_display
import AVrecordeR
import time
import os
import audio
import threading
import pygame
from host import AudioServer
import nexus_plot
from AttributeDict import AttributeDict
import collections
import numpy as np
import shimmer3_stream

add1 = '127.0.0.1'
add2 = '169.254.53.156'
port1 = '50020'
port2 = '50020'
mac1 = "00:A0:96:34:EA:23" 
mac2 = "00:A0:96:2F:A8:A6"

#0033
#bt-device -d 00:A0:96:34:EA:23
#0115
#bt-device -d 00:A0:96:2F:A8:A6

session = 0

class GUI(Frame):
  
    def __init__(self):
        super().__init__()
        self.p1 = None  
        self.p2 = None
        self.calibrating = [False, False]
        self.server = AudioServer()
        self.pool = AttributeDict()
            
        self.pool.nexus = AttributeDict()
        self.pool.nexus.bvp = [[np.zeros((30*128)), np.zeros((30*128))], [np.zeros((30*128)), np.zeros((30*128))]]
        self.pool.nexus.eda = [[np.zeros((30*128)), np.zeros((30*128))], [np.zeros((30*128)), np.zeros((30*128))]]
        self.pool.shimmers_running = [False, False, False, False]
        self.pool.stop = [False, False]
        self.pool.plotting = True
        self.shimmer_macs = ["00:06:66:F0:95:13", "00:06:66:F0:95:0F", "00:06:66:F0:94:FE", "00:06:66:F0:94:DC"]
        self.shimmers = [None, None, None, None]
         
        self.initUI()
        self.nexus_plot_thread()
    
    def initUI(self):
      
        self.master.title("Interaction-18 Controller")
        self.pack(fill=tk.BOTH, expand=1)

        reconButton = tk.Button(text="Reconnect Pupils", width=12, command = lambda: self.reconnect())
        reconButton.place(x=450, y=280)

        webcamButton = tk.Button(text="Rec. Audio1", width=12, relief="raised")
        webcamButton = tk.Button(text="Rec. Audio1", width=12, relief="raised", command = lambda: self.webcam_toggle(webcamButton, 1))
        webcamButton.place(x=50, y=50)


        webcamButton1 = tk.Button(text="Rec. Audio2", width=12, relief="raised")
        webcamButton1 = tk.Button(text="Rec. Audio2", width=12, relief="raised", command = lambda: self.webcam_toggle(webcamButton1, 2))
        webcamButton1.place(x=200, y=50)

        button1 = tk.Button(text="Logger 1", width=12, relief="raised")
        button1 = tk.Button(text="Logger 1", width=12, relief="raised", command = lambda: self.log_toggle(button1, 1))
        button1.place(x=50, y=100)

        button2 = tk.Button(text="Logger 2", width=12, relief="raised")
        button2 = tk.Button(text="Logger 2", width=12, relief="raised", command = lambda: self.log_toggle(button2, 2))
        button2.place(x=50, y=150)

        recButton1 = tk.Button(text="Record 1", width=12, relief="raised")
        recButton1 = tk.Button(text="Record 1", width=12, relief="raised", command = lambda: self.rec_toggle(recButton1, 1))
        recButton1.place(x=200, y=100)

        recButton2 = tk.Button(text="Record 2", width=12, relief="raised")
        recButton2 = tk.Button(text="Record 2", width=12, relief="raised", command = lambda: self.rec_toggle(recButton2, 2))
        recButton2.place(x=200, y=150)


        shimmer1 = tk.Button(text="Shimmer1", width=12, relief="raised")
        shimmer1 = tk.Button(text="Shimmer1", width=12, relief="raised", command = lambda: self.rec_shimmer(shimmer1, 0))
        shimmer1.place(x=50, y=200)

        shimmer2 = tk.Button(text="Shimmer2", width=12, relief="raised")
        shimmer2 = tk.Button(text="Shimmer2", width=12, relief="raised", command = lambda: self.rec_shimmer(shimmer2, 1))
        shimmer2.place(x=200, y=200)

        shimmer3 = tk.Button(text="Shimmer3", width=12, relief="raised")
        shimmer3 = tk.Button(text="Shimmer3", width=12, relief="raised", command = lambda: self.rec_shimmer(shimmer3, 2))
        shimmer3.place(x=50, y=250)

        shimmer4 = tk.Button(text="Shimmer4", width=12, relief="raised")
        shimmer4 = tk.Button(text="Shimmer4", width=12, relief="raised", command = lambda: self.rec_shimmer(shimmer4, 3))
        shimmer4.place(x=200, y=250)


        button3 = tk.Button(text="Calibrate Both", width=12,  command = lambda: self.calibrate_both())
        button3.place(x=50, y=350)

        button4 = tk.Button(text="Calib. Subject 1", width=12,  command = lambda: self.calibrate_subjet(req1, 0))
        button4.place(x=50, y=400)

        button5 = tk.Button(text="Calib. Subject 2", width=12,  command = lambda: self.calibrate_subjet(req2, 1))
        button5.place(x=50, y=450)

        accButt1 = tk.Button(text="Verify Both", width=12,  command = lambda: self.calibrate_both(True))
        accButt1.place(x=200, y=350)

        accButt2 = tk.Button(text="Verif. Subject 1", width=12,  command = lambda: self.calibrate_subjet(req1, 0, True))
        accButt2.place(x=200, y=400)

        accButt3 = tk.Button(text="Verif. Subject 2", width=12,  command = lambda: self.calibrate_subjet(req2, 1, True))
        accButt3.place(x=200, y=450)

        l1 = tk.Label(text="Session number")
        self.session = tk.StringVar()
        e1 = tk.Entry(textvariable = self.session)
        self.session.set("Karnevaali1")
        l1.place(x = 50, y = 10)
        e1.place(x = 50, y = 25)

        mac_lab = tk.Label(text="Nexus(1) MAC Add")
        self.mac1 = tk.StringVar()
        mac_entry = tk.Entry(textvariable = self.mac1)
        self.mac1.set(mac1)
        mac_lab.place(x = 450, y = 10)
        mac_entry.place(x = 450, y = 25)


        mac_lab2 = tk.Label(text="Nexus(2) MAC Add")
        self.mac2 = tk.StringVar()
        mac_entry2 = tk.Entry(textvariable = self.mac2)
        self.mac2.set(mac2)
        mac_lab2.place(x = 450, y = 50)
        mac_entry2.place(x = 450, y = 65)


        pup_lab1 = tk.Label(text="Pupil 1 Address")
        self.pupil_address1 = tk.StringVar()
        pup_entry1 = tk.Entry(textvariable = self.pupil_address1)
        self.pupil_address1.set(add1)
        pup_lab1.place(x = 450, y = 100)
        pup_entry1.place(x = 450, y = 115)


        pup_port1 = tk.Label(text="Pupil 1 Port")
        self.pupil_port1 = tk.StringVar()
        pupil_port_entry1 = tk.Entry(textvariable = self.pupil_port1)
        self.pupil_port1.set(port1)
        pup_port1.place(x = 450, y = 140)
        pupil_port_entry1.place(x = 450, y = 155)



        pup_lab2 = tk.Label(text="Pupil 2 Address")
        self.pupil_address2 = tk.StringVar()
        pup_entry2 = tk.Entry(textvariable = self.pupil_address2)
        self.pupil_address2.set(add2)
        pup_lab2.place(x = 450, y = 190)
        pup_entry2.place(x = 450, y = 205)


        pup_port2 = tk.Label(text="Pupil 2 Port")
        self.pupil_port2 = tk.StringVar()
        pupil_port_entry2 = tk.Entry(textvariable = self.pupil_port2)
        self.pupil_port2.set(port2)
        pup_port2.place(x = 450, y = 230)
        pupil_port_entry2.place(x = 450, y = 245)

        graph = tk.Button(text="Plot", width=12, relief="sunken")
        graph = tk.Button(text="Plot", width=12, relief="sunken", command = lambda: self.plot_toggle(graph))
        graph.place(x=200, y=500)



    def rec_shimmer(self,toggle_btn, shimmer):
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            self.pool.shimmers_running[shimmer] = False
        else:
            toggle_btn.config(relief="sunken")
            subj = int(shimmer > 1) + 1
            
            rec_dir = r'sessions/session_{}/shimmers/{}/{}/'.format(self.session.get(), subj, str(time.time())) 
            if not os.path.exists(rec_dir):
                os.makedirs(rec_dir)
            path = rec_dir + "shimmer_{}.txt".format(shimmer)
            self.pool.shimmers_running[shimmer] = True
            self.shimmers[shimmer] = threading.Thread(target=shimmer3_stream.stream, args=(self.pool,self.shimmer_macs[shimmer], shimmer, path))
            self.shimmers[shimmer].start()
            
        
    def plot_toggle(self,toggle_btn):
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            self.pool.plotting = False
        else:
            toggle_btn.config(relief="sunken")
            self.pool.plotting = True


    def notify(self, req, notification):
            """Sends ``notification`` to Pupil Remote"""
            topic = 'notify.' + notification['subject']
            payload = msgpack.dumps(notification, use_bin_type=True)
            req.send_string(topic, flags=zmq.SNDMORE)
            req.send(payload)
            return req.recv_string()       

    def start_calibration(self, req, acc):
        n = {'subject':'start_plugin','name':'Manual_Marker_Calibration', 'args':{}}
        self.notify(req, n)
        if acc:
            n = {'subject':'accuracy_test.should_start'}
        else:
            n = {'subject':'calibration.should_start'}
        
        self.notify(req, n)

    def stop_calibration(self, req, acc):
        if acc:
            n = {'subject':'accuracy_test.should_stop'}
        else:
            n = {'subject':'calibration.should_stop'}
        self.notify(req, n)

    def calibrate_subjet(self, req, sub, acc = False):
         if not(self.calibrating[sub]):
            self.calibrating[sub] = True
            self.start_calibration(req, acc)
            marker_display.start(acc)
            self.stop_calibration(req, acc)
            self.calibrating[sub] = False
            #black_screen()

    def calibrate_both(self, acc = False):
        if not(self.calibrating[0] or self.calibrating[1]):
            self.calibrating[0], self.calibrating[1] = True, True
            self.start_calibration(req1, acc)
            self.start_calibration(req2, acc)
            marker_display.start(acc)
            self.stop_calibration(req1, acc)
            self.stop_calibration(req2, acc)
            self.calibrating[0], self.calibrating[1] = False, False
            #black_screen()

    def set_timebase(self, req, sub):
        t0 = time.time()
        #req.send_string('T 0.0')
        #t = req.recv_string()
        req.send_string('t 0.0')
        t = req.recv_string()
        delay = time.time() - t0
        dirpath = logger.create_dir(sub, self.session.get())
        with open((dirpath + "/pupil_info_{}.txt").format(t0), "w",) as text_file:
          text_file.write("Asked at: %f" % (t0))
          text_file.write("\nPupil timebase: %s" % (t))
          text_file.write("\nRoundtrip delay: %f" % (delay))

    def start_logger(self, subj):
        if subj == 1:
            p = logger.log(req1, self.pupil_address1.get(), subj, self.mac1.get(), self.pool, self.session.get())
            self.p1 = p
            self.pool.stop[subj -1] = False
        else:
            p = logger.log(req2, self.pupil_address2.get(), subj, self.mac2.get(), self.pool, self.session.get())
            self.p2 = p
            self.pool.stop[subj -1] = False

    def rec_toggle(self,toggle_btn, subj):

        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            if subj == 1:
                self.stop_record(req1)
            else:
                self.stop_record(req2)
        else:
            toggle_btn.config(relief="sunken")
            if subj == 1:
                self.record(req1)
                self.set_timebase(req1, subj)
            else:
                self.record(req2)
                self.set_timebase(req2, subj)

    def nexus_plot_thread(self):
        #hr_plot.live_plot(self.pool)
        t = threading.Thread(target=nexus_plot.live_plot, args=(self.pool,))
        t.start()
        return

    def reconnect(self):
        global req1
        req1 = create_socket(self.pupil_address1.get(), self.pupil_port1.get())
        global req2
        req2 = create_socket(self.pupil_address2.get(), self.pupil_port2.get())

    def webcam_toggle(self,toggle_btn, subj):
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            #AVrecordeR.stop_AVrecording(self.filename, self.rec_folder)
            if subj == 1:
                self.gdict_1.stop = True
            else:
                self.server.stop = True
                #self.gdict_2.stop = True
                #self.server.stop.set()
        else:
            self.rec_folder = r'sessions/session_{}/audio/{}/{}/'.format(self.session.get(), subj, str(time.time())) 
            if not os.path.exists(self.rec_folder):
                os.makedirs(self.rec_folder)


            self.filename =  "audio.wav"
            toggle_btn.config(relief="sunken")
            if subj == 1:
                self.gdict_1 = audio.AttributeDict({"stop": False})
                t = threading.Thread(target=audio.start, args=(self.rec_folder, self.filename, self.gdict_1, 6,))
                t.start()
            else:
                print(self.rec_folder)
                self.server.rec_folder = self.rec_folder
                self.server.filename = self.filename
                self.server.start = True
                #self.gdict_2 = audio.AttributeDict({"stop": False})
                #t = threading.Thread(target=audio.start, args=(self.rec_folder, self.filename, self.gdict_2, 6,))

            #AVrecordeR.start_AVrecording(self.filename, self.rec_folder)

    def log_toggle(self,toggle_btn, subj):

        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            #if subj == 1:  
            #    self.p1[1].terminate()
            #else:
            #    self.p2[1].terminate()
            self.pool.stop[subj - 1] = True
        else:
            toggle_btn.config(relief="sunken")
            self.start_logger(subj)

    def stop_record(self, req):
        n = {'subject': 'recording.should_stop'}
        self.notify(req, n)

    def record(self, req):
        n = {'subject': 'recording.should_start', 'session_name': 'session_' + self.session.get()}
        self.notify(req, n)

def create_socket(address, port):
    ctx = zmq.Context()
    req = ctx.socket(zmq.REQ)
    req.connect('tcp://{}:{}'.format(address, port))
    return req

def black_screen(pos):
    position = 0, 0
    WIDTH = 1920
    HEIGHT = 1080
    os.environ['SDL_VIDEO_WINDOW_POS'] = str(position[0]) + "," + str(position[1])
    pygame.display.init()
    windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME, 32)
    images = []
    s = 150
    locs = [(0,0), [1920*0.5 - 0.5*s, 0], (1920 - s,0), (0, 1080*0.5 - 0.5*s), (1920 - s, 1080*0.5 - 0.5*s), (0, 1080 - s), (1920 - s, 1080 - s)]
    for i in range(7): 
        img = pygame.image.load("markers/{}_marker.png".format(i))
        img = pygame.transform.smoothscale(img, (s,s))
        images.append(img)
    while True:
        windowSurface.fill((70,70,70))
        for i, img in enumerate(images):
            windowSurface.blit(img, (locs[i][0],locs[i][1]))
        pygame.display.flip()
        pygame.time.wait(100)

def main():
    #proc1 = Process(target=black_screen, args=(1920,))
    #proc1.start()

    global req1
    req1 = create_socket(add1, port1)
    global req2
    req2 = create_socket(add2, port2)

    root = tk.Tk()
    root.geometry("800x550+300+300")
    app = GUI()
    root.mainloop()  

if __name__ == '__main__':
    main()   
