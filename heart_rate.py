from machine import UART,Pin,I2C,Timer,ADC
from piotimer import Piotimer
from fifo import Fifo
import time
import micropython
from led import Led
from oled import oled

micropython.alloc_emergency_exception_buf(200)

class CalculateHeartRate:
    def __init__(self):
        self.adc = ADC(Pin(27))
        self.samples_unsmoothed = Fifo(25)
        self.samples = Fifo(500)
        self.sample_rate = 250
        
        self.peak_led = Led(22, Pin.OUT)
        self.peak_led.off()
        
        self.sample_index = 0 # to record where is the peak
        self.two_second_counter = 0
        
        self.previous_value = 0        
        self.current_value = 0
        
        self.peak_area_in = False 
        self.peak_found = False # only if value over th, peakfound procedure start
        self.intervals = [1] # store intervals
        self.last_peak_time = time.ticks_ms()
        self.previous_interval = 1
        
        self.threshold_high = self.threshold_low = 0
        self.max_value = 0
        self.min_value = 0
        self.height = 0
        
        self.scale_counter = 0 
        self.scale_step = 5
        self.sum_every_five_sample = 0
        self.scaled_history = [0] * 128
        self.sample_average = 0

        self.isAnalyzing = False

        self.should_reset_timer = False

    def average(self, numbers):
        if not numbers:
            raise ValueError("Not a number")
        return sum(numbers) / len(numbers)
                        
    def handler(self, timer):
        try:
            #print("Timer triggered")
            self.samples_unsmoothed.put(self.adc.read_u16())
        except RuntimeError:
            pass

    def collect_data(self):
        if self.samples_unsmoothed.has_data():
            self.samples.put(int(self.average(self.samples_unsmoothed.data)))
            self.samples_unsmoothed.get()
            self.previous_value = self.current_value
            self.current_value = self.samples.get()
            self.sample_index += 1
            self.two_second_counter += 1
            return True
        return False
        
    def set_threshold(self):
        if self.two_second_counter >= 250: 
            self.two_second_counter = 0 
            self.max_value = max(self.samples.data)
            self.min_value = min(self.samples.data)
            self.height = self.max_value - self.min_value
            self.threshold_high = int(self.min_value + 0.75 * self.height)
            self.threshold_low = int(self.min_value + 0.5 * self.height)
        return self.threshold_high, self.threshold_low
    
    def is_valid_ppi(self, ppi_ms, baseline_ppi_ms, bpm_tolerance=15):
        baseline_bpm = 60000 / baseline_ppi_ms
        min_bpm = baseline_bpm - bpm_tolerance
        max_bpm = baseline_bpm + bpm_tolerance
        min_ppi = 60000 / max_bpm
        max_ppi = 60000 / min_bpm
        return min_ppi <= ppi_ms <= max_ppi
    
    def find_peaks(self):                          
        if not self.peak_area_in:
            if self.current_value > self.threshold_high:
                self.peak_led.on()
                self.peak_area_in = True
                
        else:
            if self.current_value < self.threshold_low:
                self.peak_led.off()
                self.peak_area_in = False
                self.peak_found = False
           
        if self.peak_area_in and not self.peak_found:
            if self.current_value < self.previous_value:
                now = time.ticks_ms()
                if now-self.last_peak_time > 300:
                    self.peak_found = True
                    self.last_peak_time = now 
                    self.interval = self.sample_index - 1
                    self.ppi_in_milisecond = 4 * self.interval
                    if (4*75) <= self.ppi_in_milisecond <= (4*300):
                        self.intervals.append(int(self.ppi_in_milisecond))
                        if not self.is_valid_ppi(self.ppi_in_milisecond, self.previous_interval):
                            self.should_reset_timer = True
                            self.previous_interval = self.intervals[-1]
                            # self.intervals.pop()
                            self.intervals = [1]
                        if len(self.intervals) > 100:
                            self.intervals.pop(0)
                                                
                    self.sample_index = 0
        return self.intervals
    
    def calculate_bpm(self):             
        if not self.intervals:
            return 0        
        avg_ppi = sum(self.intervals[-3:]) / 3
        if avg_ppi > 0:
            bpm = 60 * 1000 / avg_ppi
        else:
            bpm = 0
        return int(bpm)    
    
    def scale_sample(self):                   
        if self.height > 0: 
            self.sample_scaled =int((self.current_value - self.min_value) * 48 / self.height) #keep space for showing bpm
        else:
            self.sample_scaled = 24
        
        if self.sample_scaled > 48:
            self.sample_scaled = 48
        if self.sample_scaled <0:
            self.sample_scaled = 0
        
        self.scaled_history.pop(0)
        self.scaled_history.append(self.sample_scaled)
        return self.scaled_history
        
    def plot(self, data, bpm, timer_sec = None):
        oled.fill(0)        
        if 40 <= bpm <= 200:
            self.isAnalyzing = False
            display_text = f"{bpm} BPM"
        else:
            self.isAnalyzing = True
            display_text = "-- analyzing"
        oled.text(display_text, 0, 56)        
        for x in range(127):
            y1 = 48 - data[x]
            y2 = 48 - data[x+1]
            oled.line(x, y1, x+1, y2, 1)
        if timer_sec is not None:
            timer_text = str(timer_sec) + 's'
            oled.text(timer_text, 128 - len(timer_text) * 8, 56, 1)
        oled.show()
    
    def main(self, timer_sec = None):
        self.collect_data()
        self.set_threshold()
        self.find_peaks()
        
        if self.two_second_counter % 10 == 0:
            scaled = self.scale_sample()
            current_bpm = self.calculate_bpm()
            self.plot(scaled, current_bpm, timer_sec = timer_sec)
            #print(self.intervals)
 
#data = CalculateHeartRate()
#tmr = Piotimer(mode = Piotimer.PERIODIC, freq=data.sample_rate, callback=data.handler)

#while True:
#   data.main()