import json
import math

class Node():

    """" A class that defines a node and its attributes. """

    def __init__(self, state, parent, description, coord, neighbors, tags, cost):
        self.state = state # State is the name (e.g. "Library")
        self.parent = parent # Previous node
        self.description = description # Description of the place
        self.coord = coord # Coordinates of the node
        self.neighbors = neighbors # Neighbor nodes
        self.tags = tags # tags
        self.cost = cost # Distance between this node and the parent node

class Frontier():

    """ A class that defines the frontier and its associated methods. The frontier is basically
    a list that keeps track of the nodes that haven't been explored yet. Though, the frontier 
    doesn't start with all the nodes in it. Only the neighbors of explored nodes get added to the
    frontier. """

    def __init__(self):
        self.frontier = [] # Create an empty list at the beginning
    
    def add(self, node):
        self.frontier.append(node) # Append a node (used when there are new neighbors)
    
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier) # Check if a node is already in the frontier
    
    def empty(self):
        return len(self.frontier) == 0 # Check if the frontier is empty
    
    def calculate_distance(self, coord_a, coord_b):
        
        # Calculate the distance between 2 points
        distance = math.sqrt((coord_b[0]-coord_a[0])**2 + (coord_b[1]-coord_a[1])**2) 
        return distance

    def remove(self, coord_end):
        
        # Pick the next node to explore and remove it from the frontier
        if self.empty():
            raise Exception("empty frontier")
        else:
            # Uncomment below for depth first search (and comment heuristics method)
            # closest_node = self.frontier[-1]
            # self.frontier = self.frontier[:-1]

            # Compute heuristics (i.e. distance from goal + current path cost)
            min_cost = math.inf
            for node in self.frontier:

                # Calculate the cost for each node and pick the lowest
                cost = node.cost + self.calculate_distance(node.coord, coord_end)
                if cost < min_cost:
                    min_cost = cost
                    closest_node = node
            self.frontier.remove(closest_node)
            return closest_node

