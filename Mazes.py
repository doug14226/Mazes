#Maze classes and functions
# -*- coding: utf-8 -*-
"""
Maze classes and functions

 The MIT License (MIT)

 Copyright (c) 2016 Sami Salkosuo

 Modified and extended by Doug Lange

 Copyright (c) 2017 Douglas Lange


 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.

 extentions added by Doug Lange include

   polar mazes
   Krushal mazes
   random over under passages
   cairo graphics Creation of .svg output
   json persistence of grid objects
   'new paint by numbers' with each cell numbered with
       path length from start to cell + path length from cell to exit.
       i.e. if cell is on the shortest path it will have the min number

   json format
   record 1
       [ class [ __init__ parameters]]
   record 2 to n
       [ [ location or index(s) ] [neighbors] [ linked? ]


Some mazes classes translated from Ruby
from book "Mazes for Programmers" by Jamis Buck.
https://pragprog.com/book/jbmaze/mazes-for-programmers

"""
import random
import math
import json
import re
import operator
from distances import Distances
import cairo

__version__ = 0.5

PROGRAMNAME = "Mazes"
VERSION = __version__
COPYRIGHT = "(C) 2017 Douglas Lange"



class Cell:
    """ one cell of a rectangular grid of cells """
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.directions = ('north', 'east', 'south', 'west')
        self.nearby = dict()      # key is direction (i.e. 'east') value is cell object
        self.links = dict()       #
        self.attributes = dict()  # like 'color', 'on path', 'deadend'

    def dumpCell(self, filename):
        myNearby = None
        myLinks =dict()
        for d in self.directions:
            k = self.nearby.get(d)
            if k is not None:
                myNearby = [k.row, k.column]
                l = self.links.get(k)
                if l:
                    myLinks[d] = myNearby
        thisObj = [[self.row, self.column], myLinks, self.attributes]
        jsonObj = json.dumps(thisObj)
        print(jsonObj, file=filename)

    def link(self, cell, bidi=True):
        self.links[cell] = True
        if bidi is True:
            cell.link(self, False)
        return self

    def unlink(self, cell, bidi=True):
        try:
            del self.links[cell]
        except KeyError:
            pass
        if bidi:
            cell.unlink(self, False)
        return self

    def getLinks(self):
        return self.links.keys()

    def linked(self, cell):
        #return self.links.has_key(cell)
        return cell in self.links

    def neighbors(self):
        myNeighbors = [self.nearby[d] for d in self.directions]
        return [x for x in filter(None, myNeighbors)]

    def directionToText(self, direction):
        if direction == 0:
            direction = "north"
        if direction == 1:
            direction = "east"
        if direction == 2:
            direction = "south"
        if direction == 3:
            direction = "west"

        return direction

    def getNeighbor(self, direction):
        direction = self.directionToText(direction)
        myNeighbor = self.nearby[direction]
        if self.links.get(myNeighbor):
            return myNeighbor

    def fillCell(self, ctx, pointsPerCell, hue):
        yU = self.row*pointsPerCell+4
        xL = self.column*pointsPerCell+4
        ctx.rectangle(xL, yU, pointsPerCell, pointsPerCell)
