


class Distances:

    def __init__(self, rootCell, rootPallet=0):
        self.rootCell = rootCell
        self.cells = dict()
        self.pallet = dict()
        self.cells[self.rootCell] = 0
        self.pallet[self.rootCell] = rootPallet

    def __sub__(self, other):
        difference = Distances(self.rootCell)
        selfCells = self.getCells()
        if isinstance(other, int):
            for c in selfCells:
                this = self.getDistanceTo(c)
                thisPallet = self.getPallet(c)
                difference.setDistanceTo(c, (this - other))
                difference.setPallet(c, thisPallet)
        else:
            for c in selfCells:
                this = self.getDistanceTo(c)
                that = other.getDistanceTo(c)
                thisPallet = self.getPallet(c)
                difference.setDistanceTo(c, (this - that))
                difference.setPallet(c, thisPallet)
        return difference

    def max(self):
        selfCells = self.getCells()
        that = 0
        for c in selfCells:
                this = self.getDistanceTo(c)
                if this > that:
                    that = this
        return that

    def __add__(self, other):
        addition = Distances(self.rootCell)
        selfCells = self.getCells()
        if isinstance(other, int):
            for c in selfCells:
                this = self.getDistanceTo(c)
                thisPallet = self.getPallet(c)
                addition.setDistanceTo(c, (this + other))
                addition.setPallet(c, thisPallet)
        else:
            for c in selfCells:
                this = self.getDistanceTo(c)
                that = other.getDistanceTo(c)
                thisPallet = self.getPallet(c)
                addition.setDistanceTo(c, (this + that))
                addition.setPallet(c, thisPallet)
        return addition

    def minP(self, other):
        minDistance = Distances(self.rootCell)
        selfCells = self.getCells()
        for c in selfCells:
            this = self.getDistanceTo(c)
            that = other.getDistanceTo(c)
            thisPallet = self.getPallet(c)
            thatPallet = other.getPallet(c)
            if that > this:
                minDistance.setDistanceTo(c, this)
                minDistance.setPallet(c, thisPallet)
            elif that < this:
                minDistance.setDistanceTo(c, that)
                minDistance.setPallet(c, thatPallet)
            elif (that == this) and ((thatPallet - thisPallet) == 1):
                minDistance.setDistanceTo(c, that)
                minDistance.setPallet(c, thatPallet)
            elif (that == this) and not ((thatPallet - thisPallet) == 1):
                minDistance.setDistanceTo(c, this)
                minDistance.setPallet(c, thisPallet)
        return minDistance

    def getDistanceTo(self, cell):
        return self.cells.get(cell, None)

    def setDistanceTo(self, cell, distance):
        self.cells[cell] = distance

    def getPallet(self, cell):
        return self.pallet.get(cell, None)

    def setPallet(self, cell, thisPallet):
        self.pallet[cell] = thisPallet

    def getCells(self):
        return self.cells.keys()

    def isPartOfPath(self, cell):
        #return self.cells.has_key(cell)
        return cell in self.cells

    def __len__(self):
        return len(self.cells.keys())

    def pathTo(self, goal):
        current = goal
        breadcrumbs = Distances(self.rootCell)
        breadcrumbs.setDistanceTo(current, self.cells[current])

        while current is not self.rootCell:
            for neighbor in current.getLinks():
                if self.cells[neighbor] < self.cells[current]:
                    breadcrumbs.setDistanceTo(neighbor, self.cells[neighbor])
                    current = neighbor
                    break
        return breadcrumbs
