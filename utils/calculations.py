#utils/calculation.py

def calculate_metrics(ppi_list):
  """
  Docstring for calculate_metrics
  
  :param ppi_list: Description
  without any hardware dependency
  """
  if not ppi_list or len(ppi_list)<2:
    return None
  
  # 1. calculate mean_ppi and mean heart rate
  mean_ppi = (int)(sum(ppi_list) / len(ppi_list))
  if mean_ppi == 0:
     return None
  mean_hr = int(60000 / mean_ppi)

  # 2. calculate SDNN(standrad deviation)
  square_sum_diff = sum((ppi - mean_ppi)**2 for ppi in ppi_list)
  sdnn = round((square_sum_diff / len(ppi_list))** 0.5 ,2)

  # 3. calculate RMSSD
  rmssd_list = [(ppi_list[i] - ppi_list[i-1]) ** 2 for i in range(1, len(ppi_list))]
  if not rmssd_list:
     rmssd = 0.0
  else:
    rmssd = round((sum(rmssd_list) / len(rmssd_list)) ** 0.5, 2)

  return {
    "mean_ppi": mean_ppi,
    "mean_hr": mean_hr,
    "SDNN": sdnn,
    "RMSSD": rmssd
    }
