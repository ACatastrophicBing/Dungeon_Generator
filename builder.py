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
