#!/usr/bin/python
# A* 8-Puzzle Solver
# Copyright (c) 2005 Brandon Sterne
# Licensed under the MIT license.
# http://brandon.sternefamily.net/files/mit-license.txt

try:
    import psyco        #Python optimizer
    psyco.full()
except:
    pass
import sys
import heapq as h       #for the priorty queue
import copy as c        #to make deep copies of our data strucutres
import time

###  GLOBALS  ###
# user's choice of heuristic
choice = 0
i = 1
# lookup table for Manhattan distances
# we use nested dictionaries (hash tables) for constant lookup time
# the entry md[i][j] gives us the manhattan distance from square i to j
md = {1:{1:0,2:1,3:2,4:1,5:2,6:3,7:2,8:3,9:4}, \
      2:{1:1,2:0,3:1,4:2,5:1,6:2,7:3,8:2,9:3}, \
      3:{1:2,2:1,3:0,4:3,5:2,6:1,7:4,8:3,9:2}, \
      4:{1:1,2:2,3:3,4:0,5:1,6:2,7:1,8:2,9:3}, \
      5:{1:2,2:1,3:2,4:1,5:0,6:1,7:2,8:1,9:2}, \
      6:{1:3,2:2,3:1,4:2,5:1,6:0,7:3,8:2,9:1}, \
      7:{1:2,2:3,3:4,4:1,5:2,6:3,7:0,8:1,9:2}, \
      8:{1:3,2:2,3:3,4:2,5:1,6:2,7:1,8:0,9:1}, \
      9:{1:4,2:3,3:2,4:3,5:2,6:1,7:2,8:1,9:0} }

# Node class for building our search tree
# each game state that is examined is encapsulated inside a node
class Node:
    # the node contains a board state, the f cost and h cost
    # as well as a pointer to its parent to be used when reconstructing
    # the path from the start node to the goal node
    def __init__(self, contents, cost, hcost = 0):
        self.contents = contents
        self.cost = cost
        self.hcost = hcost
        self.parent = None
    def setParent(self, parent):
        self.parent = parent
    # overload the <= operator so we can maintain sorted order in our queue
    def __le__(self, other):
        return (self.cost+self.hcost) <= (other.cost+other.hcost)

# getKids function takes a node and returns a list of the node's children
# the "moves" argument is a dictionary containing lists of valid moves that
# the blank square can be moved to
def getKids(node, moves):
    global choice           #user's choice of heuristic
    global i
    kids = []
    child = Node(None, 0)   #child node to be put in list of children
    board = node.contents
    pCost = node.cost       #parent cost used to determines child's f cost
    for square in board.keys():
        if board[square] == 0:
            #generate a child node for each of the possible squares that the
            #blank square can be moved to
            for move in moves[square]:
                temp = board.copy()
                temp[square] = board[move]
                temp[move] = board[square]
                if choice is 4:
                    child = Node(temp,i)
                    i = i + 1
                else:
                    child = Node(temp,pCost+1)

                if choice is 1:
                    child.hcost = 0
                elif choice is 2:
                    child.hcost += misplaced(child)
                elif choice is 3:
                    child.hcost += manhattan(child)
                elif choice is 4:
                    child.hcost = 0
                kids.append(child)
    return kids

# goal test for our search
def isGoal(node):
    if (node.contents[1] == 1) and \
       (node.contents[2] == 2) and \
       (node.contents[3] == 3) and \
       (node.contents[4] == 4) and \
       (node.contents[5] == 5) and \
       (node.contents[6] == 6) and \
       (node.contents[7] == 7) and \
       (node.contents[8] == 8):
        return True
    else:
        return False

# reconstructs path backwards from the goal node to the start node
def getPath(end, start):
    current = c.copy(end)
    path = []
    path.append(end)
    while current.contents != start.contents:
        back = current.parent
        path.append(back)
        current = back
    path.reverse()
    return path

# prints the contents of a node in human-readable format
def printNode(node):
    for i in range(1,4):
        print node.contents[i], " ",
    print '\n'
    for i in range(4,7):
        print node.contents[i], " ",
    print '\n'
    for i in range(7,10):
        print node.contents[i], " ",

# Misplaced Tiles heuristic function
# for every square number that doesn't contain the correct tile, add 1 to cost
def misplaced(node):
    distance = 0
    for i in range(1,9):
        if i != node.contents[i]:
            distance += 1
    return distance

# Manhattan Distance heuristic function
def manhattan(node):
    # lookup table for Manhattan Distances
    global md
    distance = 0
    # for every square not containing the blank, add the Manhattan Distance
    # to the cost
    for i in range(1,10):
        if node.contents[i] != 0:
            distance += md[i][node.contents[i]]
    return distance

