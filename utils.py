import math
import pygame as pg

WHITE = pg.Color(255,255,255)
BLACK = pg.Color(0,0,0)
RED = pg.Color(255,0,0)
GREEN = pg.Color(0,255,0)
BLUE = pg.Color(0,0,255)

def lerp(a: float, b: float, t:float):
    return (1-t)*a+t*b

def add_vectors(a: list[float], b: list[float]):
    return [a[0]+b[0], a[1]+b[1]]

def sub_vectors(a, b):
    return add_vectors(a, scale_vector(b, -1))

def dot_product(a, b):
    return a[0]*b[0]+a[1]*b[1]

def scale_vector(a: list[float], s: float):
    return [a[0]*s, a[1]*s]
def normalize_vector(a):
    size = vector_size(a)
    if size == 0: 
        return a
    return scale_vector(a, 1/size)
def set_mag(a, mag):
    return scale_vector(normalize_vector(a),mag)

def rotate_vector(v, angle):
    sin = math.sin(angle)
    cos = math.cos(angle)
    return [v[0]*cos-v[1]*sin, -(v[0]*sin+v[1]*cos)]

def square_dist(a: list[float], b: list[float]):
    return (a[0]-b[0])**2+(a[1]-b[1])**2
def dist(a, b):
    return math.sqrt(square_dist(a,b))
def vector_size(a):
    return dist(a, [0,0])
def vector_angle(v):
    return math.atan2(v[1], v[0])

def vectors_eq(a: list[float], b: list[float]):
    return a[0] == b[0] and a[1] == b[1]