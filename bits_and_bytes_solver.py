# -*- coding: utf-8 -*-

from os.path import isfile
import json
from collections import deque
from random import shuffle
import click
import time
from copy import copy as cp
import os

progress_counter = 0
recursion_counter = 0


# Create the puzzle game as a class
class Board:
    # Initialize an object of the class
    def __init__(self, filepath, use_random):
        # Import the puzzle parts form the separate json list.
        self.all_parts = self.importPuzzlePartData(filepath, use_random)
        # Define an empty set of already used parts. Using a set would be more efficient, but this would referse the shuffle of the list since a set is sorted.
        # Since the list is a maximum of 16 elements, this is still performat enough
        self.parts_used = []
        # Define a set of all parts since non is used yet.
        self.parts_left = list(self.all_parts)
        # Define a 4x4 Matrix for represantation of the board. 0 represents an empty field.
        self.field = [[0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0]]

# Reset the Board
    def resetBoard(self):
        self.parts_used = []
        self.parts_left = list(self.all_parts)
        self.field = [[0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0]]

    def importPuzzlePartData(self, filepath, use_random):
        puzzledata = {}
        # Check if the file exists!
        if isfile(filepath):
            with open(filepath, "r") as f:
                # Read the json content into a dictionary
                try:
                    puzzledata = json.load(f)
                except Exception as e:
                    print("!!! Error: The file {} cannot be imported! Is it a valid json file? => Exit here\n\t {}".format(
                        filepath, e))
                    exit()

            # Shuffle the order of parts if requested
            tmp_part_number_list = list(puzzledata)
            if use_random:
                shuffle(tmp_part_number_list)

            # Create a puzzle-part object for each part using the values form the imported json file
            # Store those objects in a dictionary using the 8bit value as a key
            all_parts = {}
            for part_number in tmp_part_number_list:
                all_parts[part_number] = PuzzlePart(
                    part_number, 
                    puzzledata[part_number]["rotation"],
                    puzzledata[part_number]["pins"],
                    puzzledata[part_number]["canEdge"]
                )

            return all_parts
        else:
            print("!!! Error: Filepath does not exist! => Exit here\nFilepath given: {}".format(
                filepath))
            exit()

    # Function for identifing the next empty field on the board. It will iterate through the 4x4 matrix and return the next field with an 0 found.
    def getEmptyField(self):
        for x in range(0, 4):
            for y in range(0, 4):
                if self.field[x][y] == 0:
                    # x = row ; y = col
                    return (x, y)
        return False

    def deployPart(self, part, position):
        row, col = position
        # set the field
        self.field[row][col] = part

        # remove part from the parts left set and add it to the used parts set
        self.parts_used.append(part.number)
        self.parts_left.remove(part.number)
        return True

    # Function to remove a part from the playing field
    def setFieldNull(self, position):
        row, col = position
        if self.field[row][col] != 0:
            part = self.field[row][col]
            self.parts_used.remove(part.number)
            self.parts_left.append(part.number)
            self.field[row][col] = 0
            return True
        else:
            return False

    # Function to print the current status of the palying field
    def printField(self, decimal=False):
        board = ""
        for row in self.field:
            for part in row:
                if part == 0:
                    board += "----------, "
                else:
                    if decimal:
                        board += "{} {}, ".format(part.orientation, int(part.number,2))
                    else:
                        board += "{} {}, ".format(part.orientation, part.number)
            board += "\n"
        print(board)

    def checkNeighbours(self, part, position):
        # check corner cases
        if position == (0, 0) and part.canEdge:
            # Top Left
            # If the puzzle part has a 1 at position 1 or 7 it does not fit in the top left corner.
            if part.orientedPins[1] == 1 or part.orientedPins[7] == 1:
                # This does not work here!
                return False
        elif position == (0, 3) and part.canEdge:
            # Top Right
            # If the puzzle part has a 1 at position 1 or 3 it does not fit in the top right corner.
            if part.orientedPins[1] == 1 or part.orientedPins[3] == 1:
                # This does not work here!
                return False
        elif position == (3, 3):
            # Bottom Right
            # If the puzzle part has a 1 at position 3 or 5 it does not fit in the bottom right corner.
            if part.orientedPins[3] == 1 or part.orientedPins[5] == 1:
                # This does not work here!
                return False
        elif position == (3, 0):
            # Bottom Left
            # If the puzzle part has a 1 at position 5 or 7 it does not fit in the bottom left corner.
            if part.orientedPins[5] == 1 or part.orientedPins[7] == 1:
                # This does not work here!
                return False

        # check neighbour fields next
        # translate position to row and col to improve readability of this code.
        row, col = position
        # Get the pins of the current part to test
        test_part_pins = part.orientedPins
        # Above
        # Check if there is a part above the current part and if yes, validate if this would fit here.
        if (row-1) in range(0, 4):
            part_above = self.field[row-1][col]
            if part_above != 0:
                # Get pins of the part above
                part_above_pins = part_above.orientedPins
                # The part does not fit if pin position 0 and 5 or 1 and 4 are not equal 1!
                if (test_part_pins[0] + part_above_pins[5]) != 1 or (test_part_pins[1] + part_above_pins[4]) != 1:
                    # This does not match here!
                    return False

        # Right side
        # Check if there is a part on the right side of the current test part. If yes, validate if this would fit here.
        if (col+1) in range(0, 4):
            part_right = self.field[row][col+1]
            if part_right != 0:
                part_right_pins = part_right.orientedPins
                if (test_part_pins[2] + part_right_pins[7]) != 1 or (test_part_pins[3] + part_right_pins[6]) != 1:
                    # This does not match here!
                    return False

        # Below
        # Check if there is a part below of the current test part. If yes, validate if this would fit here.
        if (row+1) in range(0, 4):
            part_below = self.field[row+1][col]
            if part_below != 0:
                part_below_pins = part_below.orientedPins
                if (test_part_pins[4] + part_below_pins[1]) != 1 or (test_part_pins[5] + part_below_pins[0]) != 1:
                    # This does not match here!
                    return False

        # Left side
        # Check if there is a part on the left side of the current test part. If yes, validate if this would fit here.
        if (col-1) in range(0, 4):
            part_left = self.field[row][col-1]
            if part_left != 0:
                part_left_pins = part_left.orientedPins
                if (test_part_pins[7] + part_left_pins[2]) != 1 or (test_part_pins[6] + part_left_pins[3]) != 1:
                    # This does not match here!
                    return False

        # Looks like this is a fit here!
        return True

    def validatePart(self, part, position):
        row, col = position
        # check if part is still available:
        if part.number in self.parts_used:
            return False

        # ceck if position is free:
        if self.field[row][col] != 0:
            return False

        # check neighbours and corner cases next
        if self.checkNeighbours(part, position):
            # This part does fit here! Awesome :)
            return True
        else:
            # Nope this part does not fit here. Try next one :(
            return False


