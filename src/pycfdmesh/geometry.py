'''
This file is a part of BreezyNS - a simple, general-purpose 2D airflow calculator.

Copyright (c) 2013, Brendan Gray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.



Created on 26 Nov 2013

@author: AlphanumericSheepPig
'''

import math
import copy
from pycfdalg.usefulstuff import floatRange


class Point():

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def scaledBy(self, factor):
        '''
        Returns a point scaled by some factor. Original point is unmodified.
        Use "p = p.scaledBy(factor)" to modify original point.
        '''
        return Point(self.x*factor, self.y*factor) 
    
    def switchReference(self, pageHeight):
        '''
        Returns a new point in the other reference frame. The two reference frames are:
            1) Screen coords: positive y is downward and origin is the top left. 
            2) Graph coords: positive y is upward and origin is the bottom left.
        Original point is unmodified.
        Use "p = p.switchReference(pageHeight)" to modify the original point.
        '''
        return Point(self.x, pageHeight - self.y)
    
    def sqrDistTo(self, other):
        return (self.x-other.x)*(self.x-other.x) + (self.y-other.y)*(self.y-other.y) 
        
    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)
    
    def __repr__(self):
        return str("( {}, {} )".format(self.x, self.y))


class BoundingBox():
    
    def __init__(self, center, halfWidth, halfHeight = None):
        self.center = center
        self.halfWidth = halfWidth
        if not halfHeight:
            self.halfHeight = halfWidth
        else:
            self.halfHeight = halfHeight
        self.left = center.x - self.halfWidth
        self.right = center.x + self.halfWidth
        self.top = center.y + self.halfHeight
        self.bottom = center.y - self.halfHeight
         
        
        
    def containsPoint(self, point):
        if abs(point.x - self.center.x) <= self.halfWidth:
            if abs(point.y - self.center.y) <= self.halfHeight:
                return True
        return False
    
    
    def containsLine(self, line):
        return self.containsPoint(line.startPoint) and self.containsPoint(line.endPoint)
        
    
    def getPointList(self):
        topLeft     = Point(self.center.x-self.halfWidth, self.center.y+self.halfHeight)
        topRight    = Point(self.center.x+self.halfWidth, self.center.y+self.halfHeight)
        bottomRight = Point(self.center.x+self.halfWidth, self.center.y-self.halfHeight)
        bottomLeft  = Point(self.center.x-self.halfWidth, self.center.y-self.halfHeight)
        
        return PointList(topLeft, topRight, bottomRight, bottomLeft, topLeft)
    
    def getPolygon(self):
        p = Polygon()
        p.createFromPointList(self.getPointList())
        print("Creating from point list:",p)
        return p
    
    def __add__(self, other):
        '''
        Returns the intersection between two bounding boxes, or None if the boxes don't intersect.
        '''
        # Check if a box is too high or too low
        if self.bottom > other.top or self.top < other.bottom:
            return None
        # Check if a box is too far to the side
        if self.left > other.right or self.right < other.left:
            return None
        
        newTop = min(self.top, other.top)
        newBottom = max(self.bottom, other.bottom)
        newLeft = max(self.left, other.left)
        newRight = min(self.right, other.right)
        
        newCenter = Point((newLeft+newRight)/2, (newTop+newBottom)/2)
        halfWidth = abs(newLeft-newRight)/2
        halfHeight = abs(newTop-newBottom)/2
        
        return BoundingBox(newCenter, halfWidth, halfHeight)
    
    
    def __repr__(self):
        return "Bounding box x: ("+str(self.left)+"--"+str(self.right)+"), y: ("+str(self.bottom)+"--"+str(self.top)+")"
    



class PointList():
    
    def __init__(self, *points):
        self.points = []
        for p in points:
            self.points.append(p)
    
    def addPoint(self, point):
        self.points.append(point)
        
    def getXs(self):
        ''' Returns a list of the x values of each point. ''' 
        xs = []
        for p in self.points:
            xs.append(p.x)
        return xs
    
    def getYs(self):
        ''' Returns a list of the x values of each point. ''' 
        ys = []
        for p in self.points:
            ys.append(p.y)
        return ys
    
    def length(self):
        return len(self.points)
    
    def __add__(self, other):
        ''' Concatenation of two PointLists '''
        combined = PointList()
        for p in self.points:
            combined.addPoint(p)
        for p in other.points:
            combined.addPoint(p)
        return combined
    
        

