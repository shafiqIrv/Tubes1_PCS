from typing import List, Optional
from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class CloseNDense(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.next_step: Optional[Position] = None
        self.goal_object: Optional[GameObject] = None

    """
    Metode untuk mendapatkan total point dari diamond yang bertetanggan dengan diamond yang sedang diteliti :
      X   X   X
      X   O   X
      X   X   X
    X adalah tetangga dari O dan O adalah diamond yang sedang diteliti
    """

    def getAdjacentDiamondPoints(
        self, diamond: GameObject, list_of_diamonds: List[GameObject]
    ):
        # Posisi diamond yang sedang diamati
        target_x = diamond.position.x
        target_y = diamond.position.y
        total = 0

        # Kumpulan posisi dari tetangga diamond yang sedang diamati
        adjacent = [
            [target_x + i, target_y + j] for i in range(-1, 2) for j in range(-1, 2)
        ]

        # Mengecek dalam posisi tetangga diamond yang sedang diamati, apakah ada diamond yang berada di posisi tersebut.
        # Jika ada, maka akan dihitung total point dari diamond yang berada dalam area tersebut (diamond yang sedang diamati juga ikut dihitung)
        for diamond in list_of_diamonds:
            if [diamond.position.x, diamond.position.y] in adjacent:
                total += diamond.properties.points
        # Total poinst dari area 3x3 tersebut
        return total

    """
    Fungsi untuk mendapatkan posisi diamond yang relatif terdekat dari bot, yaitu yang jaraknya tidak lebih dari jarak minimum antara bot dengan diamond terdekat + 2 unit satuan,
    yang memiliki total point diamond itu sendiri dengan tetangga diamondnya yang terbesar 
    """

    def getNearestDiamond(
        self,
        bot: GameObject,
        list_of_diamonds: List[GameObject],
    ):
        # Posisi bot
        curr_coordinate_x = bot.position.x
        curr_coordinate_y = bot.position.y

        # Inisialisasi variabel untuk mencari diamond yang terdekat dengan bot
        min_distance = float("inf")
        min_coordinate = None
        min_chunk_value = None

        # Kondisi jika sisa slot inventory bot hanya 1
        if (bot.properties.inventory_size - bot.properties.diamonds) == 1:
            # Jika tidak ada diamon yang bervalue 1, maka akan kembali ke base ("Edge case")
            min_coordinate = [bot.properties.base.x, bot.properties.base.y]
            # Mencari diamond terdekat dengan point =1
            for diamond in list_of_diamonds:
                distance = abs(diamond.position.x - curr_coordinate_x) + abs(
                    diamond.position.y - curr_coordinate_y
                )
                if distance < min_distance and diamond.properties.points == 1:
                    min_distance = distance
                    min_coordinate = [diamond.position.x, diamond.position.y]
            return min_coordinate

        else:
            # Mencari diamond yang jaraknya terdekat dengan bot
            for diamond in list_of_diamonds:
                # Menghitung Manhattan Distance antara bot dengan diamond
                distance = abs(diamond.position.x - curr_coordinate_x) + abs(
                    diamond.position.y - curr_coordinate_y
                )
                # Jika jaraknya lebih kecil dari minimum distance, maka akan di-set menjadi minimum distance baru
                if distance < min_distance:
                    min_distance = distance
                    min_coordinate = [diamond.position.x, diamond.position.y]
                    min_chunk_value = self.getAdjacentDiamondPoints(
                        diamond, list_of_diamonds
                    )

            # Inisialisasi variabel untuk mencari diamond dengan Highest Density dengan Relatively Closest Distance
            output_distance = min_distance
            output_coordinate = min_coordinate
            output_chunk_value = min_chunk_value

            # Proses mencari diamond dengan density value terbesar
            for diamond in list_of_diamonds:
                # Menghitung Manhattan Distance antara bot dengan diamond
                distance = abs(diamond.position.x - curr_coordinate_x) + abs(
                    diamond.position.y - curr_coordinate_y
                )
                # Menghitung total points dari diamond yang sedang diamati dengan tetangga-tetangganya
                temp_chunk_value = self.getAdjacentDiamondPoints(
                    diamond, list_of_diamonds
                )

                # Jika jarak diamond relatif dekat dengan bot (jaraknya tidak lebih dari minimum distance + 2),
                # maka akan diperhitungkan dalam proses pemilihan diamond dengan density value terbesar
                if distance <= min_distance + 2:
                    # Jika density value dari diamond yang sedang diamati lebih besar dari density value dari diamond yang sudah dipilih sebelumnya,
                    # maka diamond yang sedang diamati akan menjadi diamond yang dipilih
                    if temp_chunk_value > output_chunk_value:
                        output_distance = distance
                        output_coordinate = [diamond.position.x, diamond.position.y]
                        output_chunk_value = temp_chunk_value

            # Output koordinat diamond yang dipilih
            return output_coordinate

    """
    Fungsi untuk mnengecek apakah object dari goal masih terdapat dalam board dan masihh tipe yang sama 
    """

    def isGoalValid(self, board: Board):
        status = False
        for object in board.game_objects:
            if (
                self.goal_object.position.x == object.position.x
                and self.goal_object.position.y == object.position.y
                and self.goal_object.type == object.type
            ):
                status = True
                break
        return status

    """
    Fungsi untuk mendapatkan object dari posisi yang diberikan
    """

    def getGameObjectFromPosition(self, position: Position, board: Board):
        for object in board.game_objects:
            if object.position.x == position.x and object.position.y == position.y:
                return object
        return None

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
        delta_x, delta_y = 9999, 9999
        base_object = None
        button_object = None

        for object in board.game_objects:
            if object.type == "DiamondGameObject":
                list_of_diamonds.append(object)
            elif object.type == "TeleportGameObject":
                list_of_teleport.append(object)
                list_of_teleport_position.append([object.position.x, object.position.y])
            elif object.type == "BotGameObject":
                list_of_bots.append(object)
            elif object.type == "BaseGameObject":
                base_object = object
            elif object.type == "DiamondButtonGameObject":
                button_object = object
            list_of_objects.append([object.position.x, object.position.y])

        # Jika goal position sudah tercapai, goal lama akan dihapus
        if self.goal_position != None:
            if [self.goal_position.x, self.goal_position.y] == [
                current_position.x,
                current_position.y,
            ]:
                print("GOAL TERCAPAI")
                self.goal_position = None
                self.goal_object = None

        # Kondisi untuk balik ke base: Jika waktu mau habis atau inventory sudah full
        # + 2 digunakan supaya bot tidak telat untuk mencapai base
        if props.diamonds == props.inventory_size or (
            props.milliseconds_left / 1000
        ) <= (
            abs(current_position.x - bot_base.x)
            + abs(current_position.y - bot_base.y)
            + 2
        ):
            base = board_bot.properties.base
            self.goal_position = base
            self.goal_object = base_object
            print("OTW BASE")

        # Kondisi jika goal position masih lanjut
        if self.goal_position:
            # Cek apakah goal_position masih valid:
            # - Jika goal_object masih ada di dalam board
            # - Jika bot tidak masuk ke dalam teleport
            if self.isGoalValid(board) and not (
                [current_position.x, current_position.y] in list_of_teleport_position
            ):
                # Untuk debugging
                print(
                    "Goal position masih valid, Pada koordinat: ",
                    self.goal_position.x,
                    self.goal_position.y,
                )
                print("Goal Object: ", self.goal_object.type)

            # Kondisi jika goal position tidak valid
            else:
                # Jika goal position tidak valid, maka goal lama akan dihapus
                print("Goal position tidak valid")
                self.goal_position = None
                self.goal_object = None

        # Kondisi jika Goal Position belum ada, menggunakan if baru agar tidak terjadi error
        if self.goal_position == None:
            delta = self.getNearestDiamond(board_bot, list_of_diamonds)
            self.goal_position = Position(x=delta[0], y=delta[1])
            self.goal_object = self.getGameObjectFromPosition(self.goal_position, board)

        # Mencari arah gerak yang harus diambil oleh bot
        delta_x, delta_y = get_direction(
            current_position.x,
            current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        # Untuk debugging
        print("GOAL: ", self.goal_position.x, self.goal_position.y)
        print(f"Delta: {delta_x}, {delta_y}")

        if delta_x == 0 and delta_y == 0:
            print(
                f"Delta 0,0 OBJECT \n{board_bot}\nPROPERTIES: \n{board_bot.properties}"
            )

        # Mengembalikan arah gerak yang harus diambil oleh bot
        return delta_x, delta_y
