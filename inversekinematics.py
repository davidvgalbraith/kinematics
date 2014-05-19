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
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

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
    time.sleep(0.1)
    global joints
    global goal
    global iterations
    global mistakes
    global goaldistance
    e = joints[0].effector()
    d = goal.minus(e)
    #if d.norm() > goaldistance:
    #    mistakes += 1
    """if mistakes > 7:
        print "Giving up on " + str(goal)
        mistakes = 0
        iterations = 1
        goal = Point(signedRandom() * 4, signedRandom() * 4, signedRandom() * 4)
        glutPostRedisplay()
        return 
    if d.norm() < 0.1:
        print "Reached " + str(goal)
        iterations = 1
        mistakes = 0
        goal = Point(signedRandom() * 4, signedRandom() * 4, signedRandom() * 4)
        glutPostRedisplay()
        return """ 
    #if iterations > 100:
    #    print "I give up. " + str(goal) + " is too hard to reach. I hope you're happy."
    #    glutLeaveMainLoop()
    #    return
    iterations += 1
    goaldistance = d.norm()
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
        joints[j].rotate(dalpha[k, 0]/10, dalpha[k+1, 0]/10)
        j += 1
    goal = goal.plus(Point(signedRandom() / 5, signedRandom() / 5, signedRandom() / 5))
    if(goal.norm() > 6):
        goal = Point(signedRandom(), signedRandom(), signedRandom())
    glutPostRedisplay()


iterations = 1
mistakes = 0
goaldistance = np.Infinity

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

def signedRandom():
    j = np.random.random()
    sign = np.random.randint(-1, 2)
    while sign == 0:
        sign = np.random.randint(-1, 2)
    return j * sign


if __name__ == "__main__":
    global goal
    global joints
    joints = []
    goal = Point(signedRandom() * 4, signedRandom() * 4, signedRandom() * 4)
    d = BallJoint(Point(0, 0, 4.5), 0.5, 0, 0)
    c = BallJoint(Point(0, 0, 3.5), 1, 0, 0, d)
    b = BallJoint(Point(0, 0, 0.5), 3, 0, 0, c)
    a = BallJoint(Point(0, 0, 0), 0.5, 0, 0, b)
    joints.append(a)
    joints.append(b)
    joints.append(c)
    joints.append(d)
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(700, 700)
    glutInitWindowPosition(0, 0)
    glutCreateWindow("I love inverse kinematics")
    glutDisplayFunc(myDisplay)
    glutReshapeFunc(myReshape)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 4, 18)
    gluLookAt(8, 8, 8, 0, 0, 0, 0, 0, 1)
    
    glutMainLoop()
