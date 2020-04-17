from djitellopy import Tello
from PIL import Image
from imutils.object_detection import non_max_suppression
import cv2
import numpy as np
import time
import datetime
import os
import argparse
import imutils
import pytesseract

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-east", "--east", type=str, required=True,
    help="path to input EAST text detector")
ap.add_argument("-c", "--min-confidence", type=float, default=0.5,
    help="minimum probability required to inspect a region")
ap.add_argument("-w", "--width", type=int, default=320,
    help="resized image width (should be multiple of 32)")
ap.add_argument("-e", "--height", type=int, default=320,
    help="resized image height (should be multiple of 32)")
args = vars(ap.parse_args())

# Frames per second of the pygame window display
FPS = 25
dimensions = (960, 720)

class FrontEnd(object):

    def __init__(self):
        # Init Tello object that interacts with the Tello drone
        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False

    def run(self):

        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return

        # In case streaming is on. This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return

        frame_read = self.tello.get_frame_read()

        should_stop = False

        # initialize the original frame dimensions, new frame dimensions,
        # and ratio between the dimensions
        (W, H) = (None, None)
        (newW, newH) = (args["width"], args["height"])
        (rW, rH) = (None, None)
        print(newW, newH)

        # define the two output layer names for the EAST detector model that
        # we are interested -- the first is the output probabilities and the
        # second can be used to derive the bounding box coordinates of text
        layerNames = ["feature_fusion/Conv_7/Sigmoid","feature_fusion/concat_3"]

        # load the pre-trained EAST text detector
        print("[INFO] loading EAST text detector...")
        net = cv2.dnn.readNet(args["east"])

        print("START MAIN LOOP")

        while not should_stop:
            self.update()

            if frame_read.stopped:
                frame_read.stop()
                break


            # gray = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2GRAY)
            # gray1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            # blur = cv2.medianBlur(gray, 3)
            frameRet = frame_read.frame

            frame = imutils.resize(frameRet, width=720)
            orig = frame.copy()

            # if our frame dimensions are None, we still need to compute the
            # ratio of old frame dimensions to new frame dimensions
            if W is None or H is None:
                (H, W) = frame.shape[:2]
                rW = W / float(newW)
                rH = H / float(newH)

            # resize the frame, this time ignoring aspect ratio
            frame = cv2.resize(frame, (newW, newH))

            # construct a blob from the frame and then perform a forward pass
            # of the model to obtain the two output layer sets
            blob = cv2.dnn.blobFromImage(frame, 1.0, (newW, newH),
            (123.68, 116.78, 103.94), swapRB=True, crop=False)
            net.setInput(blob)
            (scores, geometry) = net.forward(layerNames)

            # decode the predictions, then  apply non-maxima suppression to
            # suppress weak, overlapping bounding boxes
            (rects, confidences) = self.decode_predictions(scores, geometry)
            boxes = non_max_suppression(np.array(rects), probs=confidences)

            cropped_img = ""
            text = ""
            # loop over the bounding boxes
            for (startX, startY, endX, endY) in boxes:
                # scale the bounding box coordinates based on the respective ratios
                startX = int(startX * rW)
                startY = int(startY * rH)
                endX = int(endX * rW)
                endY = int(endY * rH)

                # draw the bounding box on the frame
                cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)

                cropped_img = orig[startY-20:endY+20, startX-20:endX+20]
                # cv2.imshow(f'Rec...', cropped_img)
                if cropped_img.size != 0:
                    filename = "{}.png".format(os.getpid())
                    cv2.imwrite(filename, cropped_img)
                    text = pytesseract.image_to_string(Image.open(filename))
                    os.remove(filename)
                    print(text)

            time.sleep(1 / FPS)

            # Listen for key presses
            k = cv2.waitKey(20)

            # Press T to take off
            # if k == ord('t'):
            if "TAKEOFF" in text and self.send_rc_control !=True:
                print("Takeoff Only Once")
                self.tello.takeoff()
                self.send_rc_control = True

            if "ROTATE360" in text and self.send_rc_control == True:
            # if k == ord('r'):
                self.tello.rotate_counter_clockwise(360)
                time.sleep(5)

            # Press L to land
            # if k == ord('l'):
            if "LAND" in text and self.send_rc_control == True:
                self.tello.land()
                self.send_rc_control = False

            # Quit the software
            if k == 27:
                should_stop = True
                break

            # Display the resulting frame
            cv2.imshow(f'Tello Text Detection...',orig)

        # When everything done, release the capture
        cv2.destroyAllWindows()

        # Call it always before finishing. I deallocate resources.
        self.tello.end()

        print("Finished MAIN LOOP")


    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                       self.yaw_velocity)

    def decode_predictions(self,scores, geometry):
        # grab the number of rows and columns from the scores volume, then
        # initialize our set of bounding box rectangles and corresponding
        # confidence scores
        (numRows, numCols) = scores.shape[2:4]
        rects = []
        confidences = []

        # loop over the number of rows
        for y in range(0, numRows):
            # extract the scores (probabilities), followed by the
            # geometrical data used to derive potential bounding box
            # coordinates that surround text
            scoresData = scores[0, 0, y]
            xData0 = geometry[0, 0, y]
            xData1 = geometry[0, 1, y]
            xData2 = geometry[0, 2, y]
            xData3 = geometry[0, 3, y]
            anglesData = geometry[0, 4, y]

            # loop over the number of columns
            for x in range(0, numCols):
                # if our score does not have sufficient probability,
                # ignore it
                if scoresData[x] < args["min_confidence"]:
                    continue

                # compute the offset factor as our resulting feature
                # maps will be 4x smaller than the input image
                (offsetX, offsetY) = (x * 4.0, y * 4.0)

                # extract the rotation angle for the prediction and
                # then compute the sin and cosine
                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                # use the geometry volume to derive the width and height
                # of the bounding box
                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                # compute both the starting and ending (x, y)-coordinates
                # for the text prediction bounding box
                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                # add the bounding box coordinates and probability score
                # to our respective lists
                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])

        # return a tuple of the bounding boxes and associated confidences
        return (rects, confidences)

def main():
    frontend = FrontEnd()
    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()
