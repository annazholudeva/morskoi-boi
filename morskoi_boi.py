from random import randint

field_size = 0


def greet():
    print('Добро пожаловать в игру "Морской бой"')
    print("Правила формата ввода данных в игре:")
    print("    x\n    y")
    print("где x - номер строки")
    print("где y - номер столбца\n")
    global field_size
    while field_size == 0:
        print('Задайте размер поля: '
              '\nвведите 1 - маленькое поле '
              '\nвведите 2 - среднее поле '
              '\nвведите 3 - большое поле\n')
        difficulty = input()
        difficulty = int(difficulty)
        if difficulty == 1:
            field_size = 6
            break
        elif difficulty == 2:
            field_size = 8
            break
        else:
            field_size = 10
            break
    return field_size


class BoardOutException(Exception):
    def __repr__(self):
        return "Вы стреляете  за пределы поля!"


class BoardUsedException(Exception):
    def __repr__(self):
        return "Клетка поля уже занята"


class BoardWrongShipException(Exception):
    pass


# создаем класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # проверка точек на равенство
    def __eq__(self, compare):
        return self.x == compare.x and self.y == compare.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


# создаем класс кораблей на игровом поле
class Ship:
    def __init__(self, bow, length, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    # добавляем метод dots, который возвращает список всех точек корабля
    @property
    def dots(self):
        dots = []
        for i in range(self.length):
            x = self.bow.x
            y = self.bow.y

            if self.direction == 0:
                x += i

            elif self.direction == 1:
                y += i

            dots.append(Dot(x, y))

        return dots

    def shooten(self, shot):
        return shot in self.dots


# описание доски для игры
class Board:
    def __init__(self, hid=False, size=greet()):
        self.size = size
        self.hid = hid

        self.c = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __repr__(self):
        r = "  | "
        for i in range(greet()):
            r += f"{i + 1} | "
        for i, row in enumerate(self.field):
            r += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            r = r.replace("■", "О")
        return r

    # проверка попадания точки класса Dot в поле
    def out(self, point):
        start = 0
        end = self.size
        return not ((start <= point.x < end) and (start <= point.y < end))

    # обводим корабль по контуру
    def contour(self, ship, v=False):
        near = [(0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1),
                (-1, -1), (-1, 0), (-1, 1)]
        for point in ship.dots:
            for pointx, pointy in near:
                current = Dot(point.x + pointx, point.y + pointy)
                if not (self.out(current)) and current not in self.busy:
                    if v:
                        self.field[current.x][current.y] = "."
                    self.busy.append(current)

    # постановка корабля на Board
    def add_ship(self, ship):
        for point in ship.dots:
            if self.out(point) or point in self.busy:
                raise BoardWrongShipException()
        for point in ship.dots:
            self.field[point.x][point.y] = "■"
            self.busy.append(point)

        self.ships.append(ship)
        self.contour(ship)

    # стрельба по Board
    def shot(self, point):
        if point in self.busy:
            raise BoardUsedException()

        if self.out(point):
            raise BoardOutException()

        self.busy.append(point)

        for ship in self.ships:
            if ship.shooten(point):
                ship.lives -= 1
                self.field[point.x][point.y] = "+"
                if ship.lives == 0:
                    self.c += 1
                    self.contour(ship, v=True)
                    print("убит")
                    return False
                else:
                    print("ранен")
                    return True

        self.field[point.x][point.y] = "."
        print("мимо")
        return False

    def restart(self):
        self.busy = []

    def beating(self):
        return self.c == len(self.ships)


# описание класса Player
class Player:
    def __init__(self, board, opponent):
        self.board = board
        self.opponent = opponent

    def ask(self):
        raise RuntimeError()

    def move(self):
        while not False:
            try:
                goal = self.ask()
                repeat = self.opponent.shot(goal)
                return repeat
            except BoardWrongShipException as error:
                print(error)


# задаем класс игрока - пользователя
class User(Player):
    def ask(self):
        while True:
            coordinates = input("Ваш ход: ").split()
            if len(coordinates) != 2:
                print("Необходимо ввести две координаты")
                continue
            x, y = coordinates
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


# задаем класс ИИ
class AI(Player):
    def ask(self):
        point = Dot(randint(0, greet() - 1), randint(0, greet() - 1))
        print(f"Ходит ИИ: {point.x + 1} {point.y + 1}")
        return point


# основная игра
class Game:
    def __init__(self):
        self.size = greet()
        player = self.random_board()
        ai = self.random_board()
        ai.hid = True
        # создание игроков
        self.ai = AI(ai, player)
        self.user = User(player, ai)

    def board(self, size):
        if size == 10:
            boats = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        elif size == 8:
            boats = [3, 3, 2, 2, 2, 1, 1, 1, 1]
        else:
            boats = [3, 2, 2, 1, 1, 1]
        board = Board(size=self.size)
        effort = 0
        for length in boats:
            while True:
                effort += 1
                if effort > 10000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.restart()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.board(greet())
        return board

    # цикл игры
    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            print(self.user.board)
            print("-" * 20)
            print("Доска ИИ:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ход игрока")
                repeat = self.user.move()
            else:
                print("Ход ИИ")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.beating():
                print("." * 20)
                print("Ты победил!")
                break

            if self.user.board.beating():
                print("." * 20)
                print("Победил ИИ!")
                break
            num += 1

    def start(self):
        self.loop()


game = Game()
game.start()
