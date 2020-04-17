# Text-Detection-with-Tello

The idea behind this project is to enable the Tello DJI drone to consider actions according to the detected text in the live video that could be streamed over a UDP port. However, in TextDetection_Tello.py file I consider 3 main actions when they detected. "TAKEOFF", "LAND" and "ROTATE360".

# Getting Started

First turn on Tello WiFi, connect to it and then:

```
git clone https://github.com/alzin/Text-Detection-with-Tello
cd Text-Detection-with-Tello/
python TextDetection_Tello.py -east frozen_east_text_detection.pb 
```

if Tello WiFi is not available then you may get the following error:

*Send command: command <br />
Timeout exceed on command command <br />
Command command was unsuccessful. Message: False <br />
Tello not connected*

## Prerequisites

Please note that the following versions are running on my PC but you may get a different version and run properly!

OpenCV 4.2.0 <br />
NumPy 1.16.1 <br />
Pytesseract 0.3.3 <br />
