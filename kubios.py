from mqtt_kubios import kubios_mqtt_request,MQTTConnectionError
from oled import oled
import ujson

from menu import Encoder

rot = Encoder(10, 11, 12)

def send_to_kubios(data): # data = heart_rate.intervals
    kubios_result = dict()
   
    try:
        oled.fill(0)
        oled.text('Sending....', 1, int(64/2), 1)
        oled.show()
        kubios_result = kubios_mqtt_request(data)
    except MQTTConnectionError:
        oled.fill(0)
        oled.text(f'Check connection', 1, int(64/2), 1)
        oled.show()
        return False
    
    #kubios_result = kubios_mqtt_request(data)
    #print(data)
    #print(kubios_result)
    try:
        pns_index = round(kubios_result["data"]["analysis"]["pns_index"],2)
        sns_index = round(kubios_result["data"]["analysis"]["sns_index"],2)
    except TypeError:
        oled.fill(0)
        oled.text(f'Check kubios proxy', 1, int(64/2), 1)
        oled.show()
        return False
    
    if sns_index > 1.0 and pns_index < -1.0:
        message = "High stress"
        perfomance = "SNS high,PNS low"
    elif sns_index > 1.0:
        message = "Moderate stress"
        perfomance = "SNS high"
    elif -1.0 <= sns_index <= 1.0 and pns_index < -1.0:
        message = "Mild stress"
        perfomance = "PNS low"
    elif -1.0 <= sns_index <= 1.0 and -1.0 <= pns_index <= 1.0:
        message = "Normal: Balanced"
        perfomance = ""
    elif sns_index < -1.0 and pns_index > 1.0:
        message = "Recovery"
        perfomance = "PNS high,SNS low"
    else:
        message = "Undefined pattern"
        perfomance = ""
        
    oled.fill(0)
    oled.text(f"Stress(SNS): ", 0, 0,1)
    oled.text(f"{sns_index}", 0,10,1)
    oled.text(f"Recovery(PNS): ", 0,20,1)
    oled.text(f"{pns_index}",0,30,1)
    oled.text(message,0,40,1)
    oled.text(perfomance,0,50)
    oled.show()
    
    return kubios_result

def save_history(data):
  analysis = data['data']['analysis']
  record = {
     'Date':analysis.get('create_timestamp')[5:10],
     'Time':analysis.get('create_timestamp')[11:16],
     'Mean HR': int(analysis.get('mean_hr_bpm')),
     'Mean PPI':int(analysis.get('mean_rr_ms')),
     'RMSSD':round(analysis.get('rmssd_ms'),2),
     'SDNN':round(analysis.get('sdnn_ms'),2),
     'PNS':round(analysis.get('pns_index'),2),
     'SNS':round(analysis.get('sns_index'),2)
  }
  with open('history.txt', 'a') as f:
      f.write(ujson.dumps(record) + "\n")


# def render_history(lines, selection):
#     oled.fill(0)
#     for index ,i in enumerate(range(min(5, len(lines)))):
#             record = ujson.loads(lines[i])
#             date = record.get("Date")
#             time = record.get("Time")
#             display_text = f"{i+1}.{date} {time}"
#             if index == selection:
#                 oled.text('>'+display_text, 0, i * 10, 1) 
#             else:
#                 oled.text(display_text, 0, i * 10, 1) 
#     oled.show()

# def display_history_menu():
#     selection = 1
#     oled.fill(0)
#     try:
#         with open('history.txt', 'r') as f:
#             lines = f.readlines()

#         render_history(lines, selection)
        
#         length = len(range(min(5, len(lines))))
        
#         while True:
#             choice = rot.choose_function_no_refresh()
#             if choice == -1:
#                 selection += -1
#                 if selection < 0:
#                     selection = 0
#                 render_history(lines, selection)
#             elif choice == 1:
#                 selection += 1
#                 if selection >= length:
#                     selection = length - 1
#                 render_history(lines, selection)
#             elif choice == 0:
#                 # select history
#                 selected = selection
#                 oled.fill(0)
#                 json_dump = ujson.loads(lines[selection])
#                 print(json_dump)
#                 index = 0
#                 for i in json_dump:
#                     if i != 'Date' and i != 'Time':
#                         print(i)
#                         display_text = i + ': ' + str(json_dump[i])
#                         oled.text(display_text, 0, index * 8, 1)
#                         index += 1
#                 oled.show()
#                 return
                        



    # except Exception as e:
    #     oled.text("No history found", 0, 0, 1)
    #     print("Error:", e)

    # oled.show()

# test
#data=[828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800,800, 812, 812, 812, 756, 820]
#kubios_result = send_to_kubios(data)
#print(kubios_result)
#save_history(kubios_result['data']['analysis'])



