import pygame
import uuid

from Attack import Attack
from sounds.Sounds import play_sound

BLUE = (0, 0, 255)

class SpaceTypes:
    CITY = 0
    ROAD = 1
    FOREST = 2
    MOUNTAIN = 3
    RIVER = 4
    PLAIN = 5
    RUINS = 6
    BARBARIAN_VILLAGE = 7

class BaseSpace():
    def __init__(self, x, y, type):
        self.id = uuid.uuid4()
        self.x = x
        self.y = y
        self.owner = None  # The team that owns the space, if any
        self.units = []
        self.type = type
        self.rect = self.create_rect(x, y)
        self.move_penalty = 0
        self.is_invalid_hover = False
        self.is_valid_hover = False
        self.is_invalid_target = False
        self.is_invalid_target_in_range = False
        self.is_selected = False
        self.is_visible_by_barbarian = False
        self.is_visible_by_wolf = False
        self.is_temp_visible_by_wolf = False
        self.is_temp_visible_by_barbarian = False

    def to_dict(self):
        return {
            'id': str(self.id),
            'x': self.x,
            'y': self.y,
            'type': self.type,
            'name': getattr(self, 'name', None),
            'owner': self.owner.name if self.owner else None,
            'units': [unit.to_dict() for unit in self.units],
            'move_penalty': self.move_penalty
        }

    def get_unit_object_by_name(self, unit_name, x, y, team):
        from Units.BaseUnit import Soldier, Settler, Archer
        if unit_name == "Soldier":
            return Soldier(x, y, team)
        elif unit_name == "Settler":
            return Settler(x, y, team)
        elif unit_name == "Archer":
            return Archer(x, y, team)

    def from_dict(self, data, team_wolf, team_barbarian):
        self.id = uuid.UUID(data['id'])
        self.x = data['x']
        self.y = data['y']
        self.type = data['type']
        self.name = data.get('name', None)
        owner_name = data.get('owner', None)
        if owner_name:
            if owner_name == 'Wolf':
                self.owner = team_wolf
            else:
                self.owner = team_barbarian
        else:
            self.owner = None
        self.units = []
        for unit in data['units']:
            unit_object = self.get_unit_object_by_name(unit['name'], unit['position'][0], unit['position'][1], unit['team'])
            self.units.append(unit_object)
        self.move_penalty = data.get('move_penalty', 0)

    def get_info(self):
        return [f"Type: {self.name}"]

    def create_rect(self, x, y):
        image = pygame.image.load(f'images\\{self.name}.png').convert()
        image.convert()
        self.image = image
        rect = image.get_rect()
        rect.center = x, y
        return rect

    def add_unit(self, unit):
        self.units.append(unit)
        unit.position = (self.x, self.y)
        unit.rect.center = self.rect.center

    def remove_unit(self, unit_to_remove):
        new_units = []
        for unit in self.units:
            if unit.id == unit_to_remove.id:
                continue
            else:
                new_units.append(unit)
        self.units = new_units

    def draw_units(self, screen):
        for unit in self.units:
            unit.stacked = False  # Reset stacked state for all units
            unit.draw(screen)
        # only draw the first unit in the stack because that is the only unit available for selection
        if self.units and len(self.units) > 1:
            self.units[0].stacked = True
            self.units[0].draw(screen)

    def draw_target_effect(self, screen, valid_target=False, in_range=False):
        if valid_target:
            target_image = pygame.image.load(f'images\\target.png')
        else:
            if in_range:
                target_image = pygame.image.load(f'images\\target-invalid-in-range.png')
            else:
                target_image = pygame.image.load(f'images\\target-invalid.png')
        target_image.convert_alpha()
        overlay_rect = target_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        screen.blit(target_image, overlay_rect)

    def draw(self, screen, current_active_team, hovered_unit=None):
        from Teams import Teams
        screen.blit(self.image, self.rect)
        if self.type in [SpaceTypes.CITY, SpaceTypes.BARBARIAN_VILLAGE] and self.owner:
            self.draw_team_effect(screen)
        if current_active_team.type == Teams.WOLF:
            if not self.is_visible_by_wolf and not self.is_temp_visible_by_wolf:
                self.draw_invisible_effect(screen)
        if current_active_team.type == Teams.BARBARIAN:
            if not self.is_visible_by_barbarian and not self.is_temp_visible_by_barbarian:
                self.draw_invisible_effect(screen)
        if self.is_valid_hover:
            self.draw_valid_hovered_effect(screen)
        if self.is_selected:
            self.draw_selected_effect(screen)
        elif self.is_invalid_hover:
            self.draw_invalid_hovered_effect(screen)
        if self.is_invalid_target:
            self.draw_target_effect(screen, valid_target=False)
        elif self.is_invalid_target_in_range:
            self.draw_target_effect(screen, valid_target=False, in_range=True)


    def draw_selected_effect(self, screen):
        # Transparent highlight effect for selected unit:
        # highlight_color = (255, 0, 0, 100)  # RGBA: Yellow with 50% opacity
        # highlight_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        # highlight_surface.fill(highlight_color)
        # screen.blit(highlight_surface, self.rect)

        # Draw a border around the unit to indicate selection
        highlight_color = (255, 255, 0)  # Yellow
        border_thickness = 2
        pygame.draw.rect(screen, highlight_color, self.rect, border_thickness)

    def draw_valid_hovered_effect(self, screen):
        hover_image = pygame.image.load(f'images\\valid-hover.png')
        hover_image.convert_alpha()
        overlay_rect = hover_image.get_rect(topleft=self.rect.topleft)
        screen.blit(hover_image, overlay_rect)

    def draw_invalid_hovered_effect(self, screen):
        hover_image = pygame.image.load(f'images\\invalid-hover.png')
        hover_image.convert_alpha()
        overlay_rect = hover_image.get_rect(topleft=self.rect.topleft)
        screen.blit(hover_image, overlay_rect)

    def draw_team_effect(self, screen):
        team_img = None
        if self.owner.name == "Wolf":
            team_img = pygame.image.load(f'images\\units\\wolf-team.png')
        elif self.owner.name == "Barbarian":
            team_img = pygame.image.load(f'images\\units\\barbarian-team.png')
        team_img.convert_alpha()
        overlay_rect = team_img.get_rect(topright=self.rect.topright)
        screen.blit(team_img, overlay_rect)

    def draw_invisible_effect(self, screen):
        team_img = None
        team_img = pygame.image.load(f'images\\units\\smoke.png')
        team_img.convert_alpha()
        overlay_rect = team_img.get_rect(topright=self.rect.topright)
        screen.blit(team_img, overlay_rect)

    def get_hover_firing_image(self, enemy, valid):
        if enemy and valid:
            return pygame.image.load(f'images\\{self.name}-hover-enemy-firing.png').convert()
        if valid:
            return pygame.image.load(f'images\\{self.name}-hover-firing.png').convert()
        else:
            return pygame.image.load(f'images\\{self.name}-hover-invalid.png').convert()

    def get_hover_image(self):
        return pygame.image.load(f'images\\{self.name}-hover.png').convert()

    def get_moving_image_hover(self, valid, enemy):
        if not valid:
            return pygame.image.load(f'images\\{self.name}-hover-invalid.png').convert()
        if enemy:
            return pygame.image.load(f'images\\{self.name}-hover-enemy.png').convert()
        else:
            return pygame.image.load(f'images\\{self.name}-hover.png').convert()

    def get_owner_image(self, owner):
        if owner.name == 'Wolf':
            return pygame.image.load(f'images\\{self.name}-wolf.png').convert()
        elif owner.name == 'Barbarian':
            return pygame.image.load(f'images\\{self.name}-barbarian.png').convert()

    def get_regular_image(self):
        return pygame.image.load(f'images\\{self.name}.png').convert()

    def clone_space(self):
        if self.name == 'Plain':
            new_space = Plain(1, 2)
        elif self.name == 'Forest':
            new_space = Forest(1, 2)
        elif self.name == 'Mountain':
            new_space = Mountain(1, 2)
        elif self.name == 'River':
            new_space = River(1, 2)
        elif self.name == 'Road':
            new_space = Road(1, 2)
        elif self.name == 'City':
            new_space = City(1, 2)
            new_space.owner = self.owner
        elif self.name == 'Ruins':
            new_space = Ruins(1, 2)
            new_space.searched = False
        elif self.name == 'Barbarian-village':
            new_space = BarbarianVillage(1, 2)
        new_space.is_selected = True
        return new_space