#       evenodd = (self.row+self.column) % 2
        ctx.set_source_rgb(*hue)
        ctx.fill()

    def drawCell(self, ctx, pointsPerCell, rows, columns):
        yU = self.row*pointsPerCell+4
        yL = yU+pointsPerCell
        xL = self.column*pointsPerCell+4
        xR = xL+pointsPerCell
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(4.0)
        if not(self.hasNeighbor("east")) and self.column < (columns-1):
            ctx.move_to(xR, yU-2)
            ctx.line_to(xR, yL+2)
            ctx.stroke()
        if not(self.hasNeighbor("south")) and self.row < (rows-1):
            ctx.move_to(xL, yL)
            ctx.line_to(xR, yL)
            ctx.stroke()

    def insetDrawCell(self, ctx, pointsPerCell):
        yU = self.row*pointsPerCell+4
        yL = yU+pointsPerCell
        xL = self.column*pointsPerCell+4
        xR = xL+pointsPerCell
        yUi = yU+3
        yLi = yL-3
        xLi = xL+3
        xRi = xR-3
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(4.0)
        if not self.hasNeighbor("east"):
            ctx.move_to(xRi, yUi-2)
            ctx.line_to(xRi, yLi+2)
            ctx.stroke()
        if not self.hasNeighbor("west"):
            ctx.move_to(xLi, yUi-2)
            ctx.line_to(xLi, yLi+2)
            ctx.stroke()
        if self.hasNeighbor("east") or self.attributes.get("EWpassage"):
            ctx.move_to(xRi-2, yUi)
            ctx.line_to(xLi+pointsPerCell+2, yUi)
            ctx.stroke()
            ctx.move_to(xRi-2, yLi)
            ctx.line_to(xLi+pointsPerCell+2, yLi)
            ctx.stroke()
        if not self.hasNeighbor("south"):
            ctx.move_to(xLi, yLi)
            ctx.line_to(xRi, yLi)
            ctx.stroke()
        if not self.hasNeighbor("north"):
            ctx.move_to(xLi, yUi)
            ctx.line_to(xRi, yUi)
            ctx.stroke()
        if self.hasNeighbor("south") or self.attributes.get("NSpassage"):
            ctx.move_to(xLi, yLi-2)
            ctx.line_to(xLi, yUi+pointsPerCell+2)
            ctx.stroke()
            ctx.move_to(xRi, yLi-2)
            ctx.line_to(xRi, yUi+pointsPerCell+2)
            ctx.stroke()

    def insetFillCell(self, ctx, pointsPerCell, hue = [1,1,1]):
        yU = self.row*pointsPerCell+4
        yL = yU+pointsPerCell
        xL = self.column*pointsPerCell+4
        xR = xL+pointsPerCell
        yUi = yU+3
        yLi = yL-3
        xLi = xL+3
        xRi = xR-3
        ctx.set_source_rgb(*hue)
        ctx.rectangle(xLi, yUi, pointsPerCell-6, pointsPerCell-6)
        ctx.fill()
        if self.hasNeighbor("east"):
            east = self.getNeighbor("east")
            tunnelEast = east.column - self.column - 1
            if tunnelEast:
                ctx.rectangle(xRi, yUi, 6, pointsPerCell-6)
                ctx.fill()
            else:
                ctx.rectangle(xRi, yUi, 3, pointsPerCell-6)
                ctx.fill()
        if self.hasNeighbor("south"):
            south = self.getNeighbor("south")
            tunnelSouth = south.row - self.row - 1
            if tunnelSouth:
                ctx.rectangle(xLi, yLi, pointsPerCell-6, 6)
                ctx.fill()
            else:
                ctx.rectangle(xLi, yLi, pointsPerCell-6, 3)
                ctx.fill()
        if self.hasNeighbor("west"):
            west = self.getNeighbor("west")
            tunnelWest = self.column - west.column - 1
            if tunnelWest:
                ctx.rectangle(xL-3, yUi, 6, pointsPerCell-6)
                ctx.fill()
            else:
                ctx.rectangle(xL, yUi, 3, pointsPerCell-6)
                ctx.fill()
        if self.hasNeighbor("north"):
            north = self.getNeighbor("north")
            tunnelNorth = self.row - north.row - 1
            if tunnelNorth:
                ctx.rectangle(xLi, yU-3, pointsPerCell-6, 6)
                ctx.fill()
            else:
                ctx.rectangle(xLi, yU, pointsPerCell-6, 3)
                ctx.fill()

    def hasNeighbor(self, direction):
        direction = self.directionToText(direction)
        myNeighbor = self.nearby[direction]
        return myNeighbor in self.links

    #return Distances from this cell to all other cells
    def getDistances(self, pallet=0):
        distances = Distances(self, rootPallet=pallet)
        frontier = []
        frontier.append(self)
        while len(frontier) > 0:
            newFrontier = []
            for cell in frontier:
                for linked in cell.getLinks():
                    if distances.getDistanceTo(linked) is None:
                        dist = distances.getDistanceTo(cell)
                        distances.setDistanceTo(linked, dist+1)
                        distances.setPallet(linked, pallet)
                        newFrontier.append(linked)
            frontier = newFrontier
        return distances
 
    #return Distances from this cell to all other cells in box
    def getDistancesInBox(self, box):
        distances = Distances(self)
        frontier = []
        frontier.append(self)
        while len(frontier) > 0 and len(box) > 0:
            newFrontier = []
            for cell in frontier:
                for linked in cell.getLinks():
                    if distances.getDistanceTo(linked) is None:
                        dist = distances.getDistanceTo(cell)
                        distances.setDistanceTo(linked, dist+1)
                        if linked in box:
                            box.remove(linked)
                        newFrontier.append(linked)
            frontier = newFrontier
        return distances



    def toString(self):
        return self.__str__()

    def __str__(self):
        output = "Cell[%d,%d], Linked neighbors: " % (self.row, self.column)
        for d in self.directions:
            c = self.nearby[d]
            if self.linked(c):
                output = output + " " + d +  ": YES "
            else:
                output = output + " " + d  + ": NO "
        return output



