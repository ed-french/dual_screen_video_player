import cv2

FILENAME="media/test.mp4"
COUNTDOWN="media/countdown.mp4"
# def playVideo():
#     cv2.namedWindow("Empty Window", cv2.WINDOW_NORMAL)


#     cv2.resizeWindow("Empty Window", 270, 480)
    
     
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#     playVideo()

KINGS_HALL={"fullscreen_width":1024,"fullscreen_height":int(1024/16*9),"fullscreen_x_offset":-1024,"fullscreen_y_offset":630}


KEY_RIGHT_CODE=2555904
KEY_LEFT_CODE=2424832

class Player:
    def __init__(self,filename):
        self.filename=filename
        self.frame_no:int=0
        self.frame_noplaying:bool=False
        self.cap=None
        self.length_frames=-1



    def reset(self):
        self.playing=False
        self.frame_no=0
        self.cap=cv2.VideoCapture(self.filename)
        self.length_frames=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @staticmethod
    def wait_for(ordinal):
        while True:
            key=cv2.waitKey(25) & 0xFF
            if  key==ordinal:
                break




    def play_clip(self,fullscreen_width=1920,fullscreen_height=1080,fullscreen_x_offset=-1920,fullscreen_y_offset=630,supress_second_monitor=False,last_frame=None)->bool:
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
                width  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)#
                    
                   # cv2.CV_CAP_PROP_FRAME_WIDTH)   # float `width`
                height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
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
                        cv2.resizeWindow(capname, fullscreen_width, fullscreen_height)
                        cv2.imshow(capname, frame) 





                    controlwin="CTRL"
                    cv2.namedWindow(controlwin,cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(controlwin,int(width),int(height))

                    proportion=self.frame_no/self.length_frames

                    propx=int((width-5)*proportion)
                    propxplus=int(propx+5)

                    cv2.rectangle(frame,(propx,int(0)),(propxplus,int(height-1)),(255,255,0),3)


                    cv2.imshow(controlwin,frame)
                    
            # Press Q on keyboard to exit 
            fullpress=cv2.waitKeyEx(25)
            key= fullpress & 0xFF
            print(self.frame_no,fullpress,key)
            if  key== ord('q') or key==27: 
                break
            elif key== ord('s'):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0-1)
                self.frame_no=0
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

            elif key ==32:
                # Pausing until released
                self.wait_for(0xFF)
                self.playing=not self.playing

                        


        
  
        
        # When everything done, release 
        # the video capture object 
        self.cap.release() 
        
        # Closes all the frames 
        cv2.destroyAllWindows() 
        return True # Ended normally


while True:
    clip=Player(COUNTDOWN)
    clip.reset()

    res=clip.play_clip(last_frame=30*11,supress_second_monitor=True)
    if not res:
        break

    clip=Player(FILENAME)
    clip.reset()
    res=clip.play_clip(**KINGS_HALL)
    if not res:
        break