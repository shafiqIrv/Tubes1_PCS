from typing import Optional
import time
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


# Revisi Bot
# kalau waktu mau abis langsung balik aja
# Portal belum dipotimasi
# tackle juga belum


class RvansLogic(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    # Chunk berukuran 3x3, untuk menghitung diamond di sekitar
    def getTotalDiamondsInChunk(
        self, board: Board, diamond_target: GameObject, delta_x, delta_y
    ):
        items = board.game_objects
        x_target = diamond_target.position.x
        y_target = diamond_target.position.y

        count = diamond_target.properties.points

        if delta_x < 0 and delta_y == 0:
            x1 = -2
            x2 = 0
            y1 = -1
            y2 = 1

        elif delta_x > 0 and delta_y == 0:
            x1 = 0
            x2 = 2
            y1 = -1
            y2 = 1

        elif delta_x == 0 and delta_y < 0:
            x1 = -1
            x2 = 1
            y1 = -2
            y2 = 0

        elif delta_x == 0 and delta_y > 0:
            x1 = -1
            x2 = 1
            y1 = 0
            y2 = 2

        elif delta_x < 0 and delta_y < 0:
            x1 = -2
            x2 = 0
            y1 = -2
            y2 = 0

        elif delta_x < 0 and delta_y > 0:
            x1 = -2
            x2 = 0
            y1 = 0
            y2 = 2

        elif delta_x > 0 and delta_y < 0:
            x1 = 0
            x2 = 2
            y1 = -2
            y2 = 0

        elif delta_x > 0 and delta_y > 0:
            x1 = 0
            x2 = 2
            y1 = 0
            y2 = 2

        else:
            x1 = -1
            x2 = 1
            y1 = -1
            y2 = 1

        for item in items:
            for i in range(x1, x2 + 1):
                for j in range(y1, y2 + 1):
                    if (
                        item.position.x == x_target + i
                        and item.position.y == y_target + j
                        and item.type == "DiamondGameObject"
                    ):
                        count += item.properties.points
        return count

    def getNearestDiamond(self, board_bot: GameObject, board: Board):
        # Bot Coordinate
        x = board_bot.position.x
        y = board_bot.position.y
        min = [999999, 0, 0]  # [distance, points,coordinate]
        nearest = None

        # Get Nearest diamond without portal
        for object in board.game_objects:
            if object.type == "DiamondGameObject":
                temp_min = [
                    ((x - object.position.x) ** 2 + (y - object.position.y) ** 2)
                    ** (1 / 2),
                    object.properties.points,
                    [object.position.x, object.position.y],
                ]
                if temp_min[0] < min[0]:
                    min = temp_min

                elif temp_min[0] == min[0]:
                    if temp_min[1] > min[1]:
                        min = temp_min

        # find secondary diamond that the only difference is 2 blocks
        list_of_min = [GameObject]

        addjacentWithMin = [
            [(min[2][0] - 1), (min[2][1] - 1)],
            [(min[2][0]), (min[2][1] - 1)],
            [(min[2][0] + 1), (min[2][1] - 1)],
            [(min[2][0] - 1), (min[2][1])],
            [(min[2][0] + 1), (min[2][1])],
            [(min[2][0] - 1), (min[2][1] + 1)],
            [(min[2][0]), (min[2][1] + 1)],
            [(min[2][0] + 1), (min[2][1] + 1)],
        ]

        for object in board.game_objects:
            if object.type == "DiamondGameObject":
                temp_min = [
                    ((x - object.position.x) ** 2 + (y - object.position.y) ** 2)
                    ** (1 / 2),
                    object.properties.points,
                    [object.position.x, object.position.y],
                ]
                if temp_min[0] <= min[0] + 2 and not (
                    [object.position.x, object.position.y] in addjacentWithMin
                ):
                    list_of_min.append(object)
                    print("OBJEK\n", object, "\n")

        print("LIST OF MIN: \n", list_of_min, "\n")

        # find the most valuable chunk of diamond
        most_valuable_chunk = [0, None]  # [chunk,coordinate]
        for diamond in list_of_min[
            1:
        ]:  # Pakai [1:] karena elemen pertama adalah deklarasi GameObject
            chunk = self.getTotalDiamondsInChunk(
                board, diamond, diamond.position.x - x, diamond.position.y - y
            )
            print("CHUNK: ")
            if chunk > most_valuable_chunk[0]:
                most_valuable_chunk[0] = chunk
                most_valuable_chunk[1] = [diamond.position.x, diamond.position.y]

        nearest = most_valuable_chunk[1]

        if nearest == None:
            nearest = [0, 0]

        print("NEAREST: ", nearest)
        return nearest

    def next_move(self, board_bot: GameObject, board: Board):
        start_time = time.time()
        props = board_bot.properties
        current_position = board_bot.position

        # Board base coordinate
        bot_base = board_bot.properties.base

        print("GOAL POSITION: ", self.goal_position)
        # Analyze new state
        if props.diamonds == 5 or (props.milliseconds_left / 1000) <= (
            (current_position.x - bot_base.x) + (current_position.y - bot_base.y) + 1
        ):  # Jika sudah penuh atau waktu mau abis
            # Move to base
            base = board_bot.properties.base
            self.goal_position = base
        else:
            delta = self.getNearestDiamond(board_bot, board)
            print("DELTA: ", delta)
            print("GOAL POSITION: ", self.goal_position)
            self.goal_position = Position(x=delta[0], y=delta[1])
        # Kala ada diamond di sekitar, ambil diamond
        current_position = board_bot.position

        print("GOAL POSITION: ", self.goal_position)
        if self.goal_position != None:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
        target = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        end_time = time.time()

        print("Processing time: ", end_time - start_time)
        print(f"Delta: {target}")
        return delta_x, delta_y


# TYPES OF GAME OBJECTS:

# Type TeleportGameObject
# Properties(points=None, pair_id='1', diamonds=None, score=None, name=None, inventory_size=None, can_tackle=None, milliseconds_left=None, time_joined=None, base=None)
# Properties(points=None, pair_id='1', diamonds=None, score=None, name=None, inventory_size=None, can_tackle=None, milliseconds_left=None, time_joined=None, base=None)

# Type DiamondButtonGameObject
# Properties(points=None, pair_id=None, diamonds=None, score=None, name=None, inventory_size=None, can_tackle=None, milliseconds_left=None, time_joined=None, base=None)

# Type DiamondGameObject
# Properties(points=2, pair_id=None, diamonds=None, score=None, name=None, inventory_size=None, can_tackle=None, milliseconds_left=None, time_joined=None, base=None)
# Properties(points=1, pair_id=None, diamonds=None, score=None, name=None, inventory_size=None, can_tackle=None, milliseconds_left=None, time_joined=None, base=None)

# Type BotGameObject
# Properties(points=None, pair_id=None, diamonds=0, score=1, name='stima3', inventory_size=5, can_tackle=True, milliseconds_left=1380, time_joined='2024-02-27T15:10:25.538Z', base=Base(y=10, x=10))

# Type BaseGameObject
# Properties(points=None, pair_id=None, diamonds=None, score=None, name='stima3', inventory_size=None, can_tackle=None, milliseconds_left=None, time_joined=None, base=None)

# BOARD_BOT PROPERTIES:
# GameObject(id=389, position=Position(y=4, x=13), type='BotGameObject',
# properties=Properties(points=None, pair_id=None, diamonds=0, score=0,
# name='stima3', inventory_size=5, can_tackle=True, milliseconds_left=58982, time_joined='2024-02-27T14:55:24.216Z', base=Base(y=3, x=12)))
