from fifo import Fifo
from led import Led
import time
from machine import UART,Pin,I2C,Timer,ADC
from ssd1306 import SSD1306_I2C
import math
from oled import oled
from heart_rate import CalculateHeartRate

class Encoder:
    def __init__(self,rot_a,rot_b,rot_push):
        self.a = Pin(rot_a, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(rot_b, mode = Pin.IN, pull = Pin.PULL_UP)
        self.push = Pin(rot_push, mode = Pin.IN, pull = Pin.PULL_UP)
                
        self.fifo = Fifo(100, typecode='i')
        self.a.irq(handler = self.switch_handler, trigger = Pin.IRQ_RISING, hard = True)
        self.push.irq(handler = self.press_handler, trigger = Pin.IRQ_RISING, hard = True)
        self.last_press = 0
        self.choice_turn = 2
        self.current_choice = 0
        self.menu_items = ['1.Measure HRV','2.Basic Analysis','3.Kubios','4.History']
               
    def press_handler(self,pin):
        current_press = time.ticks_ms()
        if current_press - self.last_press > 300:
            self.last_press = current_press
            self.fifo.put(0)

    def switch_handler(self,pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)
    
    def show_menu(self):
        choice_icon = '>'
        
        oled.fill(0)
        x = 0
        y = 5
        gap = 15
        
        for i in range(len(self.menu_items)):
            if i == self.current_choice:
                display_icon = choice_icon
            else:
                display_icon = ''
            display_text = display_icon + '' + self.menu_items[i]
            oled.text(display_text,x,y,1)        
            y += gap
        
        oled.show()
      
    def choose_function(self):
        choice_turn = None
        if self.fifo.has_data():
            choice_turn = self.fifo.get() # 1,0,-1
            #print(choice_turn)
            self.current_choice += choice_turn
            if self.current_choice > 3:
                self.current_choice = 3
            elif self.current_choice < 0:
                self.current_choice = 0
            #print(self.current_choice)
            self.show_menu()           
        return choice_turn, self.current_choice
        #else:
         #   return None, self.current_choice
    
    # only get the choice from encoder without refreshing the oled menu
    def choose_function_no_refresh(self):
        choice_turn = None
        if self.fifo.has_data():
            choice_turn = self.fifo.get() # 1,0,-1
            #print(choice_turn)
            self.current_choice += choice_turn
        return choice_turn
        #else:
         #   return None, self.current_choice
    
    def welcome(self):
        oled.fill(0)
        oled.text("Welcome to",0,0,1)
        oled.text("Heart Sense",0,12,1)
        oled.text("Press to ",0,24,1)
        oled.text("Continue ^_^",0,36,1)
        oled.text("This ==>",60,55,1)
        oled.show()
        
        start_time = time.ticks_ms()
        while True:
            if self.fifo.has_data():
                self.choice_turn = self.fifo.get()
                if self.choice_turn == 0:
                    break
            
            # if ueser does not press the button for 10 seconds, automatically go to menu
            #if time.ticks_diff(time.ticks_ms(),start_time)>10000:
            #    break
                
        self.show_menu()
            
    def start_end_measure(self):
        # cal_hr = CalculateHeartRate()
        oled.fill(0)
        oled.text("PRESS to", 10,15,1)
        oled.text("Start/Stop", 10,30,1)
        oled.text("Measuring",10,45,1)
        oled.show()
        # while True:
        #     cal_hr.main()

#for testing   
#rot = Encoder(10,11,12)
#rot.show_menu()

#while True:
#    choice_turn, current_choice = rot.choose_function() 
#    time.sleep(0.1)