class CubicBezier():
    
    def __init__(self, startPoint, firstControl, secondControl, endPoint):
        self.p0 = startPoint
        self.p1 = firstControl
        self.p2 = secondControl
        self.p3 = endPoint
    
    def getPoint(self, t):
        term0 = self.p0.scaledBy((1-t)*(1-t)*(1-t)) 
        term1 = self.p1.scaledBy(t*(1-t)*(1-t)*3)
        term2 = self.p2.scaledBy(t*t*(1-t)*3)
        term3 = self.p3.scaledBy(t*t*t)
        
        return term0 + term1 + term2 + term3
    
    def getUniformPointList(self, npoints = 20):
        stepsize = 1/npoints
        points = PointList()
        for t in floatRange(0, 1+stepsize, stepsize):
            points.addPoint(self.getPoint(t))
        return points
    
    def getDefiningPoints(self):
        endPoints = PointList(self.p0, self.p3)
        controlPoints = PointList(self.p1, self.p2)
        return endPoints, controlPoints

    def splitCurve(self):
        '''
        Splits the Bezier curve into two at the point t=0.5.
        '''
        p0 = self.p0
        p3 = self.p3
        p01 = (self.p0 + self.p1).scaledBy(1/2)
        p12 = (self.p1 + self.p2).scaledBy(1/2)
        p23 = (self.p2 + self.p3).scaledBy(1/2)
        p012 = (p01 + p12).scaledBy(1/2)
        p123 = (p12 + p23).scaledBy(1/2)
        p0123 = (p012 + p123).scaledBy(1/2)
        
        return CubicBezier(p0, p01, p012, p0123), CubicBezier(p0123, p123, p23, p3)
    
    
    def curvature(self, t):
        '''
        Returns the curvature of the curve at a given point.
        '''
        x0 = self.p0.x
        x1 = self.p1.x
        x2 = self.p2.x
        x3 = self.p3.x

        y0 = self.p0.y
        y1 = self.p1.y
        y2 = self.p2.y
        y3 = self.p3.y
        
        xd1 = 3*(1-t)*(x1-x0) + 6*(1-t)*t*(x2-x1) + 3*t*t*(x3-x2)
        yd1 = 3*(1-t)*(y1-y0) + 6*(1-t)*t*(y2-y1) + 3*t*t*(y3-y2)
        xd2 = 6*(1-t)*(x2-2*x1+x0) + 6*t*(x3-2*x2+x1)
        yd2 = 6*(1-t)*(y2-2*y1+y0) + 6*t*(y3-2*y2+y1)
        
        if (xd1*xd1 + yd1*yd1)==0:
            # Possible if a control point was not distinct
            return 0
        
        return (xd1*yd2 - yd1*xd2)/((xd1*xd1 + yd1*yd1)**1.5)
        
    

        
        
    def isLinear(self, distRelTolerence = 0.1, distAbsTolerance = 0.01, angleTolerance = 2*math.pi/180):

        # First, check end points are distinct
        dist03 = ((self.p3.y-self.p0.y)*(self.p3.y-self.p0.y)+(self.p3.x-self.p0.x)*(self.p3.x-self.p0.x))
        if dist03 < distAbsTolerance:
            return True
        
        # Second, check that at least one control point is distinct. If not, then it's a line.
        dist01 = ((self.p1.y-self.p0.y)*(self.p1.y-self.p0.y)+(self.p1.x-self.p0.x)*(self.p1.x-self.p0.x))
        dist23 = ((self.p3.y-self.p2.y)*(self.p3.y-self.p2.y)+(self.p3.x-self.p2.x)*(self.p3.x-self.p2.x))
        if dist01 < distAbsTolerance and dist23 < distAbsTolerance:
            return True

        # Now calculate the shortest distances from the control points to a line joining the end points
        dist1_03 = abs((self.p1.x - self.p3.x)*(self.p3.y-self.p0.y) - (self.p1.y - self.p3.y)*(self.p3.x-self.p0.x))
        dist2_03 = abs((self.p2.x - self.p3.x)*(self.p3.y-self.p0.y) - (self.p2.y - self.p3.y)*(self.p3.x-self.p0.x))

        actualDist = (dist1_03+dist2_03)*(dist1_03+dist2_03)
        maxDist = dist03 * distRelTolerence
        # If the control points are far away, we know the curve is not linear.
        if actualDist > maxDist:
            return False
        
        # As a final check, we want to ensure that the angle between the tangents to the end points is reasonable.
        # There's a complication to be dealt with if either control point is not distinct.
        if dist01 < distAbsTolerance:
            a1 = math.atan2(self.p2.y - self.p0.y, self.p2.x - self.p0.x)
        else:
            a1 = math.atan2(self.p1.y - self.p0.y, self.p1.x - self.p0.x)
        if dist23 < distAbsTolerance:
            a2 = math.atan2(self.p1.y - self.p3.y, self.p1.x - self.p3.x)
        else:
            a2 = math.atan2(self.p2.y - self.p3.y, self.p2.x - self.p3.x)
        angle = math.pi - abs(a1-a2)
        
        if abs(angle) > angleTolerance:
            return False
        

     
        return True
        
    
    def toLine(self):
        return StraightLine(self.p0, self.p3)
    
    def __str__(self):
        return "Bezier: "+str(self.p0)+" "+str(self.p1)+" "+str(self.p2)+" "+str(self.p3)


