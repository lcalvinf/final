import math

SIZE = [1200, 800]

# To make it look normal, we stick the holes on the edges (not corners) in a little
hole_dep = [5/SIZE[0], 5/SIZE[1]]
LAYOUT = {
# Balls
    "red-balls": [],
    "blue-balls": [],
    "player": [0.5, 0.5],

# Board
    "holes": [
        [hole_dep[0], hole_dep[1]], [0.5, -hole_dep[1]], [1-hole_dep[0], hole_dep[1]],
        [-hole_dep[0], 0.5], [1+(hole_dep[0]),0.5],
        [hole_dep[0], 1-hole_dep[1]], [0.5, 1+(hole_dep[1])], [1-hole_dep[0], 1-hole_dep[1]],
    ],

# HUD
    "score": [0.75, 20/SIZE[1]],
    "shot_count": [0.25,20/SIZE[1]]
}

for i in range(10):
    angle = (i/10)*math.pi*2
    type = "red-balls" if i%2 == 0 else "blue-balls"
    LAYOUT[type].append(
        [math.cos(angle)*0.25+0.5, math.sin(angle)*0.25*SIZE[0]/SIZE[1]+0.5]
    )

HOLE_R = 40
"""
    The radius of the holes on the board, px
"""
