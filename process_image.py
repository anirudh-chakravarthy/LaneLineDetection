print("Process Image")

import numpy as np
import cv2

from utils.functions import *


def squareROI(height, width):
    
    return np.array ( [[
                    [width - 10, height / 2], 
                    [width - 10, height],
                    [10, height ],
                    [10, height / 2]
            ]], dtype = np.int32)


def trapeziumROI(height, width):

    return np.array( [[
                [3*width/4, 3*height/5],
                [width/4, 3*height/5],
                [40, height],
                [width - 40, height]
            ]], dtype=np.int32 )


def process_image(image):

    # grayscale conversion before processing causes more harm than good
    # because sometimes the lane and road have same amount of luminance
    # grayscaleImage = grayscale(image)

    # applying LAB transform
    labImage = bgr_to_lab(image)

    # Blur to avoid edges from noise
    blurredImage = gaussian_blur(labImage, 11)

    # Detect edges using canny
    # high to low threshold factor of 3
    # it is necessary to keep a linient threshold at the lower end
    # to continue to detect faded lane markings
    edgesImage = canny(blurredImage, 40, 50)
    
    # mark out the trapezium region of interest
    # dont' be too agressive as the car may drift laterally
    # while driving, hence ample space is still left on both sides.
    height = image.shape[0]
    width = image.shape[1]
    vertices = trapeziumROI(height, width)

    # mask the canny output with trapezium region of interest
    regionInterestImage = region_of_interest(edgesImage, vertices)
    
    # parameters tuned using this method:
    # threshold 30 by modifying it and seeing where slightly curved 
    # lane markings are barely detected
    # min line length 20 by modifying and seeing where broken short
    # lane markings are barely detected
    # max line gap as 100 to allow plenty of room for the algo to 
    # connect spaced out lane markings
    lineMarkedImage = hough_lines(regionInterestImage, 1, np.pi/180, 40, 30, 200)
    
    # Test detected edges by uncommenting this
    #return cv2.cvtColor(regionInterestImage, cv2.COLOR_GRAY2RGB)

    # draw ROI on the image
    cv2.line(image, (vertices[0][0], vertices[0][1]), (vertices[1][0], vertices[1][1]), [255,255,0], 10)
    cv2.line(image, (vertices[1][0], vertices[1][1]), (vertices[2][0], vertices[2][1]), [255,255,0], 10)
    cv2.line(image, (vertices[2][0], vertices[2][1]), (vertices[3][0], vertices[3][1]), [255,255,0], 10)
    cv2.line(image, (vertices[3][0], vertices[3][1]), (vertices[0][0], vertices[0][1]), [255,255,0], 10)

    # draw output on top of original
    weightedImage =  weighted_img(lineMarkedImage, image)

    return weightedImage