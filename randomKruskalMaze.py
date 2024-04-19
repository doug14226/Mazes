"""
Randomized Kruskal's Minimum Spanning Tree Algorithm for Maze Generation.
Original by heyhuyen, Downloaded from Github, and highly
modified to fit my classes.  Copyright (c) 2017 Douglas Lange
"""

from random import shuffle, randrange, randint
from Mazes import DistanceGrid, Cell, Distances

class kruskalCell(Cell):

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
                        delta = max(abs(cell.row - linked.row), abs(cell.column - linked.column))
                        distances.setDistanceTo(linked, dist+delta)
                        distances.setPallet(linked, pallet)
                        newFrontier.append(linked)
            frontier = newFrontier
        return distances


class randomKruskalMaze(DistanceGrid):
    def __init__(self, rows, columns, cellClass=Cell):
        super().__init__(rows, columns, cellClass=Cell)   #may need Kruskal Cell class
        self.sets = []
        self.walls = []
        self.setup_sets_and_walls()

    def setup_sets_and_walls(self):
        for cell in self.eachCell():
            self.sets.append(set([cell]))
            if cell.nearby.get('south'):
                self.walls.append([cell, cell.nearby.get('south')])
            if cell.nearby.get('west'):
                self.walls.append([cell, cell.nearby.get('west')])

    def manyRandomPassages(self):
        many = (self.rows-2)*(self.columns-2)
        for i in range(0, many):
            self.addRandomPassage()

    def __RandomPassage(self,Start,End,XStart,XEnd,Here,Start_set,End_set,
                        XStart_set,XEnd_set,Attribute,direction,Rdirection):
        Start.nearby[direction] = End
        End.nearby[Rdirection] = Start
        Here.nearby[direction] = None
        Here.nearby[Rdirection] = None
        Start.link(End)  #Tunnel
        XEnd.link(Here)
        Here.link(XStart)
        Here.attributes[Attribute] = True
        self.walls.remove([Start, Here])
        self.walls.remove([Here, End])
        self.sets.append(Start_set.union(End_set))
        self.sets.append(XStart_set.union(XEnd_set.union(set([Here]))))
    
    def addRandomPassage(self):
        r = randrange(2, self.rows-1)
        c = randrange(2, self.columns-1)
        Here = self.grid[r][c]
        Used = len(Here.links)
        if not Used:
            North = self.grid[r-1][c]
            East = self.grid[r][c+1]
            South = self.grid[r+1][c]
            West = self.grid[r][c-1]
            for s in self.sets:
                if North in s:
                    N_set = s
                if East in s:
                    E_set = s
                if South in s:
                    S_set = s
                if West in s:
                    W_set = s
            if N_set.isdisjoint(S_set) and W_set.isdisjoint(E_set):
                self.sets.remove(N_set)
                self.sets.remove(S_set)
                self.sets.remove(E_set)
                self.sets.remove(W_set)
                self.sets.remove(set([Here]))
                if randint(0, 1):
                    self.__RandomPassage(North,South,East,West,Here,N_set,S_set,
                                         E_set,W_set,"NSpassage",'south','north')
                else:
                    self.__RandomPassage(East,West,North,South,Here,E_set,W_set,
                                         N_set,S_set,"EWpassage",'west','east')
 

    def build(self):
        wall_indices = [i for i in range(len(self.walls))]
        shuffle(wall_indices)
        for index in wall_indices:
            wall = self.walls[index]
            cell1 = wall[0]
            cell2 = wall[1]
            for s in self.sets:              
                if cell1 in s:
                    a_set = s               
                if cell2 in s:
                    b_set = s
            if a_set.isdisjoint(b_set):
                cell1.link(cell2)
                self.sets.append(a_set.union(b_set))
                self.sets.remove(a_set)
                self.sets.remove(b_set)