class Grid:

    def __init__(self, rows, columns, cellClass=Cell):
        self.CellClass = cellClass
        self.rows = rows
        self.columns = columns
        self.grid = self.prepareGrid()
        self.distances = None
        self.configureCells()
        self.pointsPerCell = 18
        self.start = None              # cell of path start
        self.goal = None               # cell of path goal
        self.background = None         # pallet for background
        self.deadends = None           # pallet for maze dead ends
        self.ctx = None
        self.coloring = None

    def prepareGrid(self):
        rowList = []
        i = 0
        j = 0
        for i in range(self.rows):
            columnList = []
            for j in range(self.columns):
                columnList.append(self.CellClass(i, j))
            rowList.append(columnList)
        return rowList

    def configureCells(self):
        for cell in self.eachCell():
            row = cell.row
            col = cell.column
            cell.nearby['north'] = self.getNeighbor(row-1, col)
            cell.nearby['east'] = self.getNeighbor(row, col+1)
            cell.nearby['south'] = self.getNeighbor(row+1, col)
            cell.nearby['west'] = self.getNeighbor(row, col-1)

    def eachRow(self):
        for row in self.grid:
            yield row

    def eachCell(self):
        for row in self.grid:
            for cell in row:
                yield cell

    def listDeadends(self):
#    def listDeadends(self,filename):
#        fh = open(fileName, "w", encoding="utf8")
        for cell in self.eachCell():
            if len(cell.links) == 1: # if a deadend
                deadend = cell
                pathcell = deadend
                d = self.distances.cells.get(pathcell, 0)
                while d > 0:
                    for neighbor in pathcell.getLinks():
                        n = self.distances.cells.get(neighbor, 0)
                        if n < d:
                            pathcell = neighbor
                            d = n
                            break
                print("Deadend ", deadend, pathcell)
                        

    def drawGrid(self, filename):
        WIDTH, HEIGHT = self.columns*self.pointsPerCell+8, self.rows*self.pointsPerCell+8
        drawFile = filename + ".SVG"
        surface = cairo.SVGSurface(drawFile, WIDTH, HEIGHT)
        self.ctx = cairo.Context(surface)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        if self.coloring is not None:
            for row in self.grid:
                for cell in row:
                    d = self.distances.cells.get(cell, 0)
                    hue = self.coloring.cellRGB(d, cell)
                    cell.fillCell(self.ctx, self.pointsPerCell, hue)
        for row in self.grid:
            for cell in row:
                cell.drawCell(self.ctx, self.pointsPerCell, self.rows, self.columns)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(4)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.rectangle(4, 4, self.columns*self.pointsPerCell, self.rows*self.pointsPerCell)
        self.ctx.stroke()

    def insetDrawGrid(self, filename):
        WIDTH, HEIGHT = self.columns*self.pointsPerCell+8, self.rows*self.pointsPerCell+8
        drawFile = filename + ".SVG"
        surface = cairo.SVGSurface(drawFile, WIDTH, HEIGHT)
        self.ctx = cairo.Context(surface)
        self.ctx.set_source_rgb(.549, .549, .549)
        self.ctx.set_source_rgb(1.0, 1.0, 1.0)
        self.ctx.set_line_width(4)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.rectangle(4, 4, self.columns*self.pointsPerCell, self.rows*self.pointsPerCell)
        self.ctx.fill()
        if self.coloring is not None:
            for row in self.grid:
                for cell in row:
                    d = self.distances.cells.get(cell, 0)
#                    c = int(d/2)
#                    if c > 8:
#                        c = 8
                    hue = self.coloring.cellRGB(d, cell)
                    cell.insetFillCell(self.ctx, self.pointsPerCell, hue)
        else:
            for row in self.grid:
                for cell in row:
                    cell.insetFillCell(self.ctx, self.pointsPerCell)
        for row in self.grid:
            for cell in row:
                cell.insetDrawCell(self.ctx, self.pointsPerCell)

    def drawOpening(self,cell):
        """ for now just support left and right opennings """
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        if self.coloring is None:
            hue = (1, 1, 1)
        else:
            hue = self.coloring.cellRGB(0, cell)
        self.ctx.set_source_rgb(*hue)
        self.ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        if cell.column == 0:
            self.ctx.move_to(4, 4+2+(cell.row*self.pointsPerCell))
            self.ctx.line_to(4, 4-2+((cell.row+1)*self.pointsPerCell))
            self.ctx.stroke()
        if cell.column == self.columns - 1:
            self.ctx.move_to(self.columns*self.pointsPerCell+4,
                             (cell.row*self.pointsPerCell+4+2))
            self.ctx.line_to(self.columns*self.pointsPerCell+4,
                             (4-2+(cell.row+1)*self.pointsPerCell))
            self.ctx.stroke()

    def dumpGrid(self, filename):
        thisObj = [str(type(self)), [self.rows, self.columns]]
        jsonObj = json.dumps(thisObj)
        print(jsonObj, file=filename)
        for row in self.grid:
            for cell in row:
                cell.dumpCell(filename)

    def getCell(self, row, column):

        return self.grid[row][column]
        #return self.grid[row-1][column-1]

    def getNeighbor(self, row, column):
        if not 0 <= row < self.rows:
            return None
        if not 0 <= column < self.columns:
            return None
        return self.grid[row][column]

    def size(self):
        return self.rows*self.columns

    def randomCell(self):
        row = random.randint(0, self.rows-1)