class A_Star():

    """ The class that finds the quickest way from a start node to an end node using the core of this class: the solve()
    method. Apart from the format_output() method, which turns the output into human language, all other methods are just helping
    methods. """

    def __init__(self, filename, start, end):

        # Load JSON
        with open(filename, 'r') as f:
            self.campus = json.load(f)

        # Initialize values for the first node (and end node state)
        self.start = start
        self.end = end
        self.starting_description = self.campus[start]["description"]
        self.starting_coords = self.campus[start]["coords"]
        self.starting_neighbors = self.campus[start]["neighbors"]
        self.starting_tags = self.campus[start]["tags"]
    
    def neighbors(self, node):
        
        # Find all the neighbors of a node using the data loaded from the JSON
        result = []
        for i in range(len(node.neighbors)):
            result.append((self.campus[node.neighbors[i]]["description"], node.neighbors[i], self.campus[node.neighbors[i]]["coords"], self.campus[node.neighbors[i]]["neighbors"], self.campus[node.neighbors[i]]["tags"]))
        return result
    
    def calculate_distance(self, coord_a, coord_b):
        
        # Calculate the distance between 2 points
        distance = math.sqrt((coord_b[0]-coord_a[0])**2 + (coord_b[1]-coord_a[1])**2)
        return distance

    def print_solution(self):
        solution = self.solution
        print(solution)

    def solve(self):

        # Initialize frontier with starting point
        start_node = Node(state=self.start, parent=None, description=self.starting_description, coord=self.starting_coords, neighbors=self.starting_neighbors, tags=self.starting_tags, cost=0)
        frontier = Frontier()
        frontier.add(start_node)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looking until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception("no solution")
            
            # Pick a node
            node = frontier.remove(self.campus[self.end]["coords"])

            # If the node is the goal, then solution found
            if node.state == self.end:
                nodes = []

                # Go backwards to collect the full path using the parent argument of each node
                while node.parent is not None:
                    nodes.append(node)
                    node = node.parent
                nodes.append(node) # add start node
                nodes.reverse() # put it in the right order
                self.solution = nodes
                return
            
            # Mark node as explored
            self.explored.add(node.state)

            # Add neighbors to frontier
            for description, state, coord, neighbors, tags in self.neighbors(node):

                # Check that this not is not already in the frontier or hasn't already been explored
                if not frontier.contains_state(state) and state not in self.explored:
                    
                    # Increase cost
                    cost = node.cost + self.calculate_distance(node.coord, coord)

                    # Create node and add it to the frontier
                    child = Node(state=state, parent=node, description=description, coord=coord, neighbors=neighbors, tags=tags, cost=cost)
                    frontier.add(child)

    def calculate_directions(self):

        # Initialize dict
        directions = {}

        # Loop over all groups of 3 consecutive nodes
        for i in range(len(self.solution)-2):

            # Calculate distances between points
            a = self.calculate_distance(self.solution[i].coord, self.solution[i+1].coord)
            b = self.calculate_distance(self.solution[i+1].coord, self.solution[i+2].coord)
            c = self.calculate_distance(self.solution[i+2].coord, self.solution[i].coord)

            # Calculate the angle between a and b
            angle = math.acos((a**2 + b**2 - c**2)/(2*a*b))

            # Check if the next node is ahead
            if angle > (5*math.pi/6):
                direction = "straight"
            
            # If there is a right or left turn
            elif angle > (math.pi/6):
                
                # To determine if it is left or right, move all points so that the first point is at coordinates (0,0)
                a_coord = [self.solution[i].coord[0]-self.solution[i].coord[0], self.solution[i].coord[1]-self.solution[i].coord[1]]
                b_coord = [self.solution[i+1].coord[0]-self.solution[i].coord[0], self.solution[i+1].coord[1]-self.solution[i].coord[1]]
                c_coord = [self.solution[i+2].coord[0]-self.solution[i].coord[0], self.solution[i+2].coord[1]-self.solution[i].coord[1]]
                
                # Now check all possible cases
                # If x coordinate of b is positive: if c_coord is above [AB] -> left, else -> right
                if b_coord[0] > 0:

                    # Calculate the slope of the line that goes from a_coord to b_coord
                    slope = b_coord[1]/b_coord[0]

                    if c_coord[1] > (c_coord[0]*slope):
                        direction = "left"
                    else:
                        direction = "right"
                
                # If x coord of b is negative
                elif b_coord[0] < 0:

                    # Calculate the slope of the line that goes from a_coord to b_coord
                    slope = b_coord[1]/b_coord[0]

                    if c_coord[1] > (c_coord[0]*slope):
                        direction = "right"
                    else:
                        direction = "left"
                
                # If x coord of b = 0
                else:
                    # If y > 0
                    if b_coord[1] > 0:
                        if c_coord[0] > 0:
                            direction = "right"
                        else:
                            direction = "left"
                    # If y < 0
                    else:
                        if c_coord[0] > 0:
                            direction = "left"
                        else:
                            direction = "right"

            else:
                direction = "backwards"
            
            # Add direction to the list
            directions[self.solution[i+1].state] = direction
        
        return directions

    def format_output(self):

        # Initialize instructions
        instructions = []
        
        # Calculate the angles of middle nodes
        directions = self.calculate_directions()

        # Loop over all nodes and compute instructions
        for i in range(len(self.solution)):

            # Start node
            if i == 0:

                # If the starting point is within a building
                if "building" in self.solution[i].tags:
                    instruct = "Start by leaving the building through the main door,"

                    if directions[self.solution[i+1].state] == "right":
                        instructions.append(instruct + " and turn right.")
                    
                    elif directions[self.solution[i+1].state] == "left":
                        instructions.append(instruct + " and turn left.")
                    
                    else:
                        instructions.append(instruct + " and walk straight ahead.")
                
                # If the starting point is outside
                elif "outside" in self.solution[i].tags:
                    instructions.append("Go towards the "+ self.solution[i+1].state + ". " + self.solution[i+1].description + ".")
            
            # Node before the end
            elif i == len(self.solution)-2:

                # if building then it is the wessex house
                if "building" in self.solution[i].tags:

                    # ensure it though
                    if "through building" in self.solution[i].tags:
                        instructions.append("Finally, go through the Wessex House, your destination is right on the other side!")
                
                # if outside
                else:

                    # If crossway
                    if "crossway" in self.solution[i].tags:

                        # If the end point is a building
                        if "building" in self.solution[-1].tags:

                            # If straight
                            if directions[self.solution[i].state] == "straight":
                                instructions.append("Your destination is the building straight ahead, go in!")
                            
                            # if right/left
                            else:
                                instructions.append("Your destination is the building on the "+directions[self.solution[i].state]+", go in!")
                        
                        # If the end point is outside
                        else:

                            # If straight
                            if directions[self.solution[i].state] == "straight":
                                instructions.append("Keep going straight ahead and you will reach your destination!")
                            
                            # if right/left
                            else:
                                instructions.append("At the next crossway, turn on the "+directions[self.solution[i].state]+" and you will reach your destination!")
                    
                    # if not crossway
                    else:

                        # If straight
                        if directions[self.solution[i].state] == "straight":
                            instructions.append("Keep going straight ahead and you will reach your destination!")
                            
                        # if right/left
                        else:
                            instructions.append("Turn on the "+directions[self.solution[i].state]+" so that you on the same walkway, and you will reach your destination!")

                # store instructions
                self.formatted_output = instructions
                return

            # Middle nodes
            else:

                # If previous was building, present node is front door and i = 1, then go to next node (instruction given already in node 0)
                if "front door" in self.solution[i].tags and "building" in self.solution[i-1].tags and i == 1:
                    pass
                
                # If building
                elif "building" in self.solution[i].tags:

                    # If through building
                    if "through building" in self.solution[i].tags:
                        instructions.append("Enter the "+self.solution[i].state+ " and go through it until you're out again.")

                # If outside
                elif "outside" in self.solution[i].tags:

                    # if crossway
                    if "crossway" in self.solution[i].tags:

                        # if frontdoor
                        if "front door" in self.solution[i].tags:

                            # if straight
                            if directions[self.solution[i].state] == "straight":

                                # if next node is not straight as well only
                                if directions[self.solution[i+1].state] != "straight":
                                    for neighbor in self.solution[i].neighbors:
                                        if "building" in self.campus[neighbor]["tags"]:
                                            instructions.append("Walk past the "+neighbor+".")
                                            break
                            
                            # if right or left
                            else:
                                instructions.append("Once you reach the "+self.solution[i].state+", turn "+directions[self.solution[i].state]+" towards the "+self.solution[i+1].state+".")
                        
                        # if not front door and straight
                        elif directions[self.solution[i].state] == "straight":

                            # if next node is not straight as well only
                            if directions[self.solution[i+1].state] != "straight":
                                instructions.append("Keep walking straight until you reach "+self.solution[i+1].state+".")
                        
                        # if not front door and right/left
                        else:
                            instructions.append("Once you reach the "+self.solution[i].state+", turn "+directions[self.solution[i].state]+" towards the "+self.solution[i+1].state+".")
                    
                    # if not crossway
                    else:

                        # if right/left
                        if directions[self.solution[i].state] != "straight":
                            instructions.append("Turn "+directions[self.solution[i].state]+ ", so that you stay on the same walkway.")
                        
                        # if straight
                        else:

                            # if under building
                            if "under building" in self.solution[i].tags:
                                instructions.append("Walk through the archway in front of you.")
                            
                            # If other case
                            else:
                                # ensure next stop isn't straight agin
                                if directions[self.solution[i+1].state] != "straight":
                                    instructions.append("Keep walking straight until you reach "+self.solution[i+1].state+".")

if __name__ == "__main__":

    start = "build_c"
    end = "build_g"
    campus = A_Star("test.json", start, end)
    campus.solve()
    campus.print_solution()
    print(campus.solution)
    for node in campus.solution:
        print(node.state)
    campus.format_output()
    for step in campus.formatted_output:
        print(step)