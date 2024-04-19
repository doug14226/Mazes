#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
" main routine for woven maze yellowHorizon"

import sys
from mazeColoring import mazeColoring, interpolatePallet
from randomKruskalMaze import randomKruskalMaze
from palettable.colorbrewer.sequential import YlOrRd_9

def main():
    nameForFiles = "yellowHorizon4"
    if len(sys.argv) > 1:
        nameForFiles = sys.argv[1]
    print(nameForFiles)
    rows, columns = 44, 56
    grid = randomKruskalMaze(rows, columns)
    grid.manyRandomPassages()
    grid.build()
    startRow = 14
    startColumn = 0
    grid.start = grid.getCell(startRow, startColumn)
    goalRow = 14
    goalColumn = columns-1
    grid.goal = grid.getCell(goalRow, goalColumn)
    grid.distances = grid.getDistancesFromPath(grid.start, grid.goal)
    p = interpolatePallet(YlOrRd_9.mpl_colors, grid.distances)
    grid.coloring = mazeColoring(grid, p)
    printFile = nameForFiles + ".utf8"
    fhp = open(printFile, "w", encoding="utf8")
    print("Kuschal Maze:", file=fhp)
    print("Start: ", grid.start.toString(), file=fhp)
    print("Goal: ", grid.goal.toString(), file=fhp)
    print(grid, file=fhp)
    jsonfile = nameForFiles + ".json"
    fhj = open(jsonfile, "w", encoding="utf8")
    grid.dumpGrid(fhj)
    grid.insetDrawGrid(nameForFiles)
main()
