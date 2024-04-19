""" extension of Cell and Grid to polar Mazes

(C) 2017 Douglas Lange

"""

import math
import json
import Mazes
import cairo

class PolarCell(Mazes.Cell):

    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.myGrid = None
        self.directions = ('in', 'cw', 'outcw', 'out', 'outccw', 'ccw')
        self.nearby = dict()      # key is direction (i.e. 'east') value is cell object
        self.links = dict()       #

    def fillCell(self, ctx, pointsPerCell, rows, columns, center, hue):
        incAngle = 2 * math.pi * (1 / columns)
        startAngle = self.column * incAngle
        endAngle = startAngle + incAngle
        radiusI = (self.row + self.myGrid.radiusRow1) * pointsPerCell
        radiusO = radiusI + pointsPerCell
        ctx.move_to(center + (radiusI * math.cos(endAngle)),
                    center + (radiusI * math.sin(endAngle)))
        ctx.new_path()
        ctx.arc_negative(center, center, radiusI, endAngle, startAngle)
        ctx.arc(center, center, radiusO, startAngle, endAngle)
        ctx.close_path()
        evenodd = (self.row+self.column) % 2
        ctx.set_source_rgb(*hue)
        ctx.fill()

    def drawCell(self, ctx, pointsPerCell, rows, columns, center):
        incAngle = 2 * math.pi * (1 / columns)
        startAngle = self.column * incAngle
        endAngle = startAngle + incAngle
        midAngle = startAngle + (incAngle / 2)
        radiusI = (self.row + self.myGrid.radiusRow1) * pointsPerCell 
        radiusO = radiusI + pointsPerCell 
        ctx.new_path()
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(4.0)
        if not self.hasNeighbor("cw"):
            ctx.set_line_cap(cairo.LINE_CAP_BUTT)
            ctx.move_to(center + ((radiusI -2) * math.cos(endAngle)),
                        center + ((radiusI -2) * math.sin(endAngle)))
            ctx.line_to(center + ((radiusO +2) * math.cos(endAngle)),
                        center + ((radiusO +2) * math.sin(endAngle)))
            ctx.stroke()
        if self.row < (rows-1):
            #
            # FFF   no neighbor fill all
            # FTF   a neighbor  fill none
            # TFT   two neighbors fill none
            # TFF   fill start to mid
            # FFT   fill  mid to end
            # TTT   FTT  and TTT are impossible (fill none or all)
            #
            if (self.hasNeighbor("out") or
                    (self.hasNeighbor("outcw") and self.hasNeighbor("outccw"))):
                return
            if (not self.hasNeighbor("out") and not self.hasNeighbor("outcw") and
                    not self.hasNeighbor("outccw")):
                ctx.set_line_cap(cairo.LINE_CAP_BUTT)
                ctx.arc(center, center, radiusO, startAngle, endAngle)
                ctx.stroke()
            else:
                if not self.hasNeighbor("outcw"):
                    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
                    ctx.arc(center, center, radiusO, midAngle, endAngle)
                    ctx.stroke()
                if not self.hasNeighbor("outccw"):
                    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
                    ctx.arc(center, center, radiusO, startAngle, midAngle)
                    ctx.stroke()


