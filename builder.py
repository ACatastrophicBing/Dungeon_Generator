#!/usr/bin/env python
import math
import random
import matplotlib.pyplot as plt
import pymunk
import pymunk.pygame_util
import pygame

from floorBuilder import FloorBuilder

if __name__ == '__main__':
    print("Why is my AI class so ass?")
    generator = FloorBuilder()
    space = generator.buildFloor()
    # plt.axes()
    # generator.baseCircleBuild(5, 5)
    # generator.generateBossRoom(7,5)
    # rooms = generator.pre_physics_rooms
    # for room in rooms:
    #     print("The room is a %d by %d" %(room[0],room[1]))
    #     rectangle = plt.Rectangle((room[2],room[3]),room[0],room[1],ec='red')
    #     plt.gca().add_patch(rectangle)
    #     plt.axis('scaled')
    # plt.show()