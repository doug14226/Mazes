#Maze Color classes and functions
# -*- coding: utf-8 -*-
"""
Maze Coloring classes and functions

 The MIT License (MIT)


author Doug Lange

A mazeColoring object maps the distance of a cell (usually distance off the path)
to an RGB value. Developed to seperate a maze from it's painting

 Copyright (c) 2017 Douglas Lange
 
"""
 
import math

class mazeColoring:
    
    def __init__(self, myMaze, myPallet , pallet2 = None):
        self.pallet = myPallet
        self.pallet2 = pallet2
        self.grid = myMaze
    
    def cellRGB(self, distanceValue, Cell):
        l =len(self.pallet)
        i = min(l-1, distanceValue)
        return self.pallet[i]

class myFirstMazeColloring(mazeColoring):

    def cellRGB(self, distanceValue, Cell):
        norm = math.sqrt(self.grid.rows**2 + self.grid.columns**2)
        c = int(distanceValue * 3 / norm) +2
        if c > 7:
            c = 7
        if distanceValue == 0:
            c = 1
        hue = self.pallet[c]
        if distanceValue > 0:
            if len(Cell.links) == 1:
                for ncell in Cell.links.keys():
                    if len(ncell.links) == 2:
                        hue = self.pallet2[c]
        return hue                          

class distanceHistogram:
    
    def __init__(self, distance):
        self.cdf  = [0.0 for count in range(distance.max()+2)]
        self.counts = self.buildHisto(distance)
        

    def buildHisto(self,distance):
        cnt = [0 for count in range(distance.max()+1)]
        histoCells = distance.getCells()
        ncells = 0
        for c in histoCells:
            ncells = ncells +1
            this = distance.getDistanceTo(c)
            cnt[this] = cnt[this] + 1
        lessThan = 0
        for i in range(len(cnt)):
            self.cdf[i] = lessThan / ncells
            lessThan = lessThan + cnt[i]
        self.cdf[-1] = 1.0
        return cnt
                

    def cdf(self, value):
        pass

    def pdf(self, value):
        pass



# end of classes functions follow

def interpolatePallet(pallet, distance):
    disHisto = distanceHistogram(distance)
    newPallet = []
    j = len(disHisto.cdf)
    for i in range(j):
        p = disHisto.cdf[i]
        if p < 1.0:
            x = p * (len(pallet)-1)
            k = int(x)
            l = k + 1
            a = x - k
            c1 = pallet[k]
            c2 = pallet[l]
            r1 = c1[0]
            g1 = c1[1]
            b1 = c1[2]
            r2 = c2[0]
            g2 = c2[1]
            b2 = c2[2]
            r = r1 + a * (r2 -r1)
            g = g1 + a * (g2 -g1)
            b = b1 + a * (b2 -b1)
            newPallet.append([r,g,b]) 
        else:
            newPallet.append(pallet[-1])
    return newPallet       