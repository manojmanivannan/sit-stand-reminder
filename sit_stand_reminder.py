from datetime import datetime
import winsound
import easygui
from time import sleep
import sys, os

try:
   bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
except NameError:
   bundle_dir = os.getcwd()

sit_image = os.path.abspath(os.path.join(bundle_dir,'images/sit_down.png'))
stand_image = os.path.abspath(os.path.join(bundle_dir,'images/stand_up.png'))
walk_image  = os.path.abspath(os.path.join(bundle_dir,'images/walk.png'))

cur_hour = int(datetime.now().hour)
cur_minute = int(datetime.now().minute)
counter_sit_down, counter_stand_up = 0,0
ignored_sit_down_counter, ignored_counter_stand_up = 0,0

def Mbox(title="Health Reminder", text="", style=0,image=None):
    # return ctypes.windll.user32.MessageBoxW(0, text, title, style)
   winsound.Beep(frequency=4000, duration=500)

   try:
      response = easygui.ynbox(text+
                        f"\nSat down {counter_sit_down} times"+
                        f"\nStood up {counter_stand_up} times"+
                        f"\nIgnored to sit {ignored_sit_down_counter} times"+
                        f"\nIgnored to stand {ignored_counter_stand_up} times", 
                        title, ('Done', 'Skip'),
                        image=image)
   except AssertionError:
      return Mbox(title=title, text=text, style=style, image=image)
   
   return response 


# make the script run in loop
# 20 minutes of sitting, 
# 8 minutes of standing and 
# 2 minutes of light walk

while True:

   sleep(1)

   if int(datetime.now().minute) == 0 or int(datetime.now().minute) == 30 :
      if Mbox(title="SIT DOWN",image=sit_image):
         # print('Sat down')
         counter_sit_down+=1
         sleep(61)
      else:
         # print('Ignored to sit down')
         ignored_sit_down_counter+=1
         sleep(61)

   if int(datetime.now().minute) == 20 or int(datetime.now().minute) == 50 :
      if Mbox(title="STAND UP",image=stand_image):
         # print('Stood up')
         counter_stand_up+=1
         sleep(61)
      else:
         # print('Ignored to stand up')
         ignored_counter_stand_up+=1
         sleep(61)

   if int(datetime.now().minute) == 28 or int(datetime.now().minute) == 58 :
      if Mbox(title="WALK",image=walk_image):
         # print('Stood up')
         counter_stand_up+=1
         sleep(61)
      else:
         # print('Ignored to stand up')
         ignored_counter_stand_up+=1
         sleep(61)


