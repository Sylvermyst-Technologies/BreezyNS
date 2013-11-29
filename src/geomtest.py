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

import pylab
from pycfdmesh.svgloader import beziergonsFromSVG



def plotBezierGroup(blist):
    for b in blist:
        points = b.getUniformPointList(20)
        endPoints, controlPoints = b.getDefiningPoints()
        pylab.plot(points.getXs(), points.getYs(),'k-')
        pylab.plot(endPoints.getXs(), endPoints.getYs(),'ko')
        pylab.plot(controlPoints.getXs(), controlPoints.getYs(),'kx')
    pylab.axis('equal')
    

def plotPolygonGroup(polyList, style='k-'):
    for p in polyList:
        points = p.getDefiningPoints()
        pylab.plot(points.getXs(), points.getYs(), style)
        #print(points.length())
    pylab.axis('equal')
        

def test2():
    blist = beziergonsFromSVG('./inputgeometries/arbshape6.svg')
    #pylab.figure('Original Image')
    #plotBezierGroup(blist)
    
    polygonList = []
    for b in blist:
        polygonList.append(b.approximateByPolygon())
                 
    pylab.figure('Polygon Image')
    plotPolygonGroup(polygonList)
    
    pylab.show()
        

if __name__ == "__main__":
    test2()
    
    
    