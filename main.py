from piotimer import Piotimer
import time
from oled import oled
from basic_analysis import Basic_Analysis
from menu import Encoder
from heart_rate import CalculateHeartRate
from kubios import send_to_kubios,save_history
import ujson

rot = Encoder(10, 11, 12)
rot.welcome()
entered_first_option = False
hr_measurement = None
# for basic analysis and kubios analysis, minimum 30 seconds is required
seconds_limit = 30
# show countdown timer when measuring
timer_sec = 0

def render_history(lines, selection):
    oled.fill(0)
    # read from history file, max 5 records will be displayed
    last_lines = lines[-5:]
    for index,line in enumerate(last_lines):
            record = ujson.loads(line)
            date = record.get("Date")
            time = record.get("Time")
            display_text = f"{index+1}.{date} {time}"
            if index == selection:
                oled.text('>'+display_text, 0, (index+1) * 10, 1) 
            else:
                oled.text(display_text, 0, (index+1) * 10, 1) 
    oled.show()

def display_history_menu():
    selection = 0
    oled.fill(0)
    try:
        with open('history.txt', 'r') as f:
            lines = f.readlines()

        render_history(lines, selection)       
        # read from history file, max 5 records will be displayed 
        length = len(range(min(5, len(lines))))        
        while True:
            choice = rot.choose_function_no_refresh()
            if choice == -1:
                selection += -1
                if selection < 0:
                    selection = 0
                render_history(lines, selection)
            elif choice == 1:
                selection += 1
                if selection >= length:
                    selection = length - 1
                render_history(lines, selection)
            elif choice == 0:
                # select history
                selected = selection
                oled.fill(0)
                json_dump = ujson.loads(lines[selection])
                #print(json_dump)
                index = 0
                for i in json_dump:
                    # show rest of the record except date and time
                    if i != 'Date' and i != 'Time':
                        print(i)
                        display_text = i + ': ' + str(json_dump[i])
                        oled.text(display_text, 0, index * 10, 1)
                        index += 1
                oled.show()
                return                       
    except Exception as e:
        oled.text("No history found", 0, 0, 1)
        print("Error:", e)

    oled.show()

# countdown timer when measuring
def clock(saana):
    global timer_sec, hr_measurement
    timer_sec += 1
    if hr_measurement.isAnalyzing:
        timer_sec = 0
    if hr_measurement.should_reset_timer:
        timer_sec = 0
        hr_measurement.should_reset_timer = False

def main():
    global timer_sec, hr_measurement, seconds_limit
    hr_measurement = CalculateHeartRate()
    tmr = None
    tmr_sec = None
    while True:
        action, choice = rot.choose_function()
        
        if choice == 0 and action == 0:
            # first option, live heart rate measurement without analysis
            rot.start_end_measure()
            while True:
                action = rot.choose_function_no_refresh()
                if choice == 0 and action == 0:
                    tmr = Piotimer(mode = Piotimer.PERIODIC, freq=hr_measurement.sample_rate, callback=hr_measurement.handler)
                    break
            while True:
                action = rot.choose_function_no_refresh()
                if action ==0:
                    tmr.deinit()
                    rot.show_menu()
                    break
                hr_measurement.main()
                
        elif choice == 1 and action == 0:
            # second option
            tmr_sec = Piotimer(mode = Piotimer.PERIODIC, freq=1, callback=clock)
            # start measuring screen
            rot.start_end_measure()
            # wait until user press start
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    tmr = Piotimer(mode = Piotimer.PERIODIC, freq=hr_measurement.sample_rate, callback=hr_measurement.handler)
                    break
            # start the main program, until action == 0 (user press the button), or timer >= limit
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    tmr.deinit()
                    tmr_sec.deinit()
                    timer_sec = 0
                    rot.show_menu()
                    main()
                    break
                if timer_sec >= seconds_limit:
                    break
                if timer_sec == 0:
                    hr_measurement.main()
                else:
                    hr_measurement.main(timer_sec = (seconds_limit - timer_sec))

            # start basic analysis
            basic_analysis = Basic_Analysis()
            basic_analysis.get_result(hr_measurement.intervals[4:])
            # print intervals for debugging
            print(hr_measurement.intervals)

            # wait until user press the button again to return to the menu page
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    tmr.deinit()
                    tmr_sec.deinit()
                    timer_sec = 0
                    rot.show_menu()
                    main()
                    break
        
        elif choice == 2 and action == 0:
            # third option
            tmr_sec = Piotimer(mode = Piotimer.PERIODIC, freq=1, callback=clock)
            # start measuring screen
            rot.start_end_measure()
            # wait until user press start
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    tmr = Piotimer(mode = Piotimer.PERIODIC, freq=hr_measurement.sample_rate, callback=hr_measurement.handler)
                    break
            # start the main program, until action == 0 (user press the button), or timer >= limit
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    tmr.deinit()
                    tmr_sec.deinit()
                    timer_sec = 0
                    rot.show_menu()
                    main()
                    break
                if timer_sec >= seconds_limit:
                    break
                if timer_sec == 0:
                    hr_measurement.main()
                else:
                    hr_measurement.main(timer_sec = (seconds_limit - timer_sec))

            # start kubios analysis
            history = send_to_kubios(hr_measurement.intervals[4:])
            save_history(history)
            print(history)
            # print intervals for debugging
            #print(hr_measurement.intervals)

            # wait until user press the button again to return to the menu page
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    tmr.deinit()
                    tmr_sec.deinit()
                    timer_sec = 0
                    rot.show_menu()
                    main()
                    break     
        
        elif choice == 3 and action == 0:
            display_history_menu()
            while True:
                action = rot.choose_function_no_refresh()
                if action == 0:
                    timer_sec = 0
                    rot.show_menu()
                    main()
                    break           

main()





