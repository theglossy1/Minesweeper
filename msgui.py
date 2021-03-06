import configparser
import os

import pygame

from minesweeper import EMPTY_SLOT, FLAG_SLOT, Minesweeper, MINE_BIT


FILE_ROOT = os.path.dirname(__file__)


def get_file(fname):
    if os.path.exists(fname):
        return fname
    else:
        return os.path.join(FILE_ROOT, fname)


def load_config():
    config = configparser.ConfigParser()
    config.read(get_file('msgui.ini'))
    return config


def hex_to_color(s):
    if len(s) < 3:
        s = s * 6
    elif len(s) < 6:
        s = s[0] * 2 + s[1] * 2 + s[2] * 2
    number = int(s, 16)
    r = number >> 16
    number -= r << 16
    g = number >> 8
    number -= g << 8
    b = number
    return r, g, b


def image_color_not_dead(item, colors, font, flag_image, cell_size, cell_border):
    if item == EMPTY_SLOT:
        color = colors['normal']
        image = None
    elif item == FLAG_SLOT:
        color = colors['selected']
        image = flag_image
    elif item == 0:
        color = colors['selected']
        image = None
    else:
        color = colors['selected']
        text = str(item)
        text_size = font.size(text)
        actual_size = cell_size - cell_border * 2
        image = pygame.Surface((actual_size, actual_size))
        image.fill(color)
        image.blit(font.render(text, True, colors['number']), pygame.Rect(
            (
                actual_size / 2 - text_size[0] / 2,
                actual_size / 2 - text_size[1] / 2,
            ),
            text_size,
        ))

    return color, image


def render(surface, board, cell_size, cell_border, flag_image, bomb_image, colors, font, state):
    surface.fill(colors['clear'])

    for (ri, row) in enumerate(board.render_matrix):
        for (ci, item) in enumerate(row):

            location = pygame.Rect(
                ci * cell_size + cell_border,
                ri * cell_size + cell_border,
                cell_size - cell_border * 2,
                cell_size - cell_border * 2,
            )

            if state != 1:
                color, image = image_color_not_dead(item, colors, font, flag_image, cell_size, cell_border)
            else:
                internal_item = board.board_matrix[ri, ci]
                if internal_item & MINE_BIT:
                    color = colors['bomb']
                    image = bomb_image
                else:
                    color, image = image_color_not_dead(item, colors, font, flag_image, cell_size, cell_border)
                
            surface.fill(color, location)
            if image is not None:
                surface.blit(image, location)


def main():
    config = load_config()
    board_width = config.getint('board', 'width')
    board_height = config.getint('board', 'height')
    bomb_count = config.getint('board', 'bombs')
    cell_size = config.getint('view', 'cell-size')
    cell_border = config.getint('view', 'cell-border')
    colors = {name: hex_to_color(value) for (name, value) in config['colors'].items()}
    rawfontname = config.get('view', 'font')
    fontname = get_file(rawfontname)
    fontsize = config.getint('view', 'font-size')

    pygame.init()
    screen = pygame.display.set_mode((board_width * cell_size, board_height * cell_size))

    if os.path.exists(fontname):
        font = pygame.font.Font(fontname, fontsize)
    else:
        font = pygame.font.SysFont(rawfontname, fontsize)

    board = Minesweeper(board_height, board_width, bomb_count)

    real_cell_size = cell_size - cell_border

    filename = get_file(config.get('images', 'bomb'))
    bomb_image = pygame.image.load(filename).convert_alpha()
    bomb_image = pygame.transform.scale(bomb_image, (real_cell_size, real_cell_size))

    filename = get_file(config.get('images', 'flag'))
    flag_image = pygame.image.load(filename).convert_alpha()
    flag_image = pygame.transform.scale(flag_image, (real_cell_size, real_cell_size))

    # from msterm import render as render_term
    # render_term(board)

    state = 0

    clock = pygame.time.Clock()
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                board = Minesweeper(board_height, board_width, bomb_count)
                state = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and not state:
                cell = (event.pos[1] // cell_size, event.pos[0] // cell_size)
                print('you', event.button, 'clicked', cell)
                if event.button == 1:
                    count = board.recursive_reveal(*cell)
                    if count == -1:
                        print('Game Over!')
                        state = 1
                elif event.button == 3:
                    board.toggle_flag(*cell)
                    if board.has_won():
                        print('You Won!')
                        state = 2
                        board.reveal_all()

        render(screen, board, cell_size, cell_border, flag_image, bomb_image, colors, font, state)
        # if dead:
        #     screen.blit(font.render('Game Over!', True, colors['bomb']), pygame.Rect(10, 10, 200, 200))
        pygame.display.update()


if __name__ == '__main__':
    main()
