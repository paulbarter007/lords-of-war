from Units.BaseUnit import Teams
from Units.Units import Settler, WolfHero, BarbarianHero, Wolf, Barbarian, BarbarianHorde
from Units.Spaces import River, Road, Mountain, Plain, City, Forest, Ruins, BarbarianVillage, SpaceTypes
import random


def make_random_board(team_wolf, team_barbarian, width_units, height_units, space_width, space_height, percentage_road=0.3, percentage_river=0.1,
                      percentage_mountain=0.1, percentage_forrest=0.2, percentage_ruins=0.05, percentage_barbarian=0.03):
    board = []
    wolf_start_squares = [(0, 0), (1, 0), (0, 1), (1, 1)]
    length = height_units
    breadth = width_units
    barbarian_start_squares = [(length-1, breadth-1), (length -2, breadth-1),
                               (length-1, breadth-2), (length-2, breadth-2)]
    for height_unit in range(height_units):
        for width_unit in range(width_units):
            space_type = Plain
            if (height_unit, width_unit) in wolf_start_squares:
                space_type = Plain
            elif (height_unit, width_unit) in barbarian_start_squares:
                space_type = Plain
            else:
                rand_value = random.random()
                if rand_value < percentage_road:
                    space_type = Road
                elif rand_value < percentage_road + percentage_river:
                    space_type = River
                elif rand_value < percentage_road + percentage_river + percentage_mountain:
                    space_type = Mountain
                elif rand_value < percentage_road + percentage_river + percentage_mountain + percentage_forrest:
                    space_type = Forest
                elif rand_value < percentage_road + percentage_river + percentage_mountain + percentage_forrest + percentage_ruins:
                    space_type = Ruins
                elif rand_value < percentage_road + percentage_river + percentage_mountain + percentage_forrest + percentage_ruins + percentage_barbarian:
                    space_type = BarbarianVillage

            initialised_space = space_type(space_width * width_unit + 60, 50 + space_height * height_unit)

            if initialised_space.type == SpaceTypes.BARBARIAN_VILLAGE:
                initialised_space.add_unit(BarbarianHorde(1, 2, Teams.ENEMY))

            if (height_unit == 0 and width_unit == 0) or (height_unit == height_units -1 and width_unit == width_units -1):
                # Start space
                if height_unit == 0 and width_unit == 0:
                    start_space = City(space_width * width_unit + 60, 50 + space_height * height_unit, owner=team_wolf)
                    team_wolf.owned_cities.append(start_space)
                    start_space.add_unit(Wolf(1, 2, Teams.WOLF))
                    start_space.add_unit(Settler(1, 2, Teams.WOLF))
                    start_space.add_unit(WolfHero(1, 2, Teams.WOLF))
                    start_space.is_visible_by_wolf = True
                elif height_unit == height_units -1 and width_unit == width_units -1:
                    start_space = City(space_width * width_unit + 60, 50 + space_height * height_unit, owner=team_barbarian)
                    team_barbarian.owned_cities.append(start_space)
                    start_space.add_unit(Barbarian(1, 2, Teams.BARBARIAN))
                    start_space.add_unit(Settler(1, 2, Teams.BARBARIAN))
                    start_space.add_unit(BarbarianHero(1, 2, Teams.BARBARIAN))
                    start_space.is_visible_by_barbarian = True
                board.append(start_space)
                continue
            board.append(initialised_space)
    return board

