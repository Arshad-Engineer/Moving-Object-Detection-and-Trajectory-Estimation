import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt
from statistics import mean
import cv2

#Creating a opencv window
cv2.namedWindow('Original Video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Original Video', 640, 480)

cv2.namedWindow('Masked HSV overlayed on Original Video', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Masked HSV overlayed on Original Video', 640, 480)

# Import video
video2 = cv2.VideoCapture("ball.mov")
width  = video2.get(3)  
height = video2.get(4) 
print("Width of Video: ", width, "\nHeight of Video: ", height)

# x, y co-ordinates of the center of the circle
x_lst = [] 
y_lst = [] 

#Loop through the video
while (video2.isOpened()):
    ret, frame = video2.read() 

    if ret == True:
        cv2.imshow("Original Video", frame) 
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
        # By trial and error find the threshold values for h,s,v (used pickcolor.py)
        minHSV = np.array([1, 155, 133]) 
        maxHSV = np.array([6, 255, 255]) 

        # create a mask - 255 for white areas and rest all 0
        maskhsv = cv2.inRange(hsv_image, minHSV, maxHSV) 
        
        output = cv2.bitwise_and(frame, frame, mask=maskhsv)
        cv2.imshow("Masked HSV overlayed on Original Video", output) 

        #find pixel coordinates of the center of the circle using the mask
        y, x = np.where(maskhsv == 255) # white spots
        
        if len(x) > 0 and len(y) > 0:
            x_lst.append(mean(x)) #append the mean of the x coordinates to the x_lst
            y_lst.append(mean(y)) #append the mean of the y coordinates to the y_lst
            cv2.circle(frame, (int(mean(x)), int(mean(y))), 2, (255, 0, 0), 3) #mark the center of the circle on the original video
            cv2.imshow("Original Video", frame) #show the original video with the center of the circle marked
            
        if cv2.waitKey(25)& 0xFF == ord('q'): #press q to exit
            break
    
    else:
        break

video2.release()
cv2.destroyAllWindows()

#Plot trajectory of the ball: 
fig = plt.figure()
plot1 = fig.add_subplot(111)
plot1.set_title("Trajectory of Red Ball vs Best Fit Curve")
plot1.set_xlabel("X - Axis")
plot1.set_ylabel("Y - Axis")
plot1.plot(x_lst, y_lst, color = 'magenta', label = 'Red Ball Trajectory')
plot1.invert_yaxis()

#Least Squares Curve Fitting is given a standard quadratic equation: y = ax^2 + bx + c
# Ref: https://math.libretexts.org/
A = np.array([]) 
B = np.array([]) 

for i in range(len(x_lst)):
    A = np.append(A, [x_lst[i]**2])
    
    A = np.append(A, [x_lst[i]])
   
    A = np.append(A, [1])

    B = np.append(B, [y_lst[i]])

A = A.reshape(len(x_lst), 3) 
B = B.reshape(len(y_lst), 1)
A_Trans = A.T
temp = np.dot(A_Trans, A)
temp = temp.reshape(3, 3)

temp1 = np.dot(A_Trans, B)
temp1 = temp1.reshape(3, 1)

temp_inv = inv(temp)
temp_inv = temp_inv.reshape(3, 3)
S = np.dot(temp_inv, temp1)
S = S.reshape(3, 1)

print("\nEstimated Equation of the Curve given as: y = ax^2 + bx + c\n")
print("a = " + str(S[0]) + "\nb = " + str(S[1]) + "\nc = " + str(S[2]))
print("y = " + str(S[0]) + "x^2 + " + str(S[1]) + "x + " + str(S[2]) + "\n")

#Plot the best fit curve with the data points
y_plot_list = []

for i in range(len(x_lst)):
    y_pred = S[0]*x_lst[i]**2 + S[1]*x_lst[i] + S[2]
    y_plot_list.append(y_pred)

plot1.plot(x_lst, y_plot_list, ls='dotted', color = 'blue', label = 'Best Fit Curve')
plot1.legend(loc='best', fontsize = 8)
plt.show()

#Adding 300 to y-coordinate at the time of release gives landing y pixel value
# y_lst[0] is first pixel of detection and adding 300 to find the landing distance
y_cord = 300 + y_lst[0] 

#Finding x pixel value using estimated parabola equation: y = ax^2 + bx + c
#Solve for x: ax^2 + bx + c - y_cord = 0

coeff = [float(S[0]), float(S[1]), float(S[2]) - y_cord]
roots = np.roots(coeff) 
print("Roots of the equation: ", roots)

#As the distance can be only positive, positive root is taken
if(roots[1] > 0):
    x_cord = roots[1]

else:
    x_cord = roots[0]

print("\n 'x' - Co-ordinate of the ball's landing spot : ", x_cord)