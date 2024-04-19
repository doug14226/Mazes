
""" Verious algorithms for initializing Mazes """

import random
import json
import re
import operator

from Mazes import Grid, DistanceGrid
from PolarMazes import PolarGrid, mPolarGrid
from randomKruskalMaze import randomKruskalMaze

#maze algorithms
MAZE_ALGORITHMS = dict()
MAZE_ALGORITHMS["AB"] = "Aldous Broder"
MAZE_ALGORITHMS["BT"] = "Binary Tree"
MAZE_ALGORITHMS["HK"] = "Hunt And Kill"
MAZE_ALGORITHMS["RB"] = "Recursive Backtracker"
MAZE_ALGORITHMS["S"] = "Sidewinder"
MAZE_ALGORITHMS["W"] = "Wilson"

MAZE_ALGORITHMS_DESC = []
for a in MAZE_ALGORITHMS.keys():
    MAZE_ALGORITHMS_DESC.append("%s=%s" % (a, MAZE_ALGORITHMS[a]))

"""This routine is keep for processing json file
written by the previous version of mazes"""

def oldInitMazeFromJson(jsonFileName):
    f = open(jsonFileName, "r", encoding="utf-8")
    jsonObj = f.readline()
    thisNode = json.loads(jsonObj)
    className = re.search(r"(\.)(\w+)(\')", thisNode[0]).group(2)
    params = thisNode[1]
    g = globals()
    c = g[className]
    grid = c(*params)
    row = operator.itemgetter(0)
    col = operator.itemgetter(1)
    jsonObj = f.readline()
    while jsonObj:
        thisRecord = json.loads(jsonObj)
        thisObj = thisRecord[0]
        cell = grid.grid[row(thisObj)][col(thisObj)]
        thisNeighbors = thisRecord[1]
        thisExits = thisRecord[2]
        j = len(thisNeighbors)
        for i in range(j):
            if thisNeighbors[i]:
                thisNeighbor = thisNeighbors[i]
                cellNeighbor = grid.grid[row(thisNeighbor)][col(thisNeighbor)]
                cell.nearby[cell.directions[i]] = cellNeighbor
            else:
                cell.nearby[cell.directions[i]] = None
        j = len(thisExits)
        for i in range(j):
            if thisExits[i]:
                thisNeighbor = thisNeighbors[i]
                cellNeighbor = grid.grid[row(thisNeighbor)][col(thisNeighbor)]
                cell.link(cellNeighbor, bidi=False)
        if len(thisRecord) > 3:
            cell.attributes = dict(thisRecord[3])
        jsonObj = f.readline()
    f.close()
    return grid

def initMazeFromJson(jsonFileName):
    f = open(jsonFileName, "r", encoding="utf-8")
    jsonObj = f.readline()
    thisNode = json.loads(jsonObj)
    className = re.search(r"(\.)(\w+)(\')", thisNode[0]).group(2)
    params = thisNode[1]
    g = globals()
    c = g[className]
    grid = c(*params)
    row = operator.itemgetter(0)
    col = operator.itemgetter(1)
    jsonObj = f.readline()
    while jsonObj:
        thisRecord = json.loads(jsonObj)
        thisObj = thisRecord[0]
        cell = grid.grid[row(thisObj)][col(thisObj)]
        thisLinks = thisRecord[1]
        keys = list(thisLinks.keys())
        for i in keys:
            thisNeighbor = thisLinks[i]
            cellNeighbor = grid.grid[row(thisNeighbor)][col(thisNeighbor)]
            cell.link(cellNeighbor, bidi=False)
        if len(thisRecord) > 3:
            cell.attributes = dict(thisRecord[2])
        jsonObj = f.readline()
    f.close()
    return grid


def initMaze(grid, algorithm):
    if algorithm == "AB":
        grid = initAldousBroderMaze(grid)
    if algorithm == "BT":
        grid = initBinaryTreeMaze(grid)
    if algorithm == "RB":
        grid = initRecursiveBacktrackerMaze(grid)
    if algorithm == "S":
        grid = initSidewinderMaze(grid)
    if algorithm == "W":
        grid = initWilsonMaze(grid)
    if algorithm == "HK":
        grid = initHuntAndKillMaze(grid)

    grid.algorithm = MAZE_ALGORITHMS[algorithm]

    return grid

