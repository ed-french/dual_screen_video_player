import cv2
from flask import Flask,send_file,Response
import threading

FILENAME="media/snowman_nobars.mp4"
COUNTDOWN="media/countdown.mp4"
# def playVideo():
#     cv2.namedWindow("Empty Window", cv2.WINDOW_NORMAL)


#     cv2.resizeWindow("Empty Window", 270, 480)
    
     
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#     playVideo()

KINGS_HALL={"zoom":0.75,"fullscreen_x_offset":-1024,"fullscreen_y_offset":630}
HOME_VGA_TEST={"zoom":0.75,"fullscreen_x_offset":+3000,"fullscreen_y_offset":-30}

ROOM_SPEC=HOME_VGA_TEST

KEY_RIGHT_CODE=2555904
KEY_LEFT_CODE=2424832

CONTROL_MONITOR_ZOOM=0.75

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


IP=get_ip()

class MockPlayer:
    timecode="mm:ss:ff"
    proportion=0.0

g_player=MockPlayer() # Singleton, temporary version to ensure web interface works


class Player:
    def __init__(self,filename,title=""):
        self.filename=filename
        self.frame_no:int=0
        self.frame_noplaying:bool=False
        self.cap=None
        self.length_frames=-1
        self.fps=-1
        self.timecode="??:??:??"
        self.proportion=0.0
        self.pause_requested=False
        self.restart_requested=False
        self.countdown_requested=False
        self.skip_requested=False
        self.title=title



    def reset(self):
        self.playing=False
        self.frame_no=0
        self.cap=cv2.VideoCapture(self.filename)
        self.length_frames=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        # cv2.CV_CAP_PROP_FRAME_WIDTH)   # float `width`
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) ) # float `height`
        self.proportion=0.0
        self.timecode="00:00:00"

    @staticmethod
    def wait_for(ordinal):
        while True:
            key=cv2.waitKey(25) & 0xFF
            if  key==ordinal:
                break




    def play_clip(self,zoom=0.5,fullscreen_x_offset=-1920,fullscreen_y_offset=630,supress_second_monitor=False,last_frame=None)->bool:

        self.playing=True
        if self.cap is None:
            self.reset()
        if (self.cap.isOpened()== False):  
            raise FileNotFoundError()

        while True:
            if not self.cap.isOpened():
                print("Filed ended...!")
                break
            
            if self.playing:
                ret,frame=self.cap.read()

                self.frame_no+=1

                if last_frame is not None and self.frame_no>=last_frame:
                    break


                if ret==True:
                    # Display the resulting frame(s) 


                    if not supress_second_monitor:
                        capname="CAP"
                        
                        cv2.namedWindow(capname, cv2.WND_PROP_FULLSCREEN)
                        
                        cv2.moveWindow(capname, fullscreen_x_offset, fullscreen_y_offset)
                        cv2.setWindowProperty(capname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        cv2.resizeWindow(capname, int(self.width*zoom), int(self.height*zoom))



                        cv2.imshow(capname, frame) 





                    controlwin="CTRL"
                    cv2.namedWindow(controlwin,cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(controlwin,int(self.width*CONTROL_MONITOR_ZOOM),int(self.height*CONTROL_MONITOR_ZOOM))

                    self.proportion=self.frame_no/self.length_frames

                    propx=int(self.width*self.proportion)
                    
                    
                    seconds_in=self.frame_no/self.fps
                    if self.title=="Countdown":
                        seconds_in=self.length_frames/self.fps-seconds_in+1.0
                        
                    
                    whole_secs=int(seconds_in)
                    fraction=int((seconds_in-whole_secs)*100)
                    minutes=int(whole_secs/60)
                    seconds=whole_secs-60*minutes

                    self.timecode=f"{minutes:02}:{seconds:02}:{fraction:02}"


                    cv2.putText(frame,self.timecode,(20,200),0,4,(255,255,0),4)
                    cv2.putText(frame,IP,(20,int(self.height-100)),0,1,(255,0,0),2)
                    cv2.putText(frame,"R=restart, S=Skip, SPACE=pause, Q=Back to countdown, Z=exit",(20,int(self.height-50)),0,1,(255,0,0),2)
                    
                    
                    cv2.rectangle(frame,(0,0),(self.width-1,int(self.height/30-1)),(50,50,50),3)
                    cv2.rectangle(frame,(0,int(0)),(propx,int(self.height/30-1)),(255,255,0),3)


                    cv2.imshow(controlwin,frame)
                    
            # Press Q on keyboard to exit 
            fullpress=cv2.waitKeyEx(25)
            key= fullpress & 0xFF
            print(self.frame_no,fullpress,key)


            # Skip the track

            if  key== ord('s') or key==27: 
                break

            elif g_player.skip_requested:
                g_player.skip_requested=False
                break

            
            # Restart the track

            elif key== ord('r'):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0-1)
                self.frame_no=0

            elif g_player.restart_requested:
                g_player.restart_requested=False
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0-1)
                self.frame_no=0


            # close the application

            elif key == ord('z'):
                self.cap.release()
                cv2.destroyAllWindows()
                return False
            


            elif fullpress==KEY_LEFT_CODE:
                self.frame_no=max(0,self.frame_no-60)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_no-1)
            elif fullpress==KEY_RIGHT_CODE:
                self.frame_no=min(self.length_frames-1,self.frame_no+60)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_no-1)
            
            
            # Toggle pausing playback
            elif key ==32: # Space bar
                # Pausing until released
                self.wait_for(0xFF)
                self.playing=not self.playing

            elif self.pause_requested:
                self.playing=not self.playing
                self.pause_requested=False
                        

            # Back to countdown

            elif self.countdown_requested:
                self.countdown_requested=False
                if self.title=="Countdown":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0-1)
                    self.frame_no=0
                else:
                    g_player.skip_requested=False
                    break


        
  
        
        # When everything done, release 
        # the video capture object 
        self.cap.release() 
        
        # Closes all the frames 
        cv2.destroyAllWindows() 
        return True # Ended normally
    


