import math
from numpy import random
import pymunk
from multimethod import multimethod
import pygame
import pymunk.pygame_util
import time

"""
Each cell is a size of 5 ft,
A cell is a wall or not walkable if true, a cell is open if false 
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


        # Physics Engine Time info
        # Time Step
        self._dt = 1.0 / 60.0
        # Number of physics steps per screen frame
        self._physics_steps_per_frame = 30


        # pygame viewing info
        self._screen_width = 100
        self._screen_height = 100
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
        :return: A built floor as a 2D list of a list containing an int of if the cell is occupied or not (boolean)
        Boolean is true if wall, false if open
        """
        built_floor = []
        return built_floor

    def buildFloor(self, cell_max : int, room_size  : int):
        """
        Builds a floor with a size type and returns a built floor
        :param cell_max: The size of the dungeon to make a cell_max by cell_max size
        :param room_size: The avg size of a room in cells
        :return: A built floor as a 2D list of a list containing an int of if the cell is occupied or not (boolean)
        Boolean is true if wall, false if open
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

        return self._space

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


