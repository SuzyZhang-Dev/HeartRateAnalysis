# 💓 HRV Monitoring Device with Raspberry Pi Pico

A heart rate variability (HRV) monitoring device built using **Raspberry Pi Pico**, **MicroPython**, and an **OLED display**.  
This project was developed as part of our embedded systems coursework, focusing on real-time health monitoring, efficient user interaction, and IoT communication.

## 🚀 Features

### 🌀 1. Simple One-Knob Interaction
- Uses a **single encoder** as the only user input.
- Simplifies operation for users of all ages, including children and elderly.
- Supports intuitive navigation across all functions with turn and press actions.

### 📈 2. Real-Time Heart Rate & Waveform
- Real-time display of heart rate and heartbeat waveform.
- Visual **timer** added for smoother data collection experience.
- Helps users patiently complete required sampling time.

### 🌐 3. Dual MQTT Communication
- Supports both **local** and **Kubios** MQTT analysis.
- Implements a **conditional statement** to classify stress level as *High* or *Low*, based on Kubios documentation.
- Stores four key HRV indicators (excluding SNS & PNS) in history logs.

### 📅 4. History with Timestamps
- Displays up to 5 previous records with **timestamps**.
- Enables users to clearly track and compare past results.

## 🧠 Developer Workflow Optimization

Working with **Thonny** had limitations (e.g. poor Git support).  
To improve our workflow, we used this process:

1. Switch Thonny’s interpreter to **local Python** to free Pico.
2. Use terminal and [`mpremote`](https://github.com/adafruit/ampy) to push code:
   ```bash
   mpremote cp *.py :
3.	Code in any preferred IDE and commit to Git for team collaboration.