def getRandomMaze(grid):
    algorithm = random.choice(list(MAZE_ALGORITHMS.keys()))
    return initMaze(grid, algorithm)

def initBinaryTreeMaze(grid):
    for cell in grid.eachCell():
        neighbors = []
        if cell.nearby.get('north'):
            neighbors.append(cell.nearby('north'))
        if cell.nearby.get('east'):
            neighbors.append(cell.nearby('east'))
        if len(neighbors) > 0:
            if len(neighbors) == 1:
                ind = 0
            else:
                ind = random.randint(0, len(neighbors)-1)
            neighbor = neighbors[ind]
            if neighbor:
                cell.link(neighbor)
    return grid


def initRecursiveBacktrackerMaze(grid):
    stack = []
    stack.append(grid.randomCell())

    while len(stack) > 0:
        current = stack[-1]
        neighbors = []
        for n in current.neighbors():
            if len(n.getLinks()) == 0:
                neighbors.append(n)

        if len(neighbors) == 0:
            stack.pop()
        else:
            neighbor = random.choice(neighbors)
            current.link(neighbor)
            stack.append(neighbor)

    return grid

def initSidewinderMaze(grid):
    tf = [True, False]
    for row in grid.eachRow():
        run = []
        for cell in row:
            run.append(cell)
            at_eastern_boundary = (cell.nearby.get('east') is None)
            at_northern_boundary = (cell.nearby.get('north') is None)
            #note: ruby: 0  ==  True
            should_close_out = at_eastern_boundary or (at_northern_boundary is False
                                                       and random.choice(tf) is True)
            if should_close_out is True:
                member = random.choice(run)
                if member.nearby.get('north'):
                    member.link(member.nearby('north'))
                run = []
            else:
                cell.link(cell.nearby('east'))
    return grid

def initAldousBroderMaze(grid):
    cell = grid.randomCell()
    unvisited = grid.size()-1
    while unvisited > 0:
        neighbor = random.choice(cell.neighbors())
        if len(neighbor.getLinks()) == 0:#isempty
            cell.link(neighbor)
            unvisited = unvisited-1
        cell = neighbor
    return grid

def initWilsonMaze(grid):
    unvisited = []
    for cell in grid.eachCell():
        unvisited.append(cell)

    first = random.choice(unvisited)
    unvisited.remove(first)

    while len(unvisited) > 0:
        cell = random.choice(unvisited)
        path = [cell]
        while cell in unvisited:
            cell = random.choice(cell.neighbors())
            if cell in path:
                position = path.index(cell)
                #in Ruby code: path = path[0..position]
                #is in Python needs the line below
                path = path[:position+1]
            else:
                path.append(cell)
        #in Ryby: 0.upto(path.length-2)
        #is in Python the line below
        for i in range(len(path)-1):
            path[i].link(path[i+1])
            unvisited.remove(path[i])

    return grid

def initHuntAndKillMaze(grid):
    currentCell = grid.randomCell()

    while currentCell != None:
        unvisitedNeighbors = [n for n in currentCell.neighbors() if len(n.getLinks()) == 0]
        if len(unvisitedNeighbors) > 0:
            neighbor = random.choice(unvisitedNeighbors)
            currentCell.link(neighbor)
            currentCell = neighbor
        else:
            currentCell = None
            for cell in grid.eachCell():
                visitedNeighbors = [n for n in cell.neighbors() if len(n.getLinks()) != 0]
                if len(cell.getLinks()) == 0 and len(visitedNeighbors) != 0:
                    currentCell = cell
                    neighbor = random.choice(visitedNeighbors)
                    currentCell.link(neighbor)
                    break

    return grid


# ===========================================================

def initRecursiveBacktrackerMaze2(grid):
    rbWalkFrom(grid.randomCell())
    return grid

def rbWalkFrom(cell):
    shuffledNeighbors = random.sample(cell.neighbors(), len(cell.neighbors()))
    for neighbor in shuffledNeighbors:
        if len(neighbor.getLinks()) == 0:
            cell.link(neighbor)
            rbWalkFrom(neighbor)

def printGrid(grid):
    print("%s Maze" % grid.algorithm)
    print("Deadends: %d" % len(grid.getDeadEndCells()))
    print(grid)
    print()


