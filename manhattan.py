# import time
from typing import List, Optional, Tuple
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class Manhattan(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    # Menentukan manhattan distance dari dua koordinat
    def manhattan_distance(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])  # return int

    # Menentukan koordinat terdekat dari starting point dengan value non zero yang belum dikunjungi
    def find_nearest_cell(
        self, bot: GameObject, list_of_diamonds_coors: List[Tuple[int, int]]
    ):
        current_pos = (bot.position.x, bot.position.y)

        min_dist = float("inf")
        nearest_cell = None

        for cell in list_of_diamonds_coors:
            dist = self.manhattan_distance(current_pos, cell)
            if dist < min_dist:
                min_dist = dist
                nearest_cell = cell
        return nearest_cell  # return tuple(int, int)

    # Fungsi untuk mendapatkan langkah selanjutnya yang harus diambil oleh bot
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
        list_of_diamonds_coor = []
        delta_x, delta_y = 9999, 9999

        for object in board.game_objects:
            if object.type == "DiamondGameObject":
                list_of_diamonds.append(object)
                list_of_diamonds_coor.append((object.position.x, object.position.y))
            elif object.type == "TeleportGameObject":
                list_of_teleport.append(object)
                list_of_teleport_position.append([object.position.x, object.position.y])
            elif object.type == "BotGameObject":
                list_of_bots.append(object)
            list_of_objects.append([object.position.x, object.position.y])

        # Kondisi untuk balik ke base: Jika waktu mau habis atau inventory sudah full
        if (
            props.diamonds == props.inventory_size
            or (props.milliseconds_left / 1000)
            <= ((current_position.x - bot_base.x) + (current_position.y - bot_base.y))
            + 1
        ):
            base = board_bot.properties.base
            self.goal_position = base

        # Validasi Goal Position
        if self.goal_position:
            # Cek apakah goal_position masih valid: Jika target masih berada di dalam list_of_objects dan bot tidak masuk ke dalam teleport
            if [self.goal_position.x, self.goal_position.y] in list_of_objects and not (
                [self.goal_position.x, self.goal_position.y]
                in list_of_teleport_position
            ):

                # Reset goal kalau tercapai
                if [self.goal_position.x, self.goal_position.y] == [
                    current_position.x,
                    current_position.y,
                ]:
                    self.goal_position = None
                    new_goal = self.find_nearest_cell(board_bot, list_of_diamonds_coor)
                    self.goal_position = Position(x=new_goal[0], y=new_goal[1])

            else:
                # Jika goal position tidak valid, maka akan dicari goal position yang baru
                new_goal = self.getNearestDiamond(board_bot, list_of_diamonds)
                self.goal_position = Position(x=new_goal[0], y=new_goal[1])

        else:
            goal = self.find_nearest_cell(board_bot, list_of_diamonds_coor)
            self.goal_position = Position(x=goal[0], y=goal[1])

        goal_x, goal_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        print("GOAL: ", self.goal_position.x, self.goal_position.y)
        print(f"Delta: {delta_x}, {delta_y}")

        if goal_x == 0 and goal_y == 0:
            print(
                f"Delta 0,0 OBJECT\n{board_bot}\n  PROPERTIES:\n{board_bot.properties}"
            )

        return goal_x, goal_y
