import sys
import os
import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SIZE_WINDOW = 600, 600

CROSS = 'Золотой_слиток.png'
CIRCLE = 'Алмаз.png'
WIDTH_LINES = 10

pygame.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Button(pygame.sprite.Sprite):
    # Класс кнопок для выбора режимов игры
    def __init__(self, text, pos, size):
        self.image = pygame.Surface(size)
        self.image.fill(WHITE)
        self.rect = pygame.Rect(pos, size)
        self.font = pygame.font.SysFont("Calibri", 30)
        self.text = self.font.render(text, 2, BLACK)
        self.image.blit(self.text, (2, 2))
        self.pos = pos


class GameItem(pygame.sprite.Sprite):

    def __init__(self, pos, size, image_name=None):
        super().__init__()
        self.pos = pos
        self.size = size
        self.selectable = True
        self.init_rect()
        if image_name:
            self.set_image(image_name)
        else:
            self.image = pygame.Surface(size)
            self.image.set_alpha(100)

    def init_rect(self):
        self.rect = pygame.Rect(
            self.pos, self.size)

    def set_pos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def set_image(self, image_name):
        if self.selectable:
            self.image = load_image(image_name)
            self.rect = self.image.get_rect()
            self.set_pos(self.pos)
            self.selectable = False

    def set_number(self, number):
        self.number = number


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(SIZE_WINDOW)
        pygame.display.set_caption('pygame')
        self.clock = pygame.time.Clock()

        self.player_1 = CROSS
        self.player_2 = CIRCLE

        self.computer = False
        # текущий игрок (игрок, который сейчас ходит)
        self.current_player = self.player_1
        self.background = GameItem((0, 0), SIZE_WINDOW, 'фон1.jpg')

        # список всех спрайтов(ячейки, в которые можно вставить крестик или нолик)
        self.list_sprites = list()
        self.board = list(range(0, 9))

        self.list_buttons = list()
        self.name_winner = None

        # флаг, который сигнализирует об окончании игры
        self.end = False

        self.init_grid()
        self.init_buttons()

    def draw_grid(self):
        # функция для рисования сетки поля
        left_side = (SIZE_WINDOW[0] - self.size_field[0]) // 2
        right_side = SIZE_WINDOW[0] - left_side

        up_side = (SIZE_WINDOW[1] - self.size_field[1]) // 2
        down_side = SIZE_WINDOW[1] - up_side

        for i in range(1, 2 + 1):
            pygame.draw.line(self.screen, BLACK, [
                             left_side, up_side + i * self.size_cell[1]],
                             [right_side, up_side + i * self.size_cell[1]], WIDTH_LINES)

        for i in range(1, 2 + 1):
            pygame.draw.line(self.screen, BLACK, [
                             left_side + i * self.size_cell[0], up_side],
                             [left_side + i * self.size_cell[0], down_side], WIDTH_LINES)

    def init_grid(self):
        # функция для инициализации полей, при нажатии на которые появляются соответствующие картинки

        # размер всего поля
        self.size_field = SIZE_WINDOW[0] * 0.8, SIZE_WINDOW[1] * 0.8
        # размер ячейки поля
        self.size_cell = self.size_field[0] // 3, self.size_field[1] // 3

        left_side = (SIZE_WINDOW[0] - self.size_field[0]) // 2
        right_side = SIZE_WINDOW[0] - left_side

        up_side = (SIZE_WINDOW[1] - self.size_field[1]) // 2
        down_side = SIZE_WINDOW[1] - up_side

        # здесь создаются ячейки поля, у каждой ячейки будет свой номер от 0 до 9
        number_sprite = 0
        for j in range(3):
            for i in range(3):
                rectangle = GameItem((left_side + i * self.size_cell[0] + WIDTH_LINES, up_side + j * self.size_cell[1] + WIDTH_LINES),
                                     (self.size_cell[0] - 2 * WIDTH_LINES, self.size_cell[1] - 2 * WIDTH_LINES))
                rectangle.set_number(number_sprite)
                self.list_sprites.append(rectangle)
                number_sprite += 1

    def init_buttons(self):
        # создание кнопок на стартовом экране
        self.list_buttons.append(
            Button('Играть компьютером', (60, 550), (250, 40)))

        self.list_buttons.append(
            Button('Играть с другом', (350, 550), (200, 40)))

    def draw_buttons(self):
        # рисование кнопок на стартовом экране
        for button in self.list_buttons:
            self.screen.blit(button.image, button.pos)

    def draw_sprites(self):
        # отрисовка всех ячеек поля
        group = pygame.sprite.Group(*self.list_sprites)
        group.draw(self.screen)

    def update_background(self):
        self.screen.fill(WHITE)
        self.screen.blit(self.background.image, (0, 0))

    def next_player(self):
        if self.current_player == self.player_1:
            self.current_player = self.player_2
        else:
            self.current_player = self.player_1

    def check_win(self):
        win_coord = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
                     (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        if self.end:
            return 1

        for each in win_coord:
            if self.board[each[0]] == self.board[each[1]] == self.board[each[2]]:
                if self.current_player == self.player_2:
                    winner = 'Нолик'
                else:
                    winner = ' Крестик'
                self.name_winner = Button(
                    'Выиграл ' + winner, (250, 550), (200, 40))
                print(winner)
                self.end = True
                return self.board[each[0]]
        return False

    def computer_move(self):
        BEST_MOVES = (4, 0, 2, 6, 8, 1, 3, 5, 7)
        for player_answer in BEST_MOVES:
            if player_answer >= 0 and player_answer <= 8:
                if self.list_sprites[player_answer].selectable:
                    self.board[player_answer] = self.current_player
                    self.list_sprites[player_answer].set_image(
                        self.current_player)
                    self.next_player()
                    break

    def start_screen(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.list_buttons:
                        if button.rect.collidepoint(event.pos):
                            # при нажатии на первую кнопку(игра с компьютером)
                            # устанавливается флаг self.computer = True,
                            # и теперь во время игры он будет ходить вторым
                            if self.list_buttons.index(button) == 0:
                                self.computer = True
                            running = False
                            self.start_game()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.update_background()
            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(50)

    def start_game(self):
        self.background = GameItem((0, 0), SIZE_WINDOW, 'фон2.jpg')
        running = True
        while running:
            # если играет компьютер и сейчас ход второго игрока, то компьютер сделает свой ход
            if self.computer and self.current_player == self.player_2:
                self.computer_move()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.check_win():
                    # здесь отслеживается ячейка, по которой мы нажимаем и у нее устанавливается соответствующая картинка
                    # проверяются условия на выигрыш одного из игроков и ход переходит
                    for sprite in self.list_sprites:
                        if sprite.rect.collidepoint(event.pos):
                            sprite.set_image(self.current_player)
                            self.board[sprite.number] = self.current_player
                            self.check_win()
                            self.next_player()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.update_background()
            self.draw_grid()
            self.draw_sprites()
            if self.name_winner:
                self.screen.blit(self.name_winner.image, self.name_winner.pos)
            pygame.display.flip()
            self.clock.tick(50)


if __name__ == '__main__':
    Game().start_screen()
