import pytest
from utils.calculations import calculate_metrics

def test_standard_heart_rate():
  # test data: perfect intervals 60  BPM
  data = [1000,1000,1000,1000]
  result = calculate_metrics(data)
  assert result is not None
  assert result['mean_hr'] == 60
  assert result['mean_ppi'] == 1000
  assert result['SDNN'] == 0 # NO fluctuation

def test_varing_heart_rate():
  #test: varing heart rate
  data = [800, 820, 780, 800]
  result = calculate_metrics(data)
  assert result is not None
  assert result['mean_ppi'] == 800
  assert result['mean_hr'] == 75
  assert result['SDNN'] > 0

def test_empty_input():
  # test: empty data set
  assert calculate_metrics([]) is None

def test_short_input():
  # test: too little data point
  assert calculate_metrics([800]) is None