class PuzzlePart:
    def __init__(self, n, o, p, e):
        self.number = str(n)
        self.orientation = o
        self.pins = deque(p)
        self.orientedPins = deque(p)
        self.canEdge = e

    def getData(self):
        print("\tNumber:\t\t{}\n\
        Orientation:\t{}\n\
        Pins:\t\t{}\n".format(self.number, self.orientation, list(self.orientedPins)))

    def changeOrientation(self, newOrientation):
        if newOrientation == self.orientation:
            return True
        elif newOrientation == "T":
            self.orientedPins = self.pins.copy()
            self.orientation = "T"
            return self.orientedPins
        elif newOrientation == "R":
            self.orientedPins = self.pins.copy()
            self.orientedPins.rotate(-2)
            self.orientation = "R"
            return self.orientedPins
        elif newOrientation == "B":
            self.orientedPins = self.pins.copy()
            self.orientedPins.rotate(-4)
            self.orientation = "B"
            return self.orientedPins
        elif newOrientation == "L":
            self.orientedPins = self.pins.copy()
            self.orientedPins.rotate(-6)
            self.orientation = "L"
            return self.orientedPins
        else:
            return False


def solve_backtracking(theBoard, superrandom, progress):
    # Count the number of times this function was called in the recursion
    global recursion_counter
    recursion_counter += 1

    # Manage the progress / update counter. Display the current status of the board each time the counter hits the number provided as progress.
    # Skip the status update if progress is 0.
    if progress > 0:
        global progress_counter
        if progress_counter == progress:
            progress_counter = 0
            theBoard.printField()
        progress_counter += 1

    # Get the next empty field on the board to continue
    next_empty_field = theBoard.getEmptyField()

    # If the search for the next empty field return False, the board is solved!
    if not next_empty_field:
        return theBoard

    # TODO: Implement the superrandom feature! This will require a rewrite the loop (switch to while) because shuffeling the parts will change the list during the loop.

    # Iterate all left parts to find the next one.
    for part_number in theBoard.parts_left:
        # Get the corresponding part object
        part = theBoard.all_parts[part_number]
        # Maybe not necessary but better safe than sorry: Verify if the part is already used. If yes, skip this part.
        if part.number in theBoard.parts_used:
            print("... DEBUG-parts-used triggered ...")
            continue
        # If superrandom is active, shuffle the list of orientations for this iteration.
        # available_orientations = ["T", "R", "B", "L"]
        available_orientations = ["T", "R", "B", "L"]
        if superrandom:
            shuffle(available_orientations)
        # Iterate all orientations of the puzzle part and check if it fits the empty field
        for orientation in available_orientations:
            # Adjust the part to the requested orientation
            part.changeOrientation(orientation)
            # Check if the part matches the empty field
            if theBoard.validatePart(part, next_empty_field):
                # puzzle part matches! => add it here
                theBoard.deployPart(part, next_empty_field)
                #  Test the next field recursively
                if solve_backtracking(theBoard, superrandom, progress):
                    return theBoard
                # This seems to be a dead end. Remove this part again.
                theBoard.setFieldNull(next_empty_field)
    return False