class PolarGrid(Mazes.Grid):
    
    def __init__(self, radiusRow1, rows, columnsRow1, cellClass=PolarCell):
        self.CellClass = cellClass
        self.radiusRow1 = radiusRow1
        self.rows = rows
        self.columnsRow1 = columnsRow1
        self.columnsPerRow = []
        self.grid = self.prepareGrid()
        self.distances = None
        self.configureCells()
        self.algorithm = None
        self.pointsPerCell = 18
        self.start = []                # cell of path start
        self.goal = []                 # cell of path goal
        self.background = None         # pallet for background
        self.deadends = None           # pallet for maze dead ends

    def prepareGrid(self):
        columns = self.columnsRow1
        doubleRow = self.radiusRow1
        if doubleRow == 0:
            doubleRow = 2
        rowList = []
        i = 0
        j = 0
        for i in range(self.rows):
            radiusThisRow = self.radiusRow1 + i
            if radiusThisRow > doubleRow:
                columns = 2 * columns
                doubleRow = 2 * doubleRow
            self.columnsPerRow.append(columns)
            columnList = []
            for j in range(columns):
                columnList.append(self.CellClass(i, j))
            rowList.append(columnList)
        print(self.columnsPerRow)
        return rowList


    def configureCells(self):
        for cell in self.eachCell():
            cell.myGrid = self
            row = cell.row
            col = cell.column
            colThisRow = self.columnsPerRow[row]
            if row < self.rows -1:
                colNextRow = self.columnsPerRow[row+1]
            else:
                colNextRow = colThisRow
            if row > 0:
                colLastRow = self.columnsPerRow[row-1]
            else:
                colLastRow = colThisRow
            colnrow = col
            collrow = col
            if colThisRow < colNextRow:
                colnrow = col * 2
            if colLastRow < colThisRow:
                collrow = col // 2
            cell.nearby['in'] = self.getNeighbor(row-1, collrow)
            cell.nearby['cw'] = self.getNeighbor(row, col+1)
            if colThisRow < colNextRow:
                cell.nearby['outcw'] = self.getNeighbor(row+1, colnrow+1)
                cell.nearby['outccw'] = self.getNeighbor(row+1, colnrow)
                cell.nearby['out'] = None
            else:
                cell.nearby['outcw'] = None
                cell.nearby['outccw'] = None
                cell.nearby['out'] = self.getNeighbor(row+1, colnrow)
            cell.nearby['ccw'] = self.getNeighbor(row, col-1)

    def dumpGrid(self, filename):
        thisObj = [str(type(self)), [self.radiusRow1, self.rows, self.columnsRow1]]
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
        if column < 0:
            column = self.columnsPerRow[row] + column
        if column >= self.columnsPerRow[row]:
            column = column - self.columnsPerRow[row]
        return self.grid[row][column]

    def size(self):
        return self.rows*self.columns



    def drawGrid(self, filename):
        sizeDrawing = 2*(self.radiusRow1 + self.rows) * self.pointsPerCell + 9
        center = (self.radiusRow1 + self.rows) * self.pointsPerCell + 4
        drawFile = filename + ".SVG"
        surface = cairo.SVGSurface(drawFile, sizeDrawing, sizeDrawing)
        self.ctx = cairo.Context(surface)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        if self.background is not None:
            for row in self.grid:
                for cell in row:
                    d = self.distances.cells.get(cell, 0)
                    norm = math.sqrt(4*self.rows**2)
                    c = int(d * 3 / norm) +2
                    if c > 7:
                        c = 7
                    if d == 0:
                        c = 1
                    hue = self.background[c]
                    irow = cell.row
                    cell.fillCell(self.ctx, self.pointsPerCell, self.rows,
                                  self.columnsPerRow[irow], center, hue)
                    if d > 0:
                        if len(cell.links) == 1:
                            for ncell in cell.links.keys():
                                if len(ncell.links) == 2:
                                    hue = self.deadends[c]
                                    cell.fillCell(self.ctx, self.pointsPerCell, self.rows,
                                                  self.columnsPerRow[irow], center, hue)
        for row in self.grid:
            for cell in row:
                irow = cell.row
                cell.drawCell(self.ctx, self.pointsPerCell,
                              self.rows, self.columnsPerRow[irow], center)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(4)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.arc(center, center,
                     (self.radiusRow1 + self.rows) * self.pointsPerCell, 0, 2 * math.pi)
        self.ctx.stroke()
        self.ctx.arc(center, center,
                     self.radiusRow1 * self.pointsPerCell, 0, 2 * math.pi)
        self.ctx.stroke()

    def drawOpening(self, cell):
        center = (self.radiusRow1 + self.rows) * self.pointsPerCell +4
        incAngle = 2 * math.pi * (1 / self.columnsPerRow[cell.row])
        startAngle = cell.column * incAngle
        endAngle = startAngle + incAngle
        if self.background is None:
            hue = (1, 1, 1)
        else:
            hue = self.background[1]
        self.ctx.set_source_rgb(*hue)
        radius = (cell.row + cell.myGrid.radiusRow1) * self.pointsPerCell
        if cell.row == 0:
            deltaA = 2/radius
            self.ctx.arc(center, center, radius,
                         startAngle + deltaA, endAngle - deltaA)
            self.ctx.stroke()
        if cell.row == self.rows - 1:
            radius = radius + self.pointsPerCell
            deltaA = 2/radius
            self.ctx.arc(center, center, radius,
                         startAngle + deltaA, endAngle - deltaA)
            self.ctx.stroke()

