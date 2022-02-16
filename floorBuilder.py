import math
import random
from multimethod import multimethod

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

    @multimethod
    def buildFloor(self, size_string : str, type : str):
        """
        Builds a floor with a size type and returns a built floor
        :param size_string: The size of the dungeon as a string (tiny, small, medium, large, chonky)
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
        built_floor = []
        return built_floor


