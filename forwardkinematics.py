import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Point:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def plus(self, p):
        return Point(self.x + p.x, self.y + p.y, self.z + p.z)
    
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

joints = []
k = 1
def myDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

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

    global k
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
        print "p: ", p
        if not (root.child == None):
            print root.child.position
        print
        p = p.plus(root.position)
        glVertex3f(p.x, p.y, p.z)
        glEnd()
        root = root.child
    glFlush()
    glutSwapBuffers()
    if (k > 1):
        getCommand()
    else:
        k += 1

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

goal = Point(1, 1, -1)

if __name__ == "__main__":
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
    glutCreateWindow("Dave is hot")
    glutDisplayFunc(myDisplay)
    glutReshapeFunc(myReshape)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 8, 16)
    gluLookAt(7, 7, 7, 0, 0, 0, 0, 0, 1)

    glutMainLoop()
