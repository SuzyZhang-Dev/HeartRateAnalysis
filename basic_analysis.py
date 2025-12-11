from mqtt_kubios import connect_local_mqtt,publish_basic_analysis, MQTTConnectionError
from oled import oled
from utils.calculations import calculate_metrics

class Basic_Analysis:
    def __init__(self):
        self.data_list = []
    
    def get_result(self, data_list: list[int]) -> dict:
        self.data_list = data_list
        result_dict = calculate_metrics(self.data_list)

        if result_dict is None:
            return {}
        
        mean_ppi = result_dict['mean_ppi']
        mean_hr = result_dict['mean_hr']
        sdnn = result_dict['SDNN']
        rmssd = result_dict['RMSSD']

        #convert to dict
        # analysis_results = {
        #     "mean_ppi": mean_ppi,
        #     "mean_hr": mean_hr,
        #     "SDNN": sdnn,
        #     "RMSSD": rmssd
        # }

        try:
            oled.fill(0)
            oled.text('Sending....', 1, int(64/2), 1)
            oled.show()
            publish_basic_analysis(result_dict)
        except MQTTConnectionError:
            oled.fill(0)
            oled.text(f'Check connection', 1, int(64/2), 1)
            oled.show()
            return False


        oled.fill(0)
        oled.text(f"Mean PPI: {mean_ppi}", 0, 0)
        oled.text(f"Mean HR: {mean_hr]}", 0, 15)
        oled.text(f"SDNN: {sdnn}", 0, 30)
        oled.text(f"RMSSD: {rmssd}", 0, 45)
        oled.show()
        
        
        return result_dict

#for testing
# data_list=[828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]       
# test=Basic_Anaysis(data_list)
# result=test.get_result()
# print(result)