# main search driver
def aStarSearch(board):
    # create priority queue to store nodes
    pq = []
    h.heapify(pq)

    # dictionary to define valid operators (legal moves)
    moves = {}
    moves[1] = [2,4]
    moves[2] = [1,3,5]
    moves[3] = [2,6]
    moves[4] = [1,5,7]
    moves[5] = [2,4,6,8]
    moves[6] = [3,5,9]
    moves[7] = [4,8]
    moves[8] = [5,7,9]
    moves[9] = [6,8]

    # dictionary to store previously visited nodes
    visited = {}

    # put the initial node on the queue
    global choice
    start = Node(board, 0)
    if choice is 2:
        start.hcost = misplaced(start)
    elif choice is 3:
        start.hcost = manhattan(start)

    # record start time
    time0 = time.time()
    # put the initial node on the queue
    h.heappush(pq, start)
    print "Expanding state:\n"
    printNode(start)
    print "\n\n"

    # keep track of maximum number of nodes in the queue
    maxNodes = 0

    while (len(pq)>0):              # while the queue is non-empty
        # keep track of maximum number of nodes on the queue
        if len(pq) > maxNodes:
            maxNodes = len(pq)

        # remove the first (minimal cost) node from the queue
        node = h.heappop(pq)

        # static cast of the current puzzle state to be used as a hash key
        visNode = tuple(node.contents.items())
        if visNode not in visited:
            #print "The best state to expand with a g(n) =", node.cost, \
            #      "and h(n) =", node.hcost, "is...\n"
            #   printNode(node)

            # goal test
            if isGoal(node):
                return "\n\nGoal!!\n", node, len(visited), maxNodes, \
                       time.time() - time0
            else:
                #print "\tExpanding this node...\n"
                # if not the goal, generate a list of children and put them on
                # the queue
                kids = getKids(node, moves)
                for child in kids:
                    child.setParent(node)
                    h.heappush(pq, child)
                    visited[visNode] = True

    # if the queue is ever empty, no solution exists
    return "Sorry Charlie.  No solution.", start, len(visited), maxNodes, \
           time.time() - time0

def printHelp():
    print "-p\tPath: reconstruct full path to goal"
    sys.exit()

def main():
    for arg in sys.argv:
        if arg in ("-h","--help"):
            printHelp()

    global choice

    print "Welcome to Brandon Sterne's 8-Puzzle solver."
    try:
        puz = int(raw_input('Type "1" to use a default puzzle' + \
                            ' or "2" to enter your own puzzle: '))
    except:
        print "Invalid option. Goodbye."
        sys.exit()

    if puz < 1 or puz > 2:
        print "Invalid option:", puz
        sys.exit()

    # use default board
    if puz == 1:
        # default board contents
        board = {}

        #difficult
        #board[1] = 4
        #board[2] = 0
        #board[3] = 7
        #board[4] = 6
        #board[5] = 1
        #board[6] = 8
        #board[7] = 2
        #board[8] = 5
        #board[9] = 3

        #middle
        #board[1] = 4
        #board[2] = 0
        #board[3] = 1
        #board[4] = 5
        #board[5] = 8
        #board[6] = 2
        #board[7] = 7
        #board[8] = 6
        #board[9] = 3

        #easy
        board[1] = 1
        board[2] = 2
        board[3] = 3
        board[4] = 4
        board[5] = 0
        board[6] = 5
        board[7] = 7
        board[8] = 8
        board[9] = 6

    # user-defined board
    else:
        print "\tEnter your puzzle.  Use a zero to represent the blank."
        row1 = raw_input("\tEnter the first row.  Use space or tab" +
                         " between numbers:  ")
        row2 = raw_input("\tEnter the second row.  Use space or tab" +
                         " between numbers: ")
        row3 = raw_input("\tEnter the third row.  Use space or tab" +
                         " between numbers:  ")
        board = {}
        board[1] = int(row1[0])
        board[2] = int(row1[2])
        board[3] = int(row1[4])
        board[4] = int(row2[0])
        board[5] = int(row2[2])
        board[6] = int(row2[4])
        board[7] = int(row3[0])
        board[8] = int(row3[2])
        board[9] = int(row3[4])

    print "\tEnter you choice of algorithm"
    print "\t    1. Uniform Cost Search"
    print "\t    2. A* with Misplaced Tiles heuristic"
    print "\t    3. A* with Manhattan Distance heuristic"
    print "\t    4. DFS"
    try:
        choice = int(raw_input("\t    Choice: "))
    except:
        print "Invalid choice.  Goodbye."
        sys.exit()
    if choice < 1 or choice >4:
        print "Invalid choice. Goodbye."
        sys.exit()

    result, goal, visNodes, maxNodes, time = aStarSearch(board)
    print result
    print "To solve this problem the search algorithm expanded a total of", \
          visNodes, "nodes."
    print "The maximum number of nodes in the queue at any one time was", \
          maxNodes, "."
    print "The depth of the goal node was", goal.cost, "."
    print "The search took", time, "seconds."

    # if the user wants, print only the nodes on the solution path
    for arg in sys.argv:
        if arg in ("-p","-P"):
            raw_input("\nPress enter when you are ready to print path...")
            start = Node(board, 0)
            path = getPath(goal, start)
            print "\n\nPrinting Path:\n"
            for i in range(0, len(path)):
                print "Move",i
                printNode(path[i])
                print "\n\n"


if __name__ == "__main__":
    main()