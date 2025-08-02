from Attack import show_popup
from Units.BaseUnit import BaseUnit
from Units.Spaces import City


class Soldier(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Soldier"
        super().__init__(x, y, team)
        self.health = 100
        self.can_shoot = False
        self.gold_cost = 5
        self.attack_power = 30
        self.movement = 350
        self.initial_movement = 350

class Archer(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Archer"
        super().__init__(x, y, team)
        self.health = 30
        self.can_shoot = True
        self.range = 200
        self.attack_power = 50
        self.defense_power = 5
        self.movement = 550
        self.initial_movement = 550
        self.gold_cost = 7

class Settler(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Settler"
        super().__init__(x, y, team)
        self.health = 5
        self.attack_power = 0
        self.defense_power = 0
        self.movement = 350
        self.initial_movement = 350
        self.gold_cost = 8

    def check_far_enough_from_city(self, current_space, board):
        # distance from any city, not just your own
        for space in board:
            if space.name == "City":
                if abs(space.rect.centerx - current_space.rect.centerx) < 300 and \
                   abs(space.rect.centery - current_space.rect.centery) < 300:
                    return False
        return True

    def settle(self, current_space, team, board, screen):
        if current_space.name != "City" and current_space.name != "River" and current_space.name != "Mountain":
            if self.check_far_enough_from_city(current_space, board):
                new_space = City(current_space.rect.centerx, current_space.rect.centery)
                new_space.owner = team
                new_space.units = [unit for unit in current_space.units if unit.id != self.id]
                number_on_board = 0
                for space in board:
                    if space.id == current_space.id:
                        break
                    number_on_board += 1
                board[number_on_board] = new_space
                team.owned_cities.append(new_space)
            else:
                show_popup(screen, "Too close to another city to settle")

class Hero(BaseUnit):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        self.type = 'Hero'

    def search_ruins(self, screen, active_space, board, current_active_team):
        from Utils import get_space_unit_is_in, handle_ruins_searched
        ruin = get_space_unit_is_in(board, self)
        if ruin.name != 'Ruins':
            show_popup(screen, "You need to be on a Ruins space to search")
            return
        if not ruin.searched:
            ruin.search()
            ruin.draw(screen, current_active_team)
            handle_ruins_searched(ruin, current_active_team, screen, self)
        else:
            show_popup(screen, "This Ruin has already been searched")

class WolfHero(Hero):
    def __init__(self, x, y, team):
        self.name = "wolf-hero"
        super().__init__(x, y, team)
        self.health = 150
        self.attack_power = 50
        self.defense_power = 50
        self.movement = 550
        self.initial_movement = 550

class BarbarianHero(Hero):
    def __init__(self, x, y, team):
        self.name = "barbarian-hero"
        super().__init__(x, y, team)
        self.health = 150
        self.attack_power = 150
        self.defense_power = 80
        self.movement = 350
        self.initial_movement = 350

class Wolf(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Wolf"
        super().__init__(x, y, team)
        self.health = 100
        self.can_shoot = False
        self.gold_cost = 5
        self.attack_power = 30
        self.defense_power = 20
        self.movement = 650
        self.initial_movement = 650

class Barbarian(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Barbarian"
        super().__init__(x, y, team)
        self.health = 100
        self.can_shoot = False
        self.gold_cost = 5
        self.attack_power = 80
        self.movement = 250
        self.initial_movement = 250
        self.defense_power = 45

class BarbarianHorde(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Barbarian-horde"
        super().__init__(x, y, team)
        self.health = 25
        self.can_shoot = False
        self.attack_power = 30
        self.movement = 0
        self.initial_movement = 0
        self.defense_power = 20

class Bats(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Bats"
        super().__init__(x, y, team)
        self.health = 10
        self.fly = True
        self.attack_power = 15
        self.movement = 450
        self.initial_movement = 450
        self.defense_power = 10

class Knight(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Knight"
        super().__init__(x, y, team)
        self.gold_cost = 7
        self.health = 120
        self.attack_power = 100
        self.movement = 600
        self.initial_movement = 600
        self.defense_power = 50