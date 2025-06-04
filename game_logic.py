import random

def generate_board():
    return [['▫️' for _ in range(9)] for _ in range(9)]

def render_board(board):
    return "\n".join("".join(row) for row in board)

def get_random_shape():
    return random.choice(['■', '■■', '▣', '▢', '▥'])

def generate_shapes(n=3):
    return [get_random_shape() for _ in range(n)]

def random_bonus():
    return random.choice(["+5 очков", "+1 фигура", "ничего"])