class Plain(BaseSpace):
    def __init__(self, x, y):
        self.name = 'Plain'
        super().__init__(x, y, SpaceTypes.PLAIN)
        self.move_penalty = 150

class Road(BaseSpace):
    def __init__(self, x, y):
        self.name = 'Road'
        super().__init__(x, y, SpaceTypes.ROAD)
        self.move_penalty = 50
        self.owner = None

class Forest(BaseSpace):
    def __init__(self, x, y):
        self.name = 'Forest'
        super().__init__(x, y, SpaceTypes.FOREST)
        self.move_penalty = 300

class Mountain(BaseSpace):
    def __init__(self, x, y):
        self.name = 'Mountain'
        super().__init__(x, y, SpaceTypes.MOUNTAIN)
        self.move_penalty = 400

class City(BaseSpace):
    def __init__(self, x, y, owner=None):
        self.name = 'City'
        super().__init__(x, y, SpaceTypes.CITY)
        self.move_penalty = 50
        self.owner = owner  # The team that owns the city
        self.units = []  # Units stationed in the city
        self.population = 100

    def get_info(self):
        return [f"Type: {self.name}", f"Owner: {self.owner.name if self.owner else 'None'}", f"Population: {self.population}"]

class River(BaseSpace):
    def __init__(self, x, y):
        self.name = 'River'
        super().__init__(x, y, SpaceTypes.RIVER)
        self.move_penalty = 99999