class mPolarGrid(PolarGrid):
    
    def __init__(self, radiusRow1, rows, columnsRow1):
        self.CellClass = PolarCell
        self.radiusRow1 = radiusRow1
        self.rows = rows
        self.columnsRow1 = columnsRow1
        self.columnsPerRow = []
        self.grid = self.prepareGrid()
        self.distances = None
        self.configureCells()
        self.pointsPerCell = 18
        self.start = []                # cell of path start
        self.goal = []                 # cell of path goal
        self.background = None         # pallet for background
        self.deadends = None           # pallet for maze dead ends
        self.pallets = []

    def drawGrid(self, filename):
        sizeDrawing = 2*(self.radiusRow1 + self.rows) * self.pointsPerCell + 9
        center = (self.radiusRow1 + self.rows) * self.pointsPerCell + 4
        drawFile = filename + ".SVG"
        surface = cairo.SVGSurface(drawFile, sizeDrawing, sizeDrawing)
        self.ctx = cairo.Context(surface)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.stroke()
        if True:
            for row in self.grid:
                for cell in row:
                    c = self.distances.cells.get(cell, 0)
                    p = self.distances.pallet.get(cell, 0)
#                    norm = math.sqrt(4*self.rows**2)
#                    c = int(d * 3 / norm) +2
                    if c > 7:
                        c = 7
#                    if d == 0:
#                        c = 1
                    hues = self.pallets[p]
                    hue = hues[c]
                    irow = cell.row
                    cell.fillCell(self.ctx, self.pointsPerCell, self.rows,
                                  self.columnsPerRow[irow], center, hue)
        for row in self.grid:
            for cell in row:
                irow = cell.row
                cell.drawCell(self.ctx, self.pointsPerCell,
                              self.rows, self.columnsPerRow[irow], center)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_line_width(4)
        self.ctx.set_line_join(cairo.LINE_JOIN_MITER)
        self.ctx.arc(center, center,
                     (self.radiusRow1 + self.rows) * self.pointsPerCell, 0, 2 * math.pi)
        self.ctx.stroke()
        self.ctx.arc(center, center,
                     self.radiusRow1 * self.pointsPerCell, 0, 2 * math.pi)
        self.ctx.stroke()

    def drawOpening(self, cell):
        center = (self.radiusRow1 + self.rows) * self.pointsPerCell +4
        incAngle = 2 * math.pi * (1 / self.columnsPerRow[cell.row])
        startAngle = cell.column * incAngle
        endAngle = startAngle + incAngle
        if self.background is None:
            hue = (1, 1, 1)
        else:
            hue = self.background[1]
        self.ctx.set_source_rgb(*hue)
        radius = (cell.row + cell.myGrid.radiusRow1) * self.pointsPerCell
        if cell.row == 0:
            deltaA = 2/radius
            self.ctx.arc(center, center, radius,
                         startAngle + deltaA, endAngle - deltaA)
            self.ctx.stroke()
        if cell.row == self.rows - 1:
            radius = radius + self.pointsPerCell
            deltaA = 2/radius
            self.ctx.arc(center, center, radius,
                         startAngle + deltaA, endAngle - deltaA)
            self.ctx.stroke()