class CurveList():
    
    def __init__(self, curveList=[]):
        self.curves = []
        for c in curveList:
            self.curves.append(c)
    
    def getUniformPointList(self, npoints):
        points = PointList()
        for c in self.curves:
            points += c.getUniformPointList(npoints)
        return points
    
    def getDefiningPoints(self):
        endPoints = PointList()
        controlPoints = PointList()
        for c in self.curves:
            end,cont = c.getDefiningPoints()
            endPoints += end
            controlPoints += cont 

        return endPoints, controlPoints
    
    def nCurves(self):
        return len(self.curves)

    def refine(self, distTolerence = 0.1, angleTolerence = 0.05):
        '''
        Refines the shape by replacing each curves with significant curvature with two equivalent curves.
        '''
        newCurves = []
        for c in self.curves:
            if not c.isLinear(distTolerence):
                c1, c2 = c.splitCurve()
                newCurves.append(c1)
                newCurves.append(c2)
            else:
                newCurves.append(c)
        return CurveList(newCurves)
    
    def repeatedlyRefine(self, maxSize = 1000):
        '''
        Repeatedly refines the shape until all curves are approximately linear.
        '''
        lastSize = 0
        currentSize = self.nCurves()
        newCurves = copy.deepcopy(self)
        while (currentSize < maxSize) and currentSize > lastSize:
            newCurves = newCurves.refine()
            lastSize = currentSize
            currentSize = newCurves.nCurves()
        return newCurves
    
    
    def toLineList(self):
        lineList = []
        for c in self.curves:
            lineList.append(c.toLine())
        return LineList(lineList)
    
        
                
    
    def __str__(self):
        res = "CurveList:\n"
        for c in self.curves:
            res += "    "+str(c) + "\n"
        return res
        

class Beziergon(CurveList):
    def __str__(self):
        res = "Beziergon:\n"
        for c in self.curves:
            res += "    "+str(c) + "\n"
        return res

    def refine(self, distTolerence = 0.1, angleTolerence = 0.05):
        newCurves = CurveList.refine(self, distTolerence, angleTolerence).curves
        return Beziergon(newCurves)
    
    def approximateByPolygon(self, maxSides = 1000):
        return self.repeatedlyRefine(maxSides).toLineList()
    
    def toPolygon(self):
        return Polygon(self.toLineList().lines)



class StraightLine():
    '''
    Represents a line segment between two points.
    '''
    
    def __init__(self, startPoint, endPoint):
        self.startPoint = startPoint
        self.endPoint = endPoint
    
    def getDefiningPoints(self):
        return PointList(self.startPoint, self.endPoint)
    
    def length(self):
        return math.sqrt(self.startPoint.sqrDistTo(self.endPoint))
    
    def intersectsWith(self, other):
        '''
        Returns True if two line segments intersect between their start and end points, and False otherwise.
        '''
        intersectionRegion = self.getBoundingBox() + other.getBoundingBox()
        if not intersectionRegion:
            return False
        
        m1 = (self.startPoint.y - self.endPoint.y)/(self.startPoint.x - self.endPoint.x)
        m2 = (other.startPoint.y - other.endPoint.y)/(other.startPoint.x - other.endPoint.x)
        c1 = self.startPoint.y - m1*self.startPoint.x
        c2 = other.startPoint.y - m2*other.startPoint.x
        
        # Check degenerate case if lines are parallel
        if m1 == m2:
            return c1 == c2
        
        # Otherwise there is a single intersection point. 
        x = (c2-c1)/(m1-m2)
        y = m1*x+c1
        
        intersectionPoint = Point(x, y)
        
        # If the line segments intersect, then the intersection point must lie within the intersection region.
        if intersectionRegion.containsPoint(intersectionPoint):
            return True
        else:
            return False
        
        
    def getBoundingBox(self):
        top = max(self.startPoint.y, self.endPoint.y)
        bottom = min(self.startPoint.y, self.endPoint.y)
        left = min(self.startPoint.x, self.endPoint.x)
        right = max(self.startPoint.x, self.endPoint.x)
        
        center = Point((left+right)/2, (top+bottom)/2)
        halfWidth = abs(left-right)/2
        halfHeight = abs(top-bottom)/2
        
        return BoundingBox(center, halfWidth, halfHeight)

    def __repr__(self):
        return "Straight line of length "+str(self.length())+" from "+str(self.startPoint)+" to "+str(self.endPoint)

                