class Ruins(BaseSpace):
    def __init__(self, x, y):
        self.name = 'Ruins'
        super().__init__(x, y, SpaceTypes.RUINS)
        self.move_penalty = 150
        self.searched = False

    def draw(self, screen, current_active_team, hovered_unit=None):
        from Teams import Teams
        super().draw(screen, current_active_team)
        if (not self.searched and
                ((current_active_team.type == Teams.WOLF and (self.is_visible_by_wolf or self.is_temp_visible_by_wolf)) or
                 (current_active_team.type == Teams.BARBARIAN and (self.is_visible_by_barbarian or self.is_temp_visible_by_barbarian)))):
            ruins_image = pygame.image.load(f'images\\ruins-magic.png')
            ruins_image.set_alpha(130)
            overlay_rect = ruins_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
            screen.blit(ruins_image, overlay_rect)

    def search(self):
        play_sound("sounds\\ruins.wav")
        self.searched = True

class BarbarianVillage(BaseSpace):
    def __init__(self, x, y):
        self.name = 'Barbarian-village'
        super().__init__(x, y, SpaceTypes.BARBARIAN_VILLAGE)
        self.move_penalty = 50
        self.owner = None

def calculate_city_occupied(active_team, inactive_team, city):
    if city.owner and city.owner != active_team:
        active_team.owned_cities.append(city)
        inactive_team.owned_cities.remove(city)
    elif not city.owner:
        active_team.owned_cities.append(city)
    city.owner = active_team