# As an alternative to the backtracking aproach this function implements a stochastical bruteforce aproach to solve the puzzle
# Start the bf loop
# Shuffle the pieces randomly
# Try to solve the Puzzle
# Start the loop randomly shuffled pieces
# Try the first position in random orientation "x"
# If true try the next
# If false go back to step nr 1



def bruteforce_solver(theBoard, progress, runtime):
    # TODO: Build offline cache!
    # TODO: Change the offline cache to save working combinations
    board_solved = False
    lookupPosition = {0:(0,0), 1:(0,1), 2:(0,2), 3:(0,3), 4:(1,0), 5:(1,1), 6:(1,2), 7:(1,3), 8:(2,0), 9:(2,1), 10:(2,2), 11:(2,3), 12:(3,0), 13:(3,1), 14:(3,2), 15:(3,3)}
    # available_orientations = ["T", "R", "B", "L"] 
    available_orientations = ["T", "R", "B", "L"] 
    progress_counter = 0
    timeout = time.time()+(runtime*60)
    best_board = 0
    best_parts_number = 0
    total_counter = 0

    while not board_solved:
        
        if runtime > 0:
            if time.time() > timeout:
                break 

        # Clean the board partsused, partsleft, field
        theBoard.resetBoard()
        # Shuffle the pieces randomly
        shuffle(theBoard.parts_left)

        # Try first postition
        parts_left_copy = theBoard.parts_left.copy()
        check = True
        for index, part_number in enumerate(parts_left_copy):
            part = theBoard.all_parts[part_number]
            shuffle(available_orientations)
            part.changeOrientation(available_orientations[0])
            if theBoard.validatePart(part, lookupPosition[index]):
                theBoard.deployPart(part, lookupPosition[index])
            else:
                check = False
                break
        
        parts_list = theBoard.field[0]+theBoard.field[1]+theBoard.field[2]+theBoard.field[3] 
        #print("DEBUG: parts_list = {}".format(parts_list))       
        parts_used = (16 - parts_list.count(0))
        #print("DEBUG: parts_unused = {}".format(parts_unused))
        #input("next?") 

        if parts_used > best_parts_number:
            best_board = cp(theBoard)
            best_parts_number = parts_used
            print("\n###")
            print("New best board found after {} tries: ".format(total_counter))
            print("Max parts used: {}".format(best_parts_number))
            best_board.printField()

        if progress > 0:
            if progress_counter == progress:
                progress_counter = 0
                print("Time left: {:.2f} min / # {}".format((timeout-time.time())/60, total_counter))
            progress_counter += 1
            total_counter += 1

        if check:
            board_solved = True

    return best_board, total_counter



# Get the necessary information from the commandline. If the filepath is not provided via cli, the program will ask the user!
@click.command()
@click.option("-r", "--random", type=bool, is_flag=True, help="Use the -r flag if you want to shuffle the list after the import.")
@click.option("-sr", "--superrandom", type=bool, is_flag=True, help="Use the -sr flag: Superrandom will shuffle the list of left parts and the orientation each iteration in the backtracking algorithm. (This does not affect the bruteforce aproach!)")
@click.option("-f", "--filepath", prompt="Please provide a filepath to the parts.json file: ", type=click.Path(exists=True), help="Provide the file path to your json file containing all parts of the game.")
@click.option("-m", "--mode", type=click.Choice(['bf', 'bt'], case_sensitive=False), prompt="Choose a mode [bt|bf]: ", help="Choose a mode for solving the puzzle. bt = backtracking | bf = bruteforce")
@click.option("-p", "--progress", default=10000, type=int, help="Choose a value between 0 and X>0. Each X iterations the programm will give a short status update. Setting the value to 0 will disable the status update! [default=10000]")
@click.option("-rt", "--runtime", default=1, type=float, help="Choose a max runtime in minutes. Reached the max runtime the programm will stop. Setting the value to 0 will disable the max time! [default=1]")
def main(random, superrandom, filepath, mode, progress, runtime):
    # Initializing the game by creating a new object of the board.
    theBoard = Board(filepath, random)

    print("--- Start ---")
    # Call the function depending of the selected mode
    if mode == "bt":
        # start solving the puzzle using the backtracking function
        theFinalBoard = solve_backtracking(theBoard, superrandom, progress)
        print("Number of times recursive solve function called: {}".format(recursion_counter))
        print("--- Finished ---")
        print("\n--- Solution ---")
        if theFinalBoard:
            theFinalBoard.printField()
            theFinalBoard.printField(decimal=True)
        else:
            print("No solution found!")

    elif mode == "bf":
        best_board, total_counter = bruteforce_solver(theBoard, progress, runtime)
        print("--- Finished ---")
        print("\n--- Best solution ---")
        print("Total count: {}".format(total_counter))
        best_board.printField()
        best_board.printField(decimal=True)
        
    else:
        print("!!! Error: This mode is not supported. => Exit here\n\tMode provided: {}".format(mode))
        exit()


if __name__ == "__main__":
    main()
