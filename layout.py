import math

SIZE = [1200,800]

# To make it look normal, we stick the holes on the edges (not corners) in a little
hole_dep = [5/SIZE[0], 5/SIZE[1]]
LAYOUT = {
    "balls": [
    ],
    "player": [0.5,0.5],
    "holes": [
        [hole_dep[0],hole_dep[1]], [0.5,-hole_dep[1]], [1-hole_dep[0],hole_dep[1]],
        [-hole_dep[0],0.5], [1+(hole_dep[0]),0.5],
        [hole_dep[0],1-hole_dep[1]], [0.5,1+(hole_dep[1])], [1-hole_dep[0],1-hole_dep[1]],
    ],
    "score": [0.75, 0]
}

for i in range(20):
    angle = (i/20)*math.pi*2
    LAYOUT["balls"].append(
        [math.cos(angle)*0.25+0.5, math.sin(angle)*0.25*SIZE[0]/SIZE[1]+0.5]
    )

HOLE_R = 20
"""
    The radius of the holes on the board, px
"""