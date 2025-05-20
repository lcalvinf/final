SIZE = [1200,800]

hole_dep = 5 # To make it look normal, we stick the holes on the edges (not corners) in a little
LAYOUT = {
    "balls": [
        [0.125, 0.25],
        [0.25, 0.25],
        [0.375, 0.25],
        [0.5, 0.25],
        [0.625, 0.25],
        [0.75, 0.25],
        [0.825, 0.25],

        [0.125, 0.75],
        [0.25, 0.75],
        [0.375, 0.75],
        [0.5, 0.75],
        [0.625, 0.75],
        [0.75, 0.75],
        [0.825, 0.75],
    ],
    "player": [0.5,0.5],
    "holes": [
        [0,0], [0.5,-hole_dep/SIZE[1]], [1,0],
        [-hole_dep/SIZE[0],0.5], [1+(hole_dep/SIZE[0]),0.5],
        [0,1], [0.5,1+(hole_dep/SIZE[1])], [1,1],
    ]
}

HOLE_R = 20
"""
    The radius of the holes on the board, px
"""