# Text-Detection-with-Tello

The idea behind this project is to enable the Tello DJI drone to consider actions according to the detected text in the live video that could be streamed over a UDP port. However, in TextDetection_Tello.py file I consider 3 main actions when they detected. "TAKEOFF", "LAND" and "ROTATE360".

# Getting Started

First, you need to download and print out the sample text inside images folder above "TAKEOFF", "ROTATE360" and "LAND".<br/>
of course, you can use your own text papers but however accuracy of detection may be changed!

Second, turn on Tello WiFi, connect to it and then:

```
git clone https://github.com/alzin/Text-Detection-with-Tello
cd Text-Detection-with-Tello/
python TextDetection_Tello.py -east frozen_east_text_detection.pb 
```

If Tello WiFi is not available then you may get the following error:
```
Send command: command <br />
Timeout exceed on command command <br />
Command command was unsuccessful. Message: False <br />
Tello not connected
```

## Prerequisites

Please note that the following versions are running on my PC but you may get a different version and run properly!<br/>
Please note also that I tested it on Mac but hopefully works on others OS.

Python 3.6.9<br/>
OpenCV 4.2.0<br/>
numpy 1.16.1<br/>
pytesseract 0.3.3<br/>
imutils 0.5.3<br/>
argparse 1.1<br/>

### Code Logic Explanation

Once initialized and checked that the drone is connected, start video streaming. Then, OpenCV text detection EAST which is a deep learning model "frozen_east_text_detection.pb" could be used to detect in a fast and accurate way if there is any text detected and draw a green rectangle around each text has been detected so far. Until this, it is possible to know that there is some text is being shown in the video preview but we do not what a String characters they got. So, I needed to use OCR where I each time cut the region detected by the EAST model and passed to the OCR Tesseract to analyze its content. After that, depending on what is detected. If "TAKEOFF" then Tello takeoff and if "ROTATE360" Tello rotates 360 and if "LAND" Tello lands as well. Of course, you can add your favorite commands or show the drone any string and specify an action for it. For example, you may show your name and order the drone to flip or something!</br>

Please note that the EAST mode is explained as code and logic in detail in the reference below. AS well as the Tesseract OCR and other libraries that have been used.

# References

DJI Tello drone python interface using the official Tello SDK. https://github.com/damiafuentes/DJITelloPy <br/>

Tello faces detection and tracking. https://github.com/Jabrils/TelloTV <br/>

Tesseract OCR with Python https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/

OpenCV Text Detection (EAST text detector) https://www.pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/