app=Flask(__name__,
          static_folder="static")
@app.route("/")
def main():
    return send_file("webif.html")

@app.route("/timecode")
def timecode():
    raw=f"""    <div hx-target="this"
        hx-get="/timecode"
        hx-trigger="load delay:200ms"
        hx-swap="outerHTML">
            <div id="title">{g_player.title}</div>
            <span id="timecode">{g_player.timecode}</span>
          <div class="progresscontainer">  
            <div style="width:{g_player.proportion*100}%" class="progressbar"></div>
          </div>  
    </div>"""
    return raw #Response(500,"arghhh!")

@app.route("/pause")
def pause():
    g_player.pause_requested=True
    return   """        <button class="active"
                            accesskey="P"
                            hx-get="/pause"
                            hx-target="this"
                            hx-trigger="click"
                            hx-swap="outerHTML">
            <img class="icon" src="/static/playpause.png">
        </button>"""

@app.route("/restart")
def restart():
    g_player.restart_requested=True
    return """       <button class="active"
                accesskey="R"
                hx-get="/restart"
                hx-target="this"
                hx-trigger="click"
                hx-swap="outerHTML">
                <img class="icon" src="/static/restart.png">
        </button>"""

@app.route("/countdown")
def countdown():
    g_player.countdown_requested=True
    return """        <button class="active"
                accesskey="C"
                hx-get="/countdown"
                hx-target="this"
                hx-trigger="click"
                hx-swap="outerHTML">
                <img class="icon" src="/static/countdown.png">
        </button>"""

@app.route("/skip")
def skip():
    g_player.skip_requested=True



    return """<button class="active"
                    accesskey="S"
                    hx-get="/skip"
                    hx-target="this"
                    hx-trigger="click"
                    hx-swap="outerHTML">
            <img class="icon" src="/static/skip.svg">
        </button>"""

if __name__=="__main__":

    
    # Launch server
    server=threading.Thread(target=app.run,daemon=True,kwargs={"host":"0.0.0.0", "port":80})
    server.start()

    countdown_clip=Player(COUNTDOWN,"Countdown")
    countdown_clip.reset()


    main_clip=Player(FILENAME,"Snowman")
    main_clip.reset()

        
    while True:
        g_player=countdown_clip
        g_player.reset()

        res=g_player.play_clip(last_frame=30*10,supress_second_monitor=True)
        if not res:
            break

        g_player=main_clip
        g_player.reset()
 
        res=g_player.play_clip(**ROOM_SPEC)
        if not res:
            break

