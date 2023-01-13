import math

from common import Coordinates, Map


class Bot:
    def __init__(self):
        self.path = []              # Contains the path to the solution of the level
        self.movements = []         # Contains all the piece movement requeried
        self.level = None           # Save the number of the current level
        self.thinking = True        # Used to check if the path needs to be rebuilt
        self.vertical_pieces = []   # Saves the vertical car pieces in the level
        self.stateCtr = None        # Used inside the control zone
        self.ctr = 0                # Used inside the control zone

    def run(self, state):   

        def thinking_process():

            grid = self.process_grid(self.state_map.grid)   # Get cars orientation
            path = self.search(grid)                        # Solving the level
            movements = self.make_movements(path)           # Making the movements

            return path, movements

        # Control Zone #

        if self.stateCtr != None and self.stateCtr["cursor"] == state["cursor"]:
            self.ctr += 1
        else:                       # Our idea here is that, crazy cars can really be crazy sometimes.
            self.stateCtr = state   # So, to be sure that the cursor never stops while solving all the levels
            self.ctr = 0            # We check if the cursor got "somehow" stuck and we force a new thinking process
        
        if self.ctr > 20:           # If after 2 seconds the cursor is at the same place, we declare it stuck
            self.thinking = True

        # Variables

        new_level = state["level"]
        self.state_map = Map(state["grid"])
        self.grid_size = self.state_map.grid_size

        # Get path and movements

        if self.level != new_level or self.movements == []: 
                                                            # Once we get a state theres only 2 possible early situatio
            self.level = new_level                          # in which we have to solve the level: if it's a new level or
            self.thinking = True                            # if "somehow" there's no movements left to do

        if self.thinking == True:

            self.path, self.movements = thinking_process()  # Solving the level and getting and making the movements
            self.thinking = False

        # Check if everything is going right moving the pieces

        map_coords = [coordinate for coordinate in self.state_map.coordinates if coordinate[2] != "x"] # Current piece coords

        l, dir, coords_d, coords_a = self.movements[0]
        next_move_coords = (coords_d[0], coords_d[1], l) # *Server's standart format*

        if next_move_coords in map_coords:  # The move was done 
            self.movements.pop(0)           # and can be removed from the list
        
        if (self.state_map.grid[coords_d[1]][coords_d[0]] != "o" and    # This is the part we handle crazy cars
            self.state_map.grid[coords_d[1]][coords_d[0]] != l):        # Since our solving algorithm is pretty effective
                                                                        # We decided it's time consuming undoing the crazy car
            self.path, self.movements = thinking_process()              # So it just solves the level again

        # Returning next movement's command ('W','A','S','D')
        
        if self.movements != []:

            return self.next_move(state)


    ###################### Processing Next Move ######################


    def next_move(self, state):

        selected = state["selected"]    # Current cursor's selection
        cursor = Coordinates(state["cursor"][0], state["cursor"][1]) # Current cursor's coordinates
        game_positions = self.state_map.coordinates # Coordinates of each piece

        (letter, direction, depois, antes) = self.movements[0]  # Next movement
        cars_coords = [tuplo for tuplo in game_positions if tuplo[2] == letter] #
    
        if selected != '' and selected != letter:   # If the cursor is selecting a different piece
            return " "                              # it returns space to unselect it

        if selected == letter:  # If the piece is selected
            return direction    # it returns next movement's direction

        if selected == '':  # If the cursor must go to pieces coordinates

            ## We calcule the best way to "grab" the piece

            distA = math.dist([cursor.x, cursor.y], [cars_coords[0][0], cars_coords[0][1]])
            distB = math.dist([cursor.x, cursor.y], [cars_coords[-1][0], cars_coords[-1][1]])

            if distA <= distB:                             ## The cursor will go to the car piece
                x_moves = cursor.x - cars_coords[0][0]     ## closer to itself
                y_moves = cursor.y - cars_coords[0][1]

            else: 
                x_moves = cursor.x - cars_coords[-1][0]
                y_moves = cursor.y - cars_coords[-1][1]

            if x_moves > 0:
                return "a"
            elif x_moves < 0: 
                return "d"
            elif y_moves > 0:
                return "w"
            elif y_moves < 0: 
                return "s"
            else:               ## Once it's at the spot, it returns space to "grab" the piece
                return " "
    


    ###################### Processing Path's Movements ######################


    def make_movements(self, path):

        movements = [] # List saving all the movements to solve the level

        for index in range(len(path)-1):

            # Transforming into server's standart format to use Map.coordinates

            current_grid = "".join(c for c in str(path[index]) if c.isalpha())
            next_grid = "".join(c for c in str(path[index+1]) if c.isalpha())

            current_map_coords = Map("0 " + current_grid + " 0").coordinates
            next_map_coords = Map("0 " + next_grid + " 0").coordinates

            current_coords = [coord for coord in current_map_coords if coord not in next_map_coords]
            next_coords = [coord for coord in next_map_coords if coord not in current_map_coords]

            # Getting the directional command the server uses

            x_change = next_coords[0][0] - current_coords[0][0]
            y_change = next_coords[0][1] - current_coords[0][1]

            if x_change > 0:
                direction = "d"
            elif x_change < 0:
                direction = "a"
            elif y_change > 0:
                direction = "s"
            elif y_change < 0:
                direction = "w" 

            # Saving the movement

            movements.append((  current_coords[0][2],                           # The letter we are moving
                                direction,                                      # Server's direction command
                                (next_coords[0][0], next_coords[0][1]),         # The space the piece is about to fill
                                (current_coords[0][0], current_coords[0][1])    # The space the piece left available after
                                ))

        # In the following code section (next 2 *For* cycles), we fix one of the problems that this project had
        # Since our code doesn't have in count that there's a cursor moving the pieces, we realised that the cursor was moving pieces
        # really far away from each other in two consecutive movements. So having in count that "in order to move a piece we just have
        # to make sure that space is available", we "re-run the movements' list". Doing this actually fast cycles the movements are sorted
        # trying to make consecutive moves at the same piece as much as possible. 
        
        # The movements' list is checked from the beggining until it ends

        for move_i in range(0,len(movements)):

            l, dir, coords_d, coords_a = movements[move_i]

            for new_move_i in range(move_i+1,len(movements)):
                new_l, new_dir, new_coords_d, new_coords_a = movements[new_move_i]

                if l != new_l:
                    continue

                if dir == new_dir:

                    verification = True
                    if new_move_i - move_i - 1 == 0:
                        verification = False

                    for mid_move_i in range(move_i+1, new_move_i):    
                        mid_l, mid_dir, mid_coords_d, mid_coords_a = movements[mid_move_i]

                        if mid_coords_a == new_coords_d:
                            verification = False

                    if verification == True:
                        move = movements[new_move_i]
                        movements.pop(new_move_i)
                        movements.insert(move_i+1,move)
                    break

        # The movements' list is checked from the end to the beginning

        for move_i in range(1,len(movements)+1):

            l, dir, coords_d, coords_a = movements[-move_i]

            for new_move_i in range(move_i+1,len(movements)+1):
                new_l, new_dir, new_coords_d, new_coords_a = movements[-new_move_i]

                if l != new_l:
                    continue

                if dir == new_dir:
                    verification = True
                    if len(movements)-new_move_i+1 - (len(movements)-move_i) == 0:
                        verification = False

                    for mid_move_i in range(len(movements)-new_move_i+1, len(movements)-move_i):    
                        mid_l, mid_dir, mid_coords_d, mid_coords_a = movements[mid_move_i]

                        if mid_coords_d == new_coords_a:
                            verification = False

                    if verification == True:
                        movements.insert(len(movements)-move_i,movements[-new_move_i])
                        movements.pop(-new_move_i-1)
                    break
            
        return movements


    ###################### Solving The Level ######################


    def process_grid(self, grid):

        self.vertical_pieces = []   # List of the vertical cars in the level's board

        for y in range(self.grid_size):

            letterChecked = ['o']   # List of letters already seen
            row  = grid[y]

            for x in range(self.grid_size):

                letter = row[x]

                if letter not in letterChecked:

                    letterChecked.append(letter)

                    # Check if it's a vertical car

                    try:    # Note # try_except is almost never the best approach, however in this case it's pretty effective

                        if grid[y+1][x] == letter and letter not in self.vertical_pieces:
                            self.vertical_pieces.append(letter)
                            
                    except: pass

        return grid

    def search(self, grid):

        def possible_states(board):

            known_letters = set(["o","x"])  # List of letters already searched
            states = []                     # List possible next states

            for row in range(self.grid_size):
                for column in range(self.grid_size):

                    letter = board[row][column] # New letter

                    if letter not in known_letters:
                        known_letters.add(letter)

                        ## Variables

                        if letter in self.vertical_pieces:      # h_minimum - used to search if the car can move left     (horizontally)
                            h_change = 1                        # h_maximum - used to search if the car can move right    (horizontally)
                            v_change = 0                        # h_change  - usefull on horizontal cars
                        else:                                   # v_minimum - used to search if the car can move down     (vertically)
                            h_change = 0                        # v_maximum - used to search if the car can move up       (vertically)
                            v_change = 1                        # v_change  - vertical on horizontal cars

                        h_minimum, h_maximum, v_minimum, v_maximum = row, row, column, column
                        
                        ## Change mininum values trying to move the piece left or down

                        while ( h_minimum - h_change > -1 and 
                                v_minimum - v_change > -1 and 
                                board[h_minimum - h_change][v_minimum - v_change] == letter):

                            h_minimum -= h_change   # Note :
                            v_minimum -= v_change   # Will only update one

                        ## Change maximum values trying to move the piece right or up

                        while ( h_maximum + h_change < self.grid_size and 
                                v_maximum + v_change < self.grid_size and 
                                board[h_maximum + h_change][v_maximum + v_change] == letter):

                            h_maximum += h_change   # Note :
                            v_maximum += v_change   # Will only update one

                        ## Adding left or down movements to the piece

                        if (h_minimum - h_change > -1 and 
                            v_minimum - v_change > -1 and 
                            board[h_minimum - h_change][v_minimum - v_change] == "o"):
                            # Moving
                            next_state = [row[:] for row in board]
                            next_state[h_minimum - h_change][v_minimum - v_change] = letter
                            next_state[h_maximum][v_maximum] = "o"
                            # Stating this movement
                            states.append(next_state)

                        ## Adding right or up movements to the piece

                        if (h_maximum + h_change < self.grid_size and 
                            v_maximum + v_change < self.grid_size and 
                            board[h_maximum + h_change][v_maximum + v_change] == "o"):
                            # Moving
                            next_state = [row[:] for row in board]
                            next_state[h_minimum][v_minimum] = "o"
                            next_state[h_maximum + h_change][v_maximum + v_change] = letter
                            # Stating this movement
                            states.append(next_state)

            return states

        # Variables

        states_queue = [[grid]] # List of the paths searched
        states_history = set()  # Block for repeated states

        # Searching states

        while states_queue:

            path = states_queue.pop(0)  # Current path
            
            # Check if the solution have been found

            if path[-1][self.state_map.piece_coordinates("A")[0].y][-1] == 'A':
                return path

            # Get next possible states from the current path's state

            for state in possible_states(path[-1]):

                state_board = ''.join(''.join(row) for row in state) # Record of the new state, used to check for repeated states

                if state_board not in states_history:

                    states_history.add(state_board)
                    states_queue.append(path + [state])


        return []
