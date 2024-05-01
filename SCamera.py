#This project is gifted with the full opencv2 by "pip install opencv-contrib-python" for less error msgs..
#Once used (datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=13)).strftime("%A %d %B %Y %I:%M:%S%p") (not important)
#Used the latest esp32 cam module with its development board (We can use arduino too) and AI tinkerer, and in compilation I used esp32 cam -> example -> wifi camera and than compiled it.
import cv2
import requests
from playsound import playsound
import datetime

frame1=[]
led_off=True
# ESP32 URL
URL = "http://192.168.0.7"    #Give your esp32 cam ip address here. We can get it on serial monitor defining the number you gived
AWB = True
VidName=datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
location2save='/Desktop/Projects/'+VidName+'.avi'   #Video name and where you want to save it
timer=0
led_intensity=50
show_live=False
resolution=7

try:
    cap = cv2.VideoCapture(URL + ":81/stream")
except:
    print("Problem with the ip address OR THE CAMERA ITSELF!!")
    playsound("/Desktop/Projects/alert.wav")    #Use any type of short wav or mp3 file and play it.
    print("Timer: ",timer)
    timer=timer+1

def set_resolution(url: str, index: int=1, verbose: bool=False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))

        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            requests.get(url + "/control?var=framesize&val={}".format(index))
            print(url + "/control?var=framesize&val={}".format(index))
        else:
            print("Wrong index")
    except:
        print("SET_RESOLUTION: something went wrong")
        playsound("Desktop/Projects/alert.wav")
        print(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
        print("Timer: ",timer)
        timer=timer+1

def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")

def set_gainCeiling(url: str, value: int=1, verbose: bool=False):
    try:
        if value >=0  or value <= 3:
            requests.get(url + "/control?var=gainceiling&val={}".format(value))
    except:
        print("SET_GAINCEILING: something went wrong")
        print("Timer: ",timer)
        timer=timer+1

def set_vflip(url: str, value: int=0, verbose: bool=False):
    try:
        if value ==0 or value ==1:
            requests.get(url + "/control?var=vflip&val={}".format(value))
    except:
        print("SET_VFLIP: something went wrong")
        print("Timer: ",timer)
        timer=timer+1

def set_hmirror(url: str, value: int=0, verbose: bool=False):
    try:
        
        requests.get(url + "/control?var=hmirror&val={}".format(value))
    except:
        print("SET_mirror: something went wrong")
        print("Timer: ",timer)
        timer=timer+1

def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_AWB: something went wrong")
        print("Timer: ",timer)
        timer=timer+1
    return awb

def set_led_intensity(url: str, value: int=0, verbose: bool=False):
    try:
        if value >= 0 and value <=255:
            requests.get(url + "/control?var=led_intensity&val={}".format(value))
    except:
        print("FLASHLIGHT: something went wrong")
        

if __name__ == '__main__':
    try:
        set_resolution(URL, index=resolution)
        set_quality(URL, value=15)
        set_gainCeiling(URL, value=2)
        set_led_intensity(URL,0)
        set_hmirror(URL, value=0)
        set_vflip(URL, value=0)
        frame_width = int(cap.get(3)) 
        frame_height = int(cap.get(4))
        size = (frame_width, frame_height)
        result = cv2.VideoWriter(location2save,  
                            cv2.VideoWriter_fourcc(*'XVID'), 
                            8, size)
        mog = cv2.createBackgroundSubtractorMOG2()
    except:
        playsound("Desktop/Projects/alert.wav")
    while True:

        if cap.isOpened():
            try:
                ret, frame = cap.read()
                
            
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
                fgmask = mog.apply(gray)
        
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                fgmask = cv2.erode(fgmask, kernel, iterations=2)
                fgmask = cv2.dilate(fgmask, kernel, iterations=3)
        
                contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
                cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                if led_off:    
                    cv2.putText(frame, "Led Status: OFF", (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                else:
                    cv2.putText(frame, "Led Status: ON", (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                for contour in contours:
                    # Ignore small contours
                    if cv2.contourArea(contour) < 900:
                        continue
            
                    # Draw bounding box around contour
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
                    result.write(frame)
                    
                if show_live:
                    cv2.imshow('Streaming LIVE!!', frame)


                key = cv2.waitKey(1)

                if key == ord('r'):
                    idx = int(input("Select resolution index: "))
                    set_resolution(URL, index=idx, verbose=True)

                elif key == ord('q'):
                    val = int(input("Set quality (10 - 63): "))
                    set_quality(URL, value=val)

                elif key == ord('a'):
                    AWB = set_awb(URL, AWB)
                
                elif key == ord('l'):
                    if led_off:
                        set_led_intensity(URL,led_intensity)
                        led_off=False
                    else:
                        set_led_intensity(URL,0)
                        led_off=True

                #More options are available in ip_address/status to see them. This option are already too much if you ask me.


                if key == 27:
                    print(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
                    break
                
            except:
                result.release()
                cap.release()
                cv2.destroyAllWindows()
                print(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
                for _ in range(10):
                    playsound("Desktop/Projects/alert.wav")
                    print("Timer: ",timer)
                    timer=timer+1
                    print("Problem inside the cap open function")
                break
        else:
            result.release()
            cap.release()
            cv2.destroyAllWindows()
            print(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
            for _ in range(5):
                playsound("Desktop/Projects/alert.wav")
                print("Timer: ",timer)
                print("CAP is not opend this time")
                timer=timer+1
            break
                
        
    result.release()
    cap.release()
    cv2.destroyAllWindows()
    
