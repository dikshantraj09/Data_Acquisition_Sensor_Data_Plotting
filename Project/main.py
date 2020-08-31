import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
#from scipy.integrate import cumtrapz
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
import Client
from kivy.clock import Clock
import os,sys,string,time
from plyer import vibrator
from jnius import autoclass
from plyer import gyroscope
from plyer import gravity
from plyer import accelerometer
from plyer import orientation

#from android.permissions import request_permissions, Permission
#request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

kivy.require("1.10.1")

orientation.set_sensor(mode='any')
class ConnectPage(GridLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        accelerometer.enable()
        gyroscope.enable()
        gravity.enable()
        self.cols = 2  
        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt","r") as f:
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]
        else:
            prev_ip = ''
            prev_port = ''
            prev_username = ''

        self.add_widget(Label(text='IP:',font_size=60))  
        self.ip = TextInput(text=prev_ip, multiline=False,font_size=40)  
        self.add_widget(self.ip) 
        self.add_widget(Label(text='Port:',font_size=60))
        self.port = TextInput(text=prev_port, multiline=False,font_size=40)
        self.add_widget(self.port)

        self.add_widget(Label(text='Username:',font_size=60))
        self.username = TextInput(text=prev_username, multiline=False,font_size=40)
        self.add_widget(self.username)

        self.join = Button(text="Join",font_size=60)
        self.join.bind(on_press=self.join_button)
        self.add_widget(Label())  
        self.add_widget(self.join)

    def join_button(self, instance):
        port = self.port.text
        ip = self.ip.text
        username = self.username.text
        with open("prev_details.txt","w") as f:
            f.write(f"{ip},{port},{username}")
        #print(f"Joining {ip}:{port} as {username}")
        info = f"Joining {ip}:{port} as {username}"
        sensor_app.info_page.update_info(info)

        if port.isalnum() :
           
            sensor_app.screen_manager.current = 'Info'
            Clock.schedule_once(self.connect, 1)
        else:
            vibrator.vibrate(0.05)
            sensor_app.screen_manager.current = 'Connect'
            content = Button(text='Close')
            popup = Popup(title="Error No Input !",content=content, auto_dismiss=False, size_hint=(None, None), size=(400, 300))
            content.bind(on_press=popup.dismiss)
            popup.open()
   
    def connect(self, _):

        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text
       
        if not Client.connect(ip, port, username,show_error):
            return 

        # Create chat page and activate it
        sensor_app.create_chat_page()
        sensor_app.screen_manager.current = 'Chat'

class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        accelerometer.enable()
        gyroscope.enable()
        gravity.enable()
        self.cols = 1
        self.AcceX=''
        self.AcceY=''
        self.AcceZ=''
        self.gryX=''  
        self.gryY='' 
        self.gryZ=''     
        self.graX=''  
        self.graY='' 
        self.graZ='' 

        self.event=Clock.schedule_interval(self.update, 1.0/10)
        self.event()
        self.add_widget(Label(text="SENDING ACCELEROMETER DATA...", font_size=60))
        self.add_widget(Label(text="Press STOP to stop sending accelerometer data", font_size=30))
        
        self.stop = Button(text="STOP",font_size=60, size_hint_y=None, height=100)
        self.stop.bind(on_press=self.stop_client)  
        self.add_widget(self.stop)

        self.back = Button(text="Back",font_size=60, size_hint_y=None, height=100)
        self.back.bind(on_press=self.backbutton)  
        self.add_widget(self.back)
    def backbutton(self,instance):
        self.event.cancel()
        sensor_app.screen_manager.current = 'Connect'
        Client.closesocket()
    def stop_client(self,instance):
        self.event.cancel()
        accelerometer.disable()
    def update(self,dt):   
        
       
        self.AcceX="%d"%(accelerometer.acceleration[0]-gravity.gravity[0])
        self.AcceY=",%d"%(accelerometer.acceleration[1]-gravity.gravity[1])
        self.AcceZ=",%d"%(accelerometer.acceleration[2]-gravity.gravity[2])
        
        self.gryX=",%d"%(gyroscope.rotation[0])
        self.gryY=",%d"%(gyroscope.rotation[1])
        self.gryZ=",%d"%(gyroscope.rotation[2])
        self.graX=",%d"%(gravity.gravity[0])
        self.graY=",%d"%(gravity.gravity[1])
        self.graZ=",%d"%(gravity.gravity[2])
        message = self.AcceX+self.AcceY+self.AcceZ+self.gryX+self.gryY+self.gryZ+self.graX+self.graY+self.graZ
        Client.send(message)
    
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1

        
        self.message = Label(halign="center", valign="middle", font_size=60)

        
        self.message.bind(width=self.update_text_width)

        self.add_widget(self.message)
        self.back = Button(text="Back",font_size=60, size_hint_y=None, height=100)
        self.back.bind(on_press=self.backbutton)  
        self.add_widget(self.back)
    def backbutton(self,instance):
        sensor_app.screen_manager.current = 'Connect'
   
    def update_info(self, message):
        self.message.text = message

    
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


class EpicApp(App):
    def build(self):

        
        self.screen_manager = ScreenManager()

        
        self.connect_page = ConnectPage()
        screen = Screen(name='Connect')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

    
        self.info_page = InfoPage()
        screen = Screen(name='Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name='Chat')
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)



def show_error(message):
    sensor_app.info_page.update_info(message)
    sensor_app.screen_manager.current = 'Info'
    #Clock.schedule_once(sys.exit, 10)



if __name__ == "__main__":
    sensor_app = EpicApp()
    sensor_app.run()