import random
from typing import List, Optional, Tuple
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class NearestGreedy(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.next_step: Optional[Position] = None

    def getAdjacentDiamondPoints(
        self, diamond: GameObject, list_of_diamonds: List[GameObject]
    ):
        target_x = diamond.position.x
        target_y = diamond.position.y
        total = 0
        adjacent = [
            [target_x + i, target_y + j] for i in range(-1, 2) for j in range(-1, 2)
        ]

        for diamond in list_of_diamonds:
            if [diamond.position.x, diamond.position.y] in adjacent:
                total += diamond.properties.points

        return total

    def getNearestDiamond(
        self,
        bot: GameObject,
        list_of_diamonds: List[GameObject],
    ):
        curr_coordinate_x = bot.position.x
        curr_coordinate_y = bot.position.y

        min_distance = float("inf")
        min_coordinate = None
        min_chunk_value = None

        list_of_near_diamonds: List[GameObject] = []
        for diamond in list_of_diamonds:
            distance = abs(diamond.position.x - curr_coordinate_x) + abs(
                diamond.position.y - curr_coordinate_y
            )
            if distance < min_distance:
                min_distance = distance
                min_coordinate = [diamond.position.x, diamond.position.y]
                min_chunk_value = self.getAdjacentDiamondPoints(
                    diamond, list_of_diamonds
                )

            elif distance == min_distance:
                temp_chunk_value = self.getAdjacentDiamondPoints(
                    diamond, list_of_diamonds
                )
                if temp_chunk_value > min_chunk_value:
                    min_chunk_value = temp_chunk_value
                    min_coordinate = [diamond.position.x, diamond.position.y]

        output_distance = min_distance
        output_coordinate = min_coordinate
        output_chunk_value = min_chunk_value

        for diamond in list_of_diamonds:
            distance = abs(diamond.position.x - curr_coordinate_x) + abs(
                diamond.position.y - curr_coordinate_y
            )
            temp_chunk_value = self.getAdjacentDiamondPoints(diamond, list_of_diamonds)
            if distance <= min_distance + 2:
                if temp_chunk_value > output_chunk_value:
                    output_distance = distance
                    output_coordinate = [diamond.position.x, diamond.position.y]
                    output_chunk_value = temp_chunk_value

        return output_coordinate

    # hINDARIN TELEPORT, HINDARIN MUSUH, kalau base jauh lebih deket daripada goaal selnjutny, ke base aja dulu
    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        bot_base = board_bot.properties.base
        current_position = board_bot.position

        # Plotting data
        list_of_diamonds: List[GameObject] = []
        list_of_bots: List[GameObject] = []
        list_of_teleport: List[GameObject] = []
        list_of_teleport_position = []
        list_of_objects = []
        delta_x, delta_y = 9999, 9999

        for object in board.game_objects:
            if object.type == "DiamondGameObject":
                list_of_diamonds.append(object)
            elif object.type == "TeleportGameObject":
                list_of_teleport.append(object)
                list_of_teleport_position.append([object.position.x, object.position.y])
            elif object.type == "BotGameObject":
                list_of_bots.append(object)
            list_of_objects.append([object.position.x, object.position.y])

        # Kondisi untuk balik ke base: Jika waktu mau habis atau diamond sudah 5
        if (
            props.diamonds == 5
            or (props.milliseconds_left / 1000)
            <= ((current_position.x - bot_base.x) + (current_position.y - bot_base.y))
            + 1
        ):
            base = board_bot.properties.base
            self.goal_position = base

        # Jika sudah ada goal position dari perhitungan sebelumnya
        if self.goal_position:
            # Cek apakah goal_position masih valid
            if [self.goal_position.x, self.goal_position.y] in list_of_objects and not (
                [self.goal_position.x, self.goal_position.y]
                in list_of_teleport_position
            ):
                print(
                    "Goal position masih valid, Pada koordinat: ",
                    self.goal_position.x,
                    self.goal_position.y,
                )
                # Jika goal position sudah tercapai, reset goal nya
                if [self.goal_position.x, self.goal_position.y] == [
                    current_position.x,
                    current_position.y,
                ]:
                    print("GOAL TERCAPAI")
                    self.goal_position = None
                    new_goal = self.getNearestDiamond(board_bot, list_of_diamonds)
                    self.goal_position = Position(x=new_goal[0], y=new_goal[1])

            else:
                print("Goal position tidak valid")
                new_goal = self.getNearestDiamond(board_bot, list_of_diamonds)
                self.goal_position = Position(x=new_goal[0], y=new_goal[1])

            # delta_x, delta_y = get_direction(
            #     current_position.x,
            #     current_position.y,
            #     self.goal_position.x,
            #     self.goal_position.y,
            # )

        else:
            # Goal Position belum ada
            delta = self.getNearestDiamond(board_bot, list_of_diamonds)
            self.goal_position = Position(x=delta[0], y=delta[1])

        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        print("GOAL: ", self.goal_position.x, self.goal_position.y)
        print(f"Delta: {delta_x}, {delta_y}")

        if delta_x == 0 and delta_y == 0:
            print(
                f"Delta 0,0 OBJECT\n{board_bot}\n  PROPERTIES:\n{board_bot.properties}"
            )

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
