import pyaudio
import wave
import numpy as np
import time
import threading
import os
from AttributeDict import AttributeDict

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = int(48000)
CHUNK = 512
recursion = 0

def test_inputs():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
                name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                if "USB Audio" in name:
                    print(name)
                    return i
    return -1

 
def start(path, filename, gdict, input_dev = -1):
    file_name = os.path.join(path, filename)
    audio = pyaudio.PyAudio()
    # start Recording
    info = audio.get_host_api_info_by_index(0)
    global recursion
    usb = test_inputs()
    if input_dev < 0 and usb > 0:
        input_dev = usb
    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK, input_device_index = input_dev)
    except Exception as e:
        print(e)
        time.sleep(1)
        recursion += 1
        if recursion < 10:
            start(path, filename, gdict, input_dev)
        return
    
    waveFile = wave.open(file_name, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    maxValue = 2**16
 
    i = 0
    frames = []
    try:
        print("Audio record start")
        while True:
            data = stream.read(CHUNK, exception_on_overflow = False)
            waveFile.writeframes(data)
            numpydata = np.fromstring(data, dtype=np.int16)
            frames.append([time.time(), data])
            i += 1
            if i%1000 == 0:
                dataL = numpydata[0::2]
                dataR = numpydata[1::2]
                peakL = np.abs(np.max(dataL)-np.min(dataL))/maxValue
                peakR = np.abs(np.max(dataR)-np.min(dataR))/maxValue
                print("L:%00.02f R:%00.02f"%(peakL*100, peakR*100))
            if gdict.stop:
                break
        
        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        waveFile.close()

        frames = np.array(frames)
        file_name = os.path.join(path, "audio.npy")
        np.save(file_name, frames)
        print("Audio record stop")
    except Exception as e:
        print(e)
        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        waveFile.close()

        frames = np.array(frames)
        file_name = os.path.join(path, "audio.npy")
        np.save(file_name, frames)

        rec_folder = path + r'/'.format(str(time.time())) 
        if not os.path.exists(rec_folder):
            os.makedirs(rec_folder)
        filename =  "audio.wav"

        time.sleep(1)
        recursion += 1
        if recursion < 10:
            start(rec_folder, filename, gdict, input_dev)