class LineList():
    
    def __init__(self, lineList=[]):
        self.lines = []
        for c in lineList:
            self.lines.append(c)

    def getDefiningPoints(self):
        if len(self.lines) == 0:
            return PointList()
        pointsList = PointList(self.lines[0].startPoint)
        for line in self.lines:
            pointsList.addPoint(line.endPoint)
        return pointsList
    
    
    def createFromPointList(self, pointList):
        self.lines = []
        if pointList.length()<2:
            return
        
        
        points = pointList.points
        for i in range(1,len(points)):
            self.lines.append(StraightLine(points[i-1], points[i]))
        
        return self
    
    
    def removeZeroLengthLines(self):
        newLineList = []
        for line in self.lines:
            if line.length() > 0:
                newLineList.append(line)
        return LineList(newLineList)
    
    
    def removeShortLines(self, minLength):
        newLineList = []
        currentStart = 0
        for i in range(len(self.lines)):
            startPoint = self.lines[currentStart].startPoint
            endPoint = self.lines[i].endPoint
            newLine = StraightLine(startPoint, endPoint)
            if newLine.length() >= minLength:
                newLineList.append(newLine)
                currentStart = i+1
        return LineList(newLineList)
        
    def toPolygon(self):
        return Polygon(self.lines)
        
        
class Polygon(LineList):
    
    def __init__(self, lineList=[]):
        LineList.__init__(self, lineList)
        self.calculateBoundingBox()
    

    def calculateBoundingBox(self):
        '''
        This forces the bounding box to be recalculated. If the polygon hasn't changed, rather use Polygon.getBoundingBox()
        '''
        if len(self.lines) == 0:
            self.boundingBox = None
            return None 
        
        
        xmin = self.lines[0].startPoint.x
        xmax = self.lines[0].startPoint.x
        ymin = self.lines[0].startPoint.y
        ymax = self.lines[0].startPoint.y
        for line in self.lines:
            thisXmin = min(line.startPoint.x, line.endPoint.x)
            thisXmax = max(line.startPoint.x, line.endPoint.x)
            if thisXmin < xmin: xmin = thisXmin
            elif thisXmax > xmax: xmax = thisXmax
            thisYmin = min(line.startPoint.y, line.endPoint.y)
            thisYmax = max(line.startPoint.y, line.endPoint.y)
            if thisYmin < ymin: ymin = thisYmin
            elif thisYmax > ymax: ymax = thisYmax
        center = Point((xmin+xmax)/2, (ymin+ymax)/2)
        halfWidth = abs(xmax-xmin)/2
        halfHeight = abs(ymax-ymin)/2
        self.boundingBox = BoundingBox(center, halfWidth, halfHeight)
        return self.boundingBox
    
    
    def getBoundingBox(self):
        '''
        Assumes that the polygon has not change since the bounding box was last calculated.
        '''
        return self.boundingBox
    
    
    def containsPoint(self, point):
        '''
        Uses a simple ray casting algorithm to determine if a point lies inside a polygon. 
        '''
        self.getBoundingBox()
        if not self.boundingBox.containsPoint(point):
            return False
        
        rayStart = Point(self.boundingBox.left, point.y)
        ray = StraightLine(rayStart, point)
        
        intersectionCount = 0
        for line in self.lines:
            # print ("    Testing point",point,"and line",line)
            if ray.intersectsWith(line):
                intersectionCount += 1
                # print ("        Intersection count", intersectionCount)
        if intersectionCount % 2 == 1:
            return True
        else:
            return False
            
            
    def containsBoundingBox(self, boundingBox):
        '''
        Returns true if all four corners of the boundingBox are contained inside the polygon.
        '''
        for point in boundingBox.getPointList().points:
            if not self.containsPoint(point):
                return False
        return True
        
        
        
    def __repr__(self):
        s = "Polygon with "+str(len(self.lines))+" sides:"
        for line in self.lines:
            s += "\n    "+str(line)
        return s
        
        
            
                
    
    
            
        
        