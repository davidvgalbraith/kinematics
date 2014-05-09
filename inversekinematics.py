import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time
class Point:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def plus(self, p):
        return Point(self.x + p.x, self.y + p.y, self.z + p.z)

    def minus(self, p):
        return Point(self.x - p.x, self.y - p.y, self.z - p.z)

    def dividedby(self, q):
        return Point(self.x/q, self.y/q, self.z/q)

    def normalize(self):
        norm = np.sqrt(self.x **2 + self.y ** 2 + self.z ** 2)
        if norm == 0:
            print "GODDAMMiT YOU ALWYAS DO THIS"
            exit()
        return Point(self.x/norm, self.y/norm, self.z/norm)
    
    def norm(self):
        norm = np.sqrt(self.x **2 + self.y ** 2 + self.z ** 2)
        return norm        

    def attrByNum(self, num):
        if (num == 0):
            return self.x
        if (num == 1):
            return self.y
        if num == 2:
            return self.z
        print "Idiot! Idiot! Caller is an Idiot!"
        return np.inf

    def __str__(self): 
        return "Point: " + str(self.x) + ", " + str(self.y) + ", " + str(self.z)

class BallJoint:
    #position is the location of this ball joint's inboard joint, length is its length, theta and phi are spherical angles
    def __init__(self, position, length, theta = 0, phi = 0, child = None):
        self.position = position
        self.length = length
        self.theta = theta
        self.phi = phi
        self.child = child
        self.hack = 0

    #Rotate this ball joint dtheta and dphi degrees
    def rotate(self, dtheta, dphi):
        self.theta += dtheta
        self.phi += dphi
        if self.child == None:
            return
        else:
            self.child.position = self.getOutboard().plus(self.position)
            self.child.rotate(dtheta, dphi)

    #where is the other end of this joint at relative to its origin
    def getOutboard(self):
        x = self.length * np.sin(self.theta) * np.cos(self.phi)
        y = self.length * np.sin(self.theta) * np.sin(self.phi)
        z = self.length * np.cos(self.theta)
        return Point(x, y, z)

    #Find the end of this chain
    def effector(self):
        if (self.child == None):
            return self.getOutboard().plus(self.position)
        else:
            return self.child.effector()

    #get a new one with the same stuf
    def copy(self):
        if self.child == None:
            return BallJoint(self.position, self.length, self.theta, self.phi)
        else:
            return BallJoint(self.position, self.length, self.theta, self.phi, self.child.copy())

#magic
def inverseKinematics():
    time.sleep(2)
    global joints
    global goal
    global iterations
    e = joints[0].effector()
    d = goal.minus(e)
    if d.norm() < 0.05:
        print "That's as good as she's gonna get, did it in " + str(iterations) + " iterations."
        return
    if iterations > 100:
        print "Point is out of reach, but I did my best..."
        return
    iterations += 1
    jack = []
    for a in np.arange(3):
        dimension = []
        for b in np.arange(len(joints)):
            dalpha = 0.01
            cop = joints[b].copy()
            cop.rotate(dalpha, 0)
            df = -e.attrByNum(a) + cop.effector().attrByNum(a)
            dimension.append(df / dalpha)
            
            cop = joints[b].copy()
            cop.rotate(0, dalpha)
            df = -e.attrByNum(a) + cop.effector().attrByNum(a)
            dimension.append(df / dalpha)

        jack.append(dimension)
    pseudolus = np.linalg.pinv(np.matrix(jack))
    matd = np.transpose(np.matrix([[d.x, d.y, d.z]]))
    jill = np.matrix(jack)
    dalpha = np.dot(pseudolus, matd)
    j = 0
    normalizedalpha = dalpha/(dalpha.mean() + np.random.random() / 1000)/10
    for k in np.arange(0, len(normalizedalpha), 2):
        joints[j].rotate(dalpha[k, 0], dalpha[k+1, 0])
        j += 1
    glutPostRedisplay()


joints = []
iterations = 1
def myDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    glColor3f(1, 1, 0)
    glPointSize(10)
    global goal
    glBegin(GL_POINTS)
    glVertex3f(goal.x, goal.y, goal.z)
    glEnd()

    glColor3f(1, 1, 1)
    glLineWidth(5)

    glBegin(GL_LINES)

    glVertex3f(0, 0, 0)
    glVertex3f(5, 0, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 5, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 5)

    glEnd()

    global iterations
    glPointSize(22)
    glLineWidth(10)
    root = joints[0]
    glColor3f(0, 0, 1)
    while not (root == None):
        glBegin(GL_POINTS)
        glVertex3f(root.position.x, root.position.y, root.position.z)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(root.position.x, root.position.y, root.position.z)
        p = root.getOutboard()
        p = p.plus(root.position)
        glVertex3f(p.x, p.y, p.z)
        glEnd()
        root = root.child
    glFlush()
    glutSwapBuffers()
    inverseKinematics()


    

def myReshape(w, h):
    glViewport (0,0,w,h);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glutPostRedisplay();

def getCommand():
    joint = raw_input("Which joint would you like to rotate (0=origin, 3=leaf)? ")
    theta = raw_input("What polar angle from the z-axis(theta) do you want? ")
    phi = raw_input("What rotation about the z-axis do you want? ")
    try:
        joints[int(joint)].rotate(np.radians(float(theta)), np.radians(float(phi)))
    except ValueError:
        print "Your input is crap! CRAP! FUCK you!"
        exit()
    glutPostRedisplay()

if __name__ == "__main__":
    global goal
    goalstring = raw_input("\nWhere would you like me to point within the circle of radius five centered at the origin?\n Format as for instance:\n1 2 3\n to get to the point (1, 2, 3):\n")
    goalarray = goalstring.split(" ")
    goal = Point(float(goalarray[0]), float(goalarray[1]), float(goalarray[2]))
    d = BallJoint(Point(0, 0, 4), 1, 0, 0)
    c = BallJoint(Point(0, 0, 2), 2, 0, 0, d)
    b = BallJoint(Point(0, 0, 1), 1, 0, 0, c)
    a = BallJoint(Point(0, 0, 0), 1, 0, 0, b)
    joints.append(a)
    joints.append(b)
    joints.append(c)
    joints.append(d)
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(500, 500)
    glutInitWindowPosition(0, 0)
    glutCreateWindow("I love inverse kinematics")
    glutDisplayFunc(myDisplay)
    glutReshapeFunc(myReshape)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 8, 16)
    gluLookAt(7, 7, 7, 0, 0, 0, 0, 0, 1)

    glutMainLoop()