def get_current_active_unit(screen, active_team, x, y, board):
    from Teams import Teams
    active_unit = None
    active_space = None
    unit_stack = []
    get_bottom_of_stack = False
    for space in board:
        if ((active_team.type == Teams.WOLF and (space.is_visible_by_wolf or space.is_temp_visible_by_wolf)) or
                (active_team.type == Teams.BARBARIAN and (space.is_visible_by_barbarian or space.is_temp_visible_by_barbarian))):
            if space.rect.collidepoint(x, y):
                active_space = space
            for unit in space.units:
                # check that the mouse is hovering over the unit within the space
                if unit.rect.collidepoint(x, y) and unit.team == active_team.type:
                    active_unit = unit
                    if len(space.units) > 1:
                        for unit in space.units:
                            unit.stacked = True
                        unit_stack = space.units
                        if unit.stack_clicked:  # allow one click in the stack before changing the order
                            # If the previously active unit is the same as the current unit, get bottom unit, to allow selecting different unit
                            get_bottom_of_stack = True
                            unit.stack_clicked = False
                            break
                        else:
                            unit.stack_clicked = True
                            break
                    else:
                        # If the unit is found, return the unit
                        active_unit = unit
                        unit.stacked = False
                        break
    if get_bottom_of_stack:
        # start with last element
        new_stack = [unit_stack[len(unit_stack)-1]]
        count = 0
        for unit in unit_stack:
            new_stack.append(unit)
            count += 1
        # shave off the last element because it was added twice
        new_stack = new_stack[:-1]  # Reverse the stack to have the bottom unit first
        active_space.units = new_stack
        unit_stack = new_stack
        active_unit = new_stack[0]
        active_unit.draw_stacked_effect(screen) # dont draw here just set property to stacked!
    if active_unit:
        active_unit.is_selected = True
    if active_space:
        active_space.is_selected = True
    return active_unit, active_space, unit_stack

def remove_units_selected(board):
    for space in board:
        for unit in space.units:
            unit.is_selected = False

def remove_units_hovered(board):
    for space in board:
        for unit in space.units:
            unit.is_hovered = False

def restore_movement_units(board, active_team):
    for space in board:
        for unit in space.units:
            if unit.team == active_team.type:
                unit.movement = unit.initial_movement  # Reset movement for the unit

def shoot_at_space(board, unit, mouse_position):
    if unit.movement <= 0 or not unit.can_shoot:
        return
    for space in board:
        if space.rect.collidepoint(mouse_position):
            if len(space.units) > 0 and space.units[0].team != unit.team:
                unit.movement = 0  # Reset movement after firing
                defeated = Attack(unit, space.units[0], None, space).execute()
                if defeated:
                    space.remove_unit(space.units[0])

def snap_to_space(screen, active_team, inactive_team, board, possible_dest_spaces, unit, dragged_from_space: BaseSpace):
    from Teams import Teams
    for space in board:
        if (abs(unit.rect.centerx - space.rect.centerx) < 45) and (abs(unit.rect.centery - space.rect.centery) < 45):
            unit.rect.center = space.rect.center
            if space.id in possible_dest_spaces:
                centre_active_space = (dragged_from_space.rect.centerx, dragged_from_space.rect.centery)
                centre_current_space = (space.rect.centerx, space.rect.centery)
                unit.movement -= total_terrain_move_penalty(space, unit, centre_active_space, centre_current_space, board)
                if len(space.units) > 0 and space.units[0].team != unit.team:
                    enemy = space.units[0]
                    defeated = Attack(unit, enemy, dragged_from_space, space).execute()
                    if defeated:
                        space.remove_unit(enemy)
                        space.add_unit(unit)
                    else:
                        # If the attack did not defeat the defender, snap back to next to attacker
                        snap_back_to_start(unit, dragged_from_space, space, possible_dest_spaces, board)
                        break
                else:
                    space.add_unit(unit)
                    if active_team.type == Teams.WOLF:
                        space.is_visible_by_wolf = True
                    elif active_team.type == Teams.BARBARIAN:
                        space.is_visible_by_barbarian = True
                    unit.position = space.rect.center
                    unit.rect.center = space.rect.center
                if space.type in [SpaceTypes.CITY, SpaceTypes.BARBARIAN_VILLAGE]:
                    calculate_city_occupied(active_team, inactive_team, space)
                dragged_from_space.remove_unit(unit)
            break

def snap_back_to_start(current_active_unit, dragged_from_space, attacked_space, possible_dest_space_ids, board, out_of_moves=False):
    if out_of_moves:
        current_active_unit.rect.center = dragged_from_space.rect.center
        return
    if is_space_adjacent(dragged_from_space, attacked_space):
        current_active_unit.rect.center = dragged_from_space.rect.center
        return
    for space in board:
        if space.id != attacked_space.id:
            if is_space_adjacent(space, attacked_space):
                current_active_unit.rect.center = space.rect.center
                return

