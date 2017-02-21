## =========================== ##
##      Waypoint Tracking      ##
## =========================== ##

import math, cmath
import time

# Define the complex number i
i = complex(0,1)
    
# Function to limit arguments to the move command to the range [-1,1]
def limit(x):
    if abs(x) <= 1:
        return x
    else:
        import math
        return math.copysign(1, x)

# List of x,y,z tuples representing waypoints
waypointList = [[500,3500,1000],[3500,500,1000]]
numWaypoints = len(waypointList)
# How close in mm do we need to get to the waypoint
waypoint_tolerance = 150

curPos = (0,0,0)

finishedFlag = False

# Define Proportional Gains
KPphi = 0.0002
KPtheta = (-1)*KPphi
KPgaz = 0.001
# Define Integral Gains
KIphi = 0
KItheta = (-1)*KIphi
KIgaz = 0

# SETUP
# Ensure drone is aligned with y-axis facing in the increasing y direction
refYaw = 0

# Initialise error integrals
errX_integ = 0
errY_integ = 0
errAlt_integ = 0
# First waypoint (waypoint counter)
n = 0

counter = 0
while not finishedFlag and counter < 2000: # This condition will become the Waypoint Reached condition
    time.sleep(0.1)
    print(counter)
    # SENSOR READING
    # Read current location
    # xpos,ypos,yaw
    with open("C:\Python34\PositionData.txt","r") as f:
        f_data = f.read()

    try:
        curPos = tuple([float(i) for i in f_data.split(" ")])
    except:
        print("READING ERROR")

    curYaw = curPos[2]
    print("Current position:\t {},{},{}".format(curPos[0], curPos[1], curYaw))
    print("Waypoint:\t\t {}".format(waypointList[n]))

    # Calculate error between drones current position and current waypoint
    errPos = tuple([i - j for i, j in zip(waypointList[n], curPos)])
    errYaw = math.radians(refYaw - curYaw)

    # Current position on complex plane
    W_o = complex(errPos[0], errPos[1])
    print("errYaw: \t\t{:.2f}".format(errYaw))
    #print("W_o: \t\t{:.2f} {:.2f}".format(P.real, P.imag))
    # New imagined waypoint position P_prime found by rotation
    W_prime = W_o*cmath.exp(i*errYaw)
    #print("W_prime: \t{:.2f} {:.2f}".format(W_prime.real, W_prime.imag))

    # Calculate error between drones current position and current rotated waypoint
    errPos = [W_prime.real, W_prime.imag]
    #errAlt = waypointList[n][2]-curAlt
    print("Error:\t\t {},{},{}".format(errPos[0], errPos[1], errYaw))

    # Upate integral of errors
    errX_integ += errPos[0]
    errY_integ += errPos[1]
    #errAlt_integ += errAlt

    # CONTROL
    # If waypoint is reached
    if math.hypot(errPos[0], errPos[1]) < waypoint_tolerance:
        time.sleep(3)
        # If there are no more waypoints we are finished
        if n+1 >= numWaypoints:
            finishedFlag = True
        # Otherwise advance to the next waypoint
        else:
            print("Next Waypoint")
            # Reset error integrals
            errX_integ = 0
            errY_integ = 0
            #errAlt_integ = 0
            # "Hover"
            phi = theta = yaw = 0
            fileControl_data = open("C:\Python34\ControlData.txt","w")
            fileControl_data.write("{} {} {}".format(phi, theta, yaw))
            fileControl_data.close()
            # Update waypoint counter
            n += 1
    else:
        # Yaw
        # No Yaw control
        yaw = 0

        # Roll
        phi = limit(KPphi*errPos[0] + KIphi*errX_integ)
        print("Left" if phi < 0 else "Right")

        # Pitch
        theta = limit(KPtheta*errPos[1] + KItheta*errY_integ)
        print("Forward" if theta < 0 else "Backward")

        # Vertical Speed
        #gaz = limit(KPgaz*errAlt + KIgaz*errAlt_integ)
        #print("Down" if gaz < 0 else "Up")

        #control.move(phi, theta, gaz, yaw)
        try:
                fileControl_data = open("C:\Python34\ControlData.txt","w")
                fileControl_data.write("{} {} {}".format(phi, theta, yaw))
                fileControl_data.close()
        except:
                pass

    counter +=1

print ("Journey Complete!" if finishedFlag else "Time Up!")
phi = theta = yaw = 0
fileControl_data = open("C:\Python34\ControlData.txt","w")
fileControl_data.write("{} {} {}".format(phi, theta, yaw))
fileControl_data.close()
