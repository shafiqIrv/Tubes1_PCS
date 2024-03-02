import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class RandomLogic(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        # Analyze new state
        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base
            self.goal_position = base
        else:
            # Just roam around
            self.goal_position = None

        current_position = board_bot.position
        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
        else:
            # Roam around
            delta = self.directions[self.current_direction]
            delta_x = delta[0]
            delta_y = delta[1]
            if random.random() > 0.6:
                self.current_direction = (self.current_direction + 1) % len(
                    self.directions
                )
        for object in board.game_objects:
            print("type: ", object.type)
            print (object.properties)


        print(f"Delta: {delta_x}, {delta_y}")
    
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