def is_space_adjacent(space1, space2):
    # bug here when go from corner to corner to corner
    centre_space1 = (space1.rect.centerx, space1.rect.centery)
    centre_space2 = (space2.rect.centerx, space2.rect.centery)
    distance = pygame.math.Vector2(centre_space1).distance_to(centre_space2)
    return distance < 110  # Assuming spaces are close enough if within 100 pixels

def total_terrain_move_penalty(current_space, unit, start_point, end_point, board):
    # Calculate the move penalty based on the terrain type between two points
    total_move_penalty = 0
    for space in board:
        if space.rect.clipline(start_point, end_point): # and space.id != current_space.id:
            if unit.fly:
                total_move_penalty += 50
            else:
                total_move_penalty += space.move_penalty
    return total_move_penalty

def remove_hover_effects(board):
    # remove space hovers for movement and unit hovers for targets
    for space in board:
        space.is_valid_hover = False
        space.is_invalid_hover = False
        space.is_invalid_target = False
        space.is_invalid_target_in_range = False
        space.is_selected = False
        for unit in space.units:
            unit.is_valid_target = False
            unit.is_invalid_target = False
            unit.selected = False

def handle_hover(board, screen, current_active_unit, active_space, event, firing, current_active_team):
    remove_hover_effects(board)
    current_hovered_space = possible_dest_space_ids = None
    if current_active_unit and active_space:
        if not firing:
            current_active_unit.rect.move_ip(event.rel)
        current_hovered_space, possible_dest_space_ids = hover_space(board, screen, current_active_unit,
                                                                         active_space,
                                                                         event.pos[0], event.pos[1], current_active_team, firing=firing)
    return current_hovered_space, possible_dest_space_ids

def check_hover_unit(active_team, screen, board, mouse_position, firing=False):
    for space in board:
        for unit in space.units:
            if unit.rect.collidepoint(mouse_position) and unit.team == active_team.type:
                if firing and not unit.can_shoot:
                    continue
                if not unit.is_hovered:
                    unit.is_hovered = True
                return unit

def handle_move(distance, unit, centre_active_space, centre_current_space, space, screen, board, current_active_team):
    possible_dest_space_ids = set()
    terrain_penalty = total_terrain_move_penalty(space, unit, centre_active_space, centre_current_space, board)
    space.draw(screen, current_active_team)
    if unit.movement >= terrain_penalty:
        enemy = None
        if space.units and space.units[0].team != unit.team:
            enemy = space.units[0]
        space.is_valid_hover = True
        possible_dest_space_ids.add(space.id)
    else:
        space.is_invalid_hover = True
    return list(possible_dest_space_ids)

def handle_shoot(distance, unit, centre_active_space, centre_current_space, space, screen, board, current_active_team):
    space.draw(screen, current_active_team)
    possible_dest_shooting_ids = set()
    if distance <= (unit.range):
        if space.units and space.units[0].team != unit.team:
            enemy = space.units[0]
            if unit.movement > 0:
                possible_dest_shooting_ids.add(space.id)
                enemy.is_valid_target = True
            else:
                enemy.is_invalid_target = True
        else:
            space.is_invalid_target_in_range = True
    else:
        space.is_invalid_target = True
        if space.units and space.units[0].team != unit.team:
            enemy = space.units[0]
            enemy.is_invalid_target = True
    return list(possible_dest_shooting_ids)

def hover_space(board, screen, unit, active_space, x, y, current_active_team, firing=False):
    # Manage moving and shooting
    for space in board:
        if space.rect.collidepoint(x, y) and space.id != active_space.id:
            centre_active_space = (active_space.rect.centerx, active_space.rect.centery)
            centre_current_space = (space.rect.centerx, space.rect.centery)
            distance = pygame.math.Vector2(centre_active_space).distance_to(centre_current_space)
            if firing:
                return space, handle_shoot(distance, unit, centre_active_space, centre_current_space, space, screen, board,
                                           current_active_team)
            else:
                return space, handle_move(distance, unit, centre_active_space, centre_current_space, space, screen, board,
                                          current_active_team)

    return None, []

