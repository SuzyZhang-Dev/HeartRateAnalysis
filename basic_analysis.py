from mqtt_kubios import connect_local_mqtt,publish_basic_analysis, MQTTConnectionError
from oled import oled

class Basic_Analysis:
    def __init__(self):
        self.data_list = []
               
    def calculate(self):    
        self.mean_ppi = int(sum(self.data_list)/len(self.data_list))
        self.mean_hr = int(60000/self.mean_ppi)
               
        square_sum_diff = 0 
        for ppi in self.data_list:            
            diff = ppi - self.mean_ppi
            square_sum_diff += diff ** 2        
        square_avg = square_sum_diff / len(self.data_list)
        self.SDNN = round(square_avg ** 0.5,2)
        
        RMSSD_list = []        
        for i in range(1,len(self.data_list)):
            ppi_diff = self.data_list[i] - self.data_list[i-1]
            RMSSD_list.append(ppi_diff)        
        diff_square = 0 
        for diff in RMSSD_list:
            diff_square += diff**2
        diff_square_avg = diff_square / len(RMSSD_list)
        self.RMSSD = round(diff_square_avg ** 0.5,2)
              
        return self.mean_ppi, self.mean_hr, self.SDNN, self.RMSSD
    
    def get_result(self, data_list: list[int]) -> dict:
        self.data_list = data_list
        result = self.calculate()
        #print("Mean PPI:", result[0])
        #print("Mean HR:", result[1])
        #print("SDNN:", result[2])
        #print("RMSSD:", result[3])

        #convert to dict
        analysis_results = {
            "mean_ppi": result[0],
            "mean_hr": result[1],
            "SDNN": result[2],
            "RMSSD": result[3]
        }

        try:
            oled.fill(0)
            oled.text('Sending....', 1, int(64/2), 1)
            oled.show()
            await_result = publish_basic_analysis(analysis_results)
        except MQTTConnectionError:
            oled.fill(0)
            oled.text(f'Check connection', 1, int(64/2), 1)
            oled.show()
            return False


        oled.fill(0)
        oled.text(f"Mean PPI: {result[0]}", 0, 0)
        oled.text(f"Mean HR: {result[1]}", 0, 15)
        oled.text(f"SDNN: {result[2]}", 0, 30)
        oled.text(f"RMSSD: {result[3]}", 0, 45)
        oled.show()
        
        
        return analysis_results

#for testing
# data_list=[828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]       
# test=Basic_Anaysis(data_list)
# result=test.get_result()
# print(result)