#        column = self.grid
        column = random.randint(0, len(self.grid[row])-1)
        return self.grid[row][column]

    def contentsOf(self, cell):
        return "   "

    def getDeadEndCells(self):
        deadends = []
        for cell in self.eachCell():
            if len(cell.getLinks()) == 1:
                deadends.append(cell)
        return deadends

    def braid(self, p=1.0):
        deadends = self.getDeadEndCells()
        random.shuffle(deadends)
        j = len(deadends)
        for i in range(j):
            cell = deadends[i]
            myNeighbors = cell.neighbors()
            myLinks = cell.getLinks()
            possibleLinks = []
            if len(myLinks) == 1 and random.random() <= p:
                for n in myNeighbors:
                    if n not in myLinks:
                        possibleLinks.append(n)
                otherDeadEnds = list(filter(lambda x: len(x.getLinks()) == 1, possibleLinks))
                if len(otherDeadEnds):
                    l =random.choice(otherDeadEnds)
                else:
                    l = random.choice(possibleLinks)
                cell.link(l)
        

        

    def __str__(self):
        return self.asciiStr()

    def unicodeStr(self):
        pass

    def asciiStr(self):
        output = "+" + "---+" * self.columns + "\n"
        for row in self.eachRow():
            top = "|"
            bottom = "+"
            for cell in row:
                if not cell:
                    cell = Cell(-1, -1)
                body = "%s" % self.contentsOf(cell)
                if cell.linked(cell.nearby.get('east')):
                    east_boundary = " "
                else:
                    east_boundary = "|"

                top = top + body + east_boundary
                if cell.linked(cell.nearby.get('south')):
                    south_boundary = "   "
                else:
                    south_boundary = "---"
                corner = "+"
                bottom = bottom + south_boundary + corner

            output = output+top+"\n"
            output = output+bottom+"\n"
        return output

    def getDistancesFromPath(self, start, goal, pallet=0):
        distancesToStart = start.getDistances(pallet)
        distancesToGoal = goal.getDistances(pallet)
        pathLength = distancesToGoal.getDistanceTo(start)
        sumDistances = distancesToStart + distancesToGoal
        return (sumDistances - pathLength)

    def getMaxFractalDistances(self):
        fractalDistances = Distances(None)
        for lrow in self.grid:
            for cell in lrow:
                box = []
                fd = 0
                r = cell.row
                c = cell.column
                if (c - 1) >= 0 :
                    box.append(self.grid[r][c-1])
                if (r - 1) >= 0 :
                    box.append(self.grid[r-1][c])
                if (c + 1) < self.columns :
                    box.append(self.grid[r][c+1])
                if (r + 1) < self.rows :
                    box.append(self.grid[r+1][c])
                distancesInBox = cell.getDistancesInBox(box)
                if (c - 1) >= 0 :
                    d = distancesInBox.getDistanceTo(self.grid[r][c-1])
                    if d > fd:
                        fd = d
                if (r - 1) >= 0 :
                    d = distancesInBox.getDistanceTo(self.grid[r -1 ][c])
                    if d > fd:
                        fd = d
                if (c + 1) < self.columns :
                    d = distancesInBox.getDistanceTo(self.grid[r][c+1])
                    if d > fd:
                        fd = d
                if (r + 1) <  self.rows :
                    d = distancesInBox.getDistanceTo(self.grid[r+1][c])
                    if d > fd:
                        fd = d
                fractalDistances.setDistanceTo(cell, fd)
        return fractalDistances


class DistanceGrid(Grid):

    def contentsOf(self, cell):
        if  (self.distances.getDistanceTo(cell) is not None and
             self.distances.getDistanceTo(cell) is not None):
            n = self.distances.getDistanceTo(cell)
            return "%03d" % n
        else:
            return "   " #super(Grid, self).contentsOf(cell)


