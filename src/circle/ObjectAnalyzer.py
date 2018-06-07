from PIL import ImageEnhance, Image
from cv2 import imshow
import cv2

import PIL as p
from circle import Circle as cl
import numpy as np


#cap = cv2.VideoCapture(0)
#cap.open('tcp://192.168.1.1:5555')
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
width = 1280#cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = 720#cap.get(cv2.CAP_PROP_FRAME_HEIGHT)


class ObjectAnalyzer:
    #Variables: 
    circleObj = cl.Circle()
    
    maskLimit = 100
    upperMaskLimit = 255
    
    
    #Mask 
    lowMaskLowHue = 0
    lowMaskHighHue = 10
    lowMaskLowSat = 0
    lowMaskHighSat = 255
    lowMaskLowVal = 0
    lowMaskHighVal = 255
    
    highMaskLowHue = 170
    highMaskHighHue = 180
    highMaskLowSat = 0
    highMaskHighSat = 255
    highMaskLowVal = 0
    highMaskHighVal = 255
    
    
    
    #Requires further testing
    edgedLowLimit = 0
    edgedHighLimit = 0
    
    #Requires further testing
    houghDP = 1
    
    #Not to low. Set to 2000 if only we only wish 1 circle pr. image. 
    houghMinDist = 1
    
    #Param 1 will set the sensitivity; how strong the edges of the circles need to be. 
    #Too high and it won't detect anything, too low and it will find too much clutter. 
    houghParam1 = 1
    #Param 2 will set how many edge points it needs to find to declare that it's found a circle. 
    #Again, too high will detect nothing, too low will declare anything to be a circle. 
    #The ideal value of param 2 will be related to the circumference of the circles.
    houghParam2 = 1
    #Min around 50. max around 1000. 
    houghMinRadius = 1
    houghMaxRadius = 1
    
    #Used for testing. 
    brightness = 0;
    #Used to determine maskLimit later on. 
    perceivedBrightness = 10
    
    #For mapping mask limit and perceived brightness. 
    inMin = 0
    inMax = 1
    outMin = 2
    outMax = 3
    
    
    
    def map(self, value, inMin, inMax, outMin, outMax):
        # Figure out how 'wide' each range is
        leftSpan = inMax - inMin
        rightSpan = outMax - outMin
        
       
        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - inMin) / float(leftSpan)
        
        # Convert the 0-1 range into a value in the right range.    
        return int(outMin + (valueScaled * rightSpan))

    
    def nothing(self):
        pass
    
    cv2.namedWindow('HSV')
    cv2.namedWindow('Trackbar')
    cv2.resizeWindow('Trackbar',780,780)
    # create trackbars for color change
    
    #HSV saturation
    cv2.createTrackbar('lowMaskLowSat','HSV',0,255,nothing)
    cv2.createTrackbar('lowMaskHighSat','HSV',0,255,nothing)
    cv2.createTrackbar('highMaskLowSat','HSV',0,255,nothing)
    cv2.createTrackbar('highMaskHighSat','HSV',0,255,nothing)
    #HSV value
    cv2.createTrackbar('lowMaskLowVal','HSV',0,255,nothing)
    cv2.createTrackbar('lowMaskHighVal','HSV',0,255,nothing)
    cv2.createTrackbar('highMaskLowVal','HSV',0,255,nothing)
    cv2.createTrackbar('highMaskHighVal','HSV',0,255,nothing)
    
    
    
        
    #cv2.createTrackbar('MaskLimit','Trackbar',0,255,nothing)
    #cv2.createTrackbar('UpperMaskLimit','Trackbar',0,255,nothing)
    #No use for these since it's already determined. Keeping them if further testing is needed. 
    #cv2.createTrackbar('lowMaskLowRed','Trackbar',0,180,nothing)
    #cv2.createTrackbar('lowMaskUpperRed','Trackbar',0,180,nothing)
    #cv2.createTrackbar('highMaskLowRed','Trackbar',0,180,nothing)
    #cv2.createTrackbar('highMaskUpperRed','Trackbar',0,180,nothing)

    
    #Still useful. Used to make sure that the circle detected actually is there. 
    cv2.createTrackbar('Error','Trackbar',1,100,nothing)
    cv2.createTrackbar('Amount of Circles','Trackbar',1,10,nothing)
    
    #Used for testing. 
    cv2.createTrackbar('Edged low limit','Trackbar',0,255,nothing)
    cv2.createTrackbar('Edged high limit','Trackbar',0,255,nothing)
    
    #hough circles
    cv2.createTrackbar('Hough: dp','Trackbar',1,100,nothing) # Inverse ratio of the accumulator resolution to the image resolution. For example, if dp=1 , the accumulator has the same resolution as the input image. If dp=2 , the accumulator has half as big width and height.
    cv2.createTrackbar('Hough: min dist','Trackbar',10,2000,nothing) #minimum distance between circle centers
    cv2.createTrackbar('Hough: param1','Trackbar',10,300,nothing)
    cv2.createTrackbar('Hough: param2','Trackbar',10,300,nothing)
    cv2.createTrackbar('minRadius','Trackbar',1,2000,nothing)
    cv2.createTrackbar('maxRadius','Trackbar',1,2000,nothing)
    
    #Image brigthness
    cv2.createTrackbar('Brightness','Trackbar',1,1000,nothing)
    
    #cv2.createTrackbar('inMin','Trackbar',0,180,nothing)
    #cv2.createTrackbar('inMax','Trackbar',1,180,nothing)
    #cv2.createTrackbar('outMin','Trackbar',2,180,nothing)
    #cv2.createTrackbar('outMax','Trackbar',3,180,nothing)
                       
    
    def calculateBrightness(self,image):
        pImage = Image.fromarray(image)
        stat = p.ImageStat.Stat(pImage)
        
        self.perceivedBrightness = stat.mean[0]

        #print("perceivedBrightness: ", self.perceivedBrightness)
    
    def setImageBrightNess(self,image,value):
        PilImage = Image.fromarray(image)
        enhancer = ImageEnhance.Brightness(PilImage)        
        image = enhancer.enhance(value)
        return image
    
    
    def updateValues(self):
        #self.maskLimit = cv2.getTrackbarPos('MaskLimit','Trackbar')
        self.upperMaskLimit = cv2.getTrackbarPos('UpperMaskLimit','Trackbar')
    
        #self.lowMaskLowRed = cv2.getTrackbarPos('lowMaskLowRed','Trackbar')
        #self.lowMaskUpperRed = cv2.getTrackbarPos('lowMaskUpperRed','Trackbar')
        #self.highMaskLowRed = cv2.getTrackbarPos('highMaskLowRed','Trackbar')
        #self.highMaskUpperRed = cv2.getTrackbarPos('highMaskUpperRed','Trackbar')
        
        #HSV 
        self.lowMaskLowSat = cv2.getTrackbarPos('lowMaskLowSat','HSV')
        self.lowMaskHighSat = cv2.getTrackbarPos('lowMaskHighSat','HSV')
        self.highMaskLowSat = cv2.getTrackbarPos('highMaskLowSat','HSV')
        self.highMaskHighSat = cv2.getTrackbarPos('highMaskHighSat','HSV')
        
        self.lowMaskLowVal = cv2.getTrackbarPos('lowMaskLowVal','HSV')
        self.lowMaskHighVal = cv2.getTrackbarPos('lowMaskHighVal','HSV')
        self.highMaskLowVal = cv2.getTrackbarPos('highMaskLowVal','HSV')
        self.highMaskHighVal = cv2.getTrackbarPos('highMaskHighVal','HSV')
        
 
        
        error = cv2.getTrackbarPos('Error','Trackbar')
        amountOfCircles = cv2.getTrackbarPos('Amount of Circles','Trackbar')
        self.edgedLowLimit = cv2.getTrackbarPos('Edged low limit','Trackbar')
        self.edgedHighLimit = cv2.getTrackbarPos('Edged high limit','Trackbar')
        
        self.houghDP = cv2.getTrackbarPos('Hough: dp','Trackbar')/10
        
        if self.houghDP == 0:
                self.houghDP = 1
        self.houghMinDist = cv2.getTrackbarPos('Hough: min dist','Trackbar')
        if self.houghMinDist == 0:
                self.houghMinDist = 1
        
        self.houghParam1 = cv2.getTrackbarPos('Hough: param1','Trackbar')
        if self.houghParam1 == 0:
                self.houghParam1 = 1
        
        self.houghParam2 = cv2.getTrackbarPos('Hough: param2','Trackbar')
        if self.houghParam2 == 0:
                self.houghParam2 = 1
        
        self.houghMinRadius = cv2.getTrackbarPos('minRadius','Trackbar')
        if self.houghMinRadius == 0:
                self.houghMinRadius = 1
        
        self.houghMaxRadius = cv2.getTrackbarPos('maxRadius','Trackbar')
        if self.houghMaxRadius == 0:
                self.houghMaxRadius = 1
        
        if error == 0:
                error = 1
        if amountOfCircles == 0:
                amountOfCircles = 1
        
        
        self.circleObj.setError(error)
        self.circleObj.setAmountOfCircles(amountOfCircles)
        
        self.brightness = cv2.getTrackbarPos('Brightness','Trackbar')
        self.brightness = self.brightness/float(1000)
        
        
        
        #self.inMin = cv2.getTrackbarPos('inMin','Trackbar')
        #self.inMax = cv2.getTrackbarPos('inMax','Trackbar')
        #if self.inMax == 0:
        #    self.inMax = 1
        #self.outMin = cv2.getTrackbarPos('outMin','Trackbar')
        #self.outMax = cv2.getTrackbarPos('outMax','Trackbar')
        #if self.outMax == 0:
        #    self.outMax = 1
        
    
    def setTestValues(self, frame):
        self.updateValues() #Used for testing.     
        brightnessFrame = self.setImageBrightNess(frame, self.brightness)
        frame = np.array(brightnessFrame)
        self.calculateBrightness(frame)             #Calculate the perceived brightness. 


    
    def getRedHSVImage(self, frame):
        # lower mask (0-10)
        red_hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        imshow("RedHSV",red_hsv)
            
        
        #Create the boundary of the first mask. 
        lowMask_lower_red = np.array([self.lowMaskLowHue,self.lowMaskLowSat,self.lowMaskLowVal])
        lowMask_upper_red = np.array([self.lowMaskHighHue,self.lowMaskHighSat,self.lowMaskHighVal])           
            
        mask0 = cv2.inRange(red_hsv, lowMask_lower_red, lowMask_upper_red)
            
            
        #Create the boundary of the second mask. 
        highMask_lower_red = np.array([self.highMaskLowHue,self.highMaskLowSat,self.highMaskLowVal])
        highMask_upper_red = np.array([self.highMaskHighHue,self.highMaskHighSat,self.highMaskHighVal])
        
        mask1 = cv2.inRange(red_hsv, highMask_lower_red, highMask_upper_red)
        
        # join my masks
        mask = mask0 + mask1
        
        
        # set my output img to zero everywhere except my mask
        red_output = frame.copy()
        
        red_output = cv2.bitwise_and(red_output, red_output, mask = mask)
        
        
        imshow("Red", red_output)
        return red_output
    
    
    
    def findCircle(self, frame):
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grey, (7, 7), 0)
        #blurred1 = cv2.medianBlur(grey.copy(),5)        #Might be better for filtering noise. 



        
    def analyzeFrame(self,frame):
        while (True):
            self.setTestValues(frame)
            
            #Maps perceived brigthness to masklimit. Only used in the final version. Requires further testing. 
            #self.maskLimit = self.map(self.perceivedBrightness, self.inMin, self.inMax, self.outMin, self.outMax)
            
            redImage = self.getRedHSVImage(frame)
          
          
            #bilateral = cv2.bilateralFilter(red_output, 5, 250, 250)
            #imgray = cv2.cvtColor(bilateral, cv2.COLOR_BGR2GRAY)
            #blur = cv2.GaussianBlur(imgray, (5, 5), 0)
            #ret, thresh = cv2.threshold(blur, 40, 255, 0)
            
            grey = cv2.cvtColor(redImage, cv2.COLOR_BGR2GRAY)
            #cv2.imshow("Grey",grey)
            
            
            
            
            #waitKey(2500)
            blurred = cv2.GaussianBlur(grey, (7, 7), 0)
            blurred1 = cv2.medianBlur(grey.copy(),5)
            
            #Test Try and change the values above. 
            
            #cv2.imshow("blurred",blurred)
            #cv2.imshow("blurred1", blurred1)

            edged = cv2.Canny(blurred, self.edgedLowLimit, self.edgedHighLimit)
            #edged1 = cv2.Canny(blurred1, self.edgedLowLimit, self.edgedHighLimit)
            cv2.imshow("Edged",edged)
            #cv2.imshow("edged1",edged1)
            #_, contours, hierarchy = cv2.findContours(edged1.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            circles = cv2.HoughCircles(edged.copy(), cv2.HOUGH_GRADIENT, self.houghDP, self.houghMinDist, param1 = self.houghParam1, param2 = self.houghParam2, minRadius = self.houghMinRadius, maxRadius = self.houghMaxRadius)
            #ret,thresh = cv2.threshold(grey,127,255,0)
            #
            #edged2 = cv2.Canny(thresh, self.edgedLowLimit, self.edgedHighLimit)
            #cv2.imshow("edged2",edged2)
            #adaptive = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
            #th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
            #_, contours = cv2.findContours(thresh, 1, 2)
            
            #cv2.imshow("thresh",thresh)
            #ellipse = cv2.fitEllipse(contours)
            #ellipse = cv2.ellipse(img, ellipse, (0,255,0), 2)
            #cv2.imshow("Adaptive", adaptive)
            
            #rows = thresh.shape[0]
            
            #circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30, minRadius=40, maxRadius=400)
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i in circles[0, :]:
                    #If radius is zero, circle doesn't exist..
                    if i[2] == 0:
                        break
                    #Create the new circle.
                    newCircle = ([i[0],i[1],i[2]])
              
                    self.circleObj.circleKnown(newCircle)
                    self.circleObj.enoughNewCircles(frame, width, height)
                    # Display the resulting frame
            cv2.imshow('frame', frame)
            cv2.moveWindow('frame', 20, 20)
    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
        cv2.destroyAllWindows()
    
    

    
    
#recorderObj = Recorder()
#recorderObj.main()
