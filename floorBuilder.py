import math
from numpy import random
import pymunk
from multimethod import multimethod
import pygame
import pymunk.pygame_util
import time
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

"""
Each cell is a size of 5 ft,
1's signifying a room, 0.5 signifying a corridor, 0's signifying a wall, and -1's signifying the boss room
"""
class FloorBuilder():
    def __init__(self):
        """
        Class constructor.
        """
        self.built_floor = []
        self._space = pymunk.Space()
        self._space.gravity = 0, 0 # To allow for body objects to float in space
        self.pre_physics_rooms = []
        self._bodies = []  # The actual bodies
        self._bodies_shape = []  # The Poly / shape of the object
        self._bodies_x_y = []

        # Room selection process
        self._bodies_area = []  # Area of each body to help with fitness and room selection
        self._bodies_fitness = []  # Fitness equation for uniformly selecting best rooms at random
        self._rooms_to_select = 0  # How many rooms the dungeon has
        self._fitness_multiplier = 2  # How askew to area of body / selection of rooms
        self._rooms_selected = []  # Which rooms were selected to exist
        self._traproom_probability = 0.01


        # Physics Engine Time info
        # Time Step
        self._dt = 1.0 / 60.0
        # Number of physics steps per screen frame
        self._physics_steps_per_frame = 30


        # pygame viewing info
        self._dungeon_size = [100, 100]
        self._screen_width = self._dungeon_size[0]
        self._screen_height = self._dungeon_size[1]
        pygame.init()
        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))
        self._clock = pygame.time.Clock()

        self._draw_options = pymunk.pygame_util.DrawOptions(self._screen)


    @multimethod
    def buildFloor(self, size_string : str, type : str):
        """
        Builds a floor with a size type and returns a built floor
        :param size_string: The size of the dungeon as a string (tiny, small, medium, large, chonky)
        :param type: what type of dungeon is it? This comes into play with the generation of the shape the rooms are
        generated in
        :return: A built floor as a 2D list of a list containing an int of if the cell is occupied or not
        1's signifying a room, 0.5 signifying a corridor, 0's signifying a wall, and -1's signifying the boss room
        """
        built_floor = []
        return built_floor

    def buildFloor(self, cell_max : int, room_size  : int):
        """
        Builds a floor with a size type and returns a built floor
        :param cell_max: The size of the dungeon to make a cell_max by cell_max size
        :param room_size: The avg size of a room in cells
        :return: A built floor as a 2D list of a list containing an int of if the cell is occupied or not
        1's signifying a room, 0.5 signifying a corridor, 0's signifying a wall, and -1's signifying the boss room
        """
        built_floor = []
        return built_floor

    def buildFloor(self):
        """
        The base floor builder, builds a medium dungeon with the avg 4x4 square size room
        :return: A built floor
        """
        self.baseCircleBuild(70,5)
        self.generateBossRoom(7,1.2)
        self._rooms_to_select = 5 # Excludes the boss room, which should be the last added
        self.expansionSelectionSim()
        self.delaunayTriangulation()
        return [] # Returns array of map

    def baseCircleBuild(self,numRooms, circleRadius):
        """
        :param numRooms: Number of rooms I want to generate within the circle
        :param circleRadius: How big of a circle is generated, how tightly is it originally packed?
        :return: The physics generated room locked in place that was simulated in a basic circle
        """
        rooms = []
        for i in range(numRooms):
            rand_size_x = int(random.normal(loc = 4, scale = 2.5))
            if rand_size_x < 2:
                rand_size_x = 2
            rand_size_y = int(random.normal(loc = rand_size_x, scale = 2.5))
            if rand_size_y < 2:
                rand_size_y = 2
            rand_theta = 2 * math.pi * random.random()
            rand_rad = circleRadius * random.random()
            pos_x = math.cos(rand_theta) * rand_rad + self._screen_width / 2
            pos_y = math.sin(rand_theta) * rand_rad + self._screen_height / 2
            rooms.append([rand_size_x,rand_size_y,pos_x,pos_y])
        self.pre_physics_rooms = rooms

    def generateBossRoom(self,max_size,circleRadius):
        """
        :param max_size: Maximum size of the boss room
        :param circleRadius: How far out / close in to the center of the dungeon I want the boss room to be
        :return: Returns nada
        """
        rand_size_x = int(random.normal(loc=max_size, scale=2.5))
        if rand_size_x < 2:
            rand_size_x = 2
        rand_size_y = int(random.normal(loc=rand_size_x, scale=2.5))
        if rand_size_y < 2:
            rand_size_y = 2
        rand_theta = 2 * math.pi * random.random()
        rand_rad = circleRadius * random.random()
        pos_x = math.cos(rand_theta) * rand_rad + self._screen_width / 2
        pos_y = math.sin(rand_theta) * rand_rad + self._screen_height / 2
        self.pre_physics_rooms.append([rand_size_x, rand_size_y, pos_x, pos_y])



    def expansionSelectionSim(self):
        """
        Uses the pre_physics_rooms of the program to expand and select the rooms of the dungeon
        Runs the physics simulator to expand the rooms, selects the largest rooms, then snaps all rooms to nearest grid

        :return: The fully generated map
        """
        # Room and physics space creation
        rooms_simulated = []
        for room in self.pre_physics_rooms:
            curr_room = pymunk.Body()
            curr_room.position = room[2], room[3]
            vertices = [(-room[0] / 2, -room[1] / 2), (room[0] / 2, -room[1] / 2), (-room[0] / 2, room[1] / 2), (room[0] / 2, room[1] / 2)]
            physics_box = pymunk.Poly(curr_room, vertices)
            physics_box.mass = (room[0] ** 2 + room[1] ** 2) ** (1/2) # To let the bigger boxes push things easier, but not too much
            self._space.add(curr_room,physics_box) # Adds the object to the physics space
            self._bodies.append(curr_room)
            self._bodies_shape.append(physics_box)
            self._bodies_area.append(room[0]*room[1])
            self._bodies_x_y.append([room[0], room[1]])
            rooms_simulated.append([pymunk.body, physics_box])

        # Runs the simulation til the stuff stops
        self.showDungeonGeneration(1)

        # Selection and Removal of rooms
        fitness = [body ** self._fitness_multiplier for body in self._bodies_area[0:-2]]
        fit_sum = sum(fitness)
        prev_fit = 0
        for body in fitness:
            self._bodies_fitness.append(body / fit_sum + prev_fit)
            prev_fit = prev_fit + body / fit_sum

        # Use uniform distribution and select the rooms
        for num_selection in range(self._rooms_to_select):
            selection = random.uniform(low=0, high=1)
            for fit in self._bodies_fitness:
                if fit >= selection and self._bodies_fitness.index(fit) not in self._rooms_selected:
                    self._rooms_selected.append(self._bodies_fitness.index(fit))
                    break

        self._rooms_selected.append(len(self._bodies_area) - 1)

        # Remove all bodies from space to have a blank slate, but keep all the data in _bodies and _bodies_shape
        for room in range(len(self._bodies)):
            self._space.remove(self._bodies[room],self._bodies_shape[room])

        # Update the current listing of bodies and all following info to be able to edit info in the future
        for i in range(len(self._bodies)-1, 0, -1):
            if i not in self._rooms_selected:
                self._bodies.pop(i)
                self._bodies_shape.pop(i)
                self._bodies_area.pop(i)
                self._bodies_x_y.pop(i)

        print(self._bodies[0].position)

        # Expanding room sizes by 1 extra cell, running sim, then returning back to how it previously was
        placeholder = []
        body_copy = self._bodies.copy()
        for room_num in range(len(body_copy)):
            # Get vertices. clone, expand, place in same spot, finish
            width, height = self._bodies_x_y[room_num]
            print(f"Width {width}, Height {height}")
            vertices = [(-width / 2 - 2, -height / 2 - 2), (width / 2 + 2, -height / 2 - 2), (-width / 2 - 2, height / 2 + 2), (width / 2 + 2, height / 2 + 2)]
            physics_box = pymunk.Poly(body_copy[room_num], vertices)
            physics_box.mass = (width ** 2 + height ** 2) ** (2)
            placeholder.append(physics_box)
            self._space.add(body_copy[room_num], physics_box)

        self.showDungeonGeneration(1)

        for room_num in range(len(self._bodies)):
            new_pos = body_copy[room_num].position
            self._bodies[room_num].position = new_pos
            self._space.remove(body_copy[room_num], placeholder[room_num])
            self._space.add(self._bodies[room_num], self._bodies_shape[room_num])

        # Show final room product
        self.showDungeonGeneration(1)

        static_rooms = []
        return static_rooms

    def delaunayTriangulation(self):
        """
        Uses the self features and returns a finished map with all rooms connected to each other, boss room hopefully
        connected last
        :return: An array of 1's signifying a room, 0.5 signifying a corridor, 0's signifying a wall, and -1's signifying the boss room
        2 is a trap room
        """
        # TODO: Make a function to snap each room to cells, and also get their center
        snapped_grid = [[0] * math.ceil(math.sqrt(self._dungeon_size[0]**2 + self._dungeon_size[1]**2))] * math.ceil(math.sqrt(self._dungeon_size[0]**2 + self._dungeon_size[1]**2))
        delaunay_points = []
        for room in range(len(self._bodies)):
            curr_loc = self._space.bodies[room].position
            delaunay_points.append([math.floor(curr_loc[0]), math.floor(curr_loc[1])]) # Append the 'centroid' cell of the room to the delauney point thing
            curr_room_world_verteces = []
            for vert in self._bodies_shape[room].get_vertices():
                curr_room_world_verteces.append([math.floor(curr_loc[0] + vert[0]), math.floor(curr_loc[1] + vert[1])])
            # Set the room values to 1 if a room, 2 if trap room, -1 boss room (last room added)
            # now need to set the values in the snapped grid to their correct numbers
            for i in range(abs(curr_room_world_verteces[0][0] - curr_room_world_verteces[3][0])):
                for k in range(abs(curr_room_world_verteces[0][1] - curr_room_world_verteces[3][1])):
                    if room == self._bodies[-1]:
                        snapped_grid[curr_room_world_verteces[0][0] + i][curr_room_world_verteces[0][1] + k] = -1
                    else:
                        if self._traproom_probability < random.random():
                            snapped_grid[curr_room_world_verteces[0][0] + i][curr_room_world_verteces[0][1] + k] = 2
                        else:
                            snapped_grid[curr_room_world_verteces[0][0] + i][curr_room_world_verteces[0][1] + k] = 1


            # TODO: Using the points found above, use delaunay's algorithm to create connections between rooms
        # non_boss_delauynay = delaunay_points[1:-2]
        map_connections = Delaunay(delaunay_points)
        print(map_connections)
        print(type(map_connections))
        print(f"Points : {map_connections.points}")
        print(f"Neighbors : {map_connections.neighbors}")
        csr_style = []
        num_neighbors = len(map_connections.neighbors)
        for i in range(num_neighbors): # Get a n x n matrix of all the neighbors ? Or Do I instead convert it into a csgraph
            #CSR style
            curr_row = [0] * num_neighbors
            for j in map_connections.neighbors[i]:
                if j != -1:
                    if j == num_neighbors - 1 or i == num_neighbors - 1:
                        curr_row[j] = 20
                    else:
                        curr_row[j] = j*2 + 1
            csr_style.append(curr_row)

        map_node_connections = csr_matrix(csr_style)
        print(csr_style)
        map_connections = minimum_spanning_tree(map_node_connections) # Probably doesn't work since its not the correct input type
        print(f"Minimum spanning tree? {map_connections}")

        # TODO: Using the connections found above, path plan from each node to each node with a heuristic based on
        # not connecting to another room and giving a bonus for using the same corridor / path, as wel as straight halls



    def angularVelocityLimiter(self):
        for bodies in self._bodies:
            bodies.angular_velocity = 0
            bodies.angle = 0

    def showDungeonGeneration(self, run_seconds):
        startTime = time.time()
        curr_time = time.time()
        while curr_time < startTime + run_seconds:
            curr_time = time.time()
            for x in range(self._physics_steps_per_frame):
                self._space.step(self._dt)
                self.angularVelocityLimiter()
            self._screen.fill(pygame.Color("white"))
            self._space.debug_draw(self._draw_options)
            pygame.display.flip()
            self._clock.tick(50)


