import pygame
import uuid

from sounds.Sounds import play_sound

BLUE = (0, 0, 255)

# duplicated class to avoid circular import issues
class Teams():
    WOLF = 1
    BARBARIAN = 2
    ENEMY = 3

class BaseUnit():
    def __init__(self, x, y, team):
        self.team = team
        if team == Teams.WOLF:
            self.team_name = "Wolf"
        elif team == Teams.BARBARIAN:
            self.team_name = "Barbarian"
        self.type = 'RegularUnit'
        self.id = uuid.uuid4()
        self.can_shoot = False
        self.range = 0
        self.health = 20
        self.initial_health = 20
        self.fly = False
        self.attack_power = 10
        self.defense_power = 5
        self.movement = 250
        self.initial_movement = 250
        self.position = (x, y)
        self.image = None
        self.rect = self.create_rect()
        self.stacked = False
        self.stack_clicked = False
        self.is_selected = False
        self.is_hovered = False
        self.is_valid_target = False
        self.is_invalid_target = False
        self.has_speed_potion = False
        self.has_bloodlust = False
        self.has_spell = False

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "team": self.team,
            "health": self.health,
            "can_shoot": self.can_shoot,
            "range": self.range,
            "fly": self.fly,
            "attack_power": self.attack_power,
            "defense_power": self.defense_power,
            "movement": self.movement,
            "initial_movement": self.initial_movement,
            "position": self.position
        }

    def from_dict(self, data):
        self.id = uuid.UUID(data["id"])
        self.name = data["name"]
        self.team = data["team"]
        self.health = data["health"]
        self.can_shoot = data["can_shoot"]
        self.range = data["range"]
        self.fly = data["fly"]
        self.attack_power = data["attack_power"]
        self.defense_power = data["defense_power"]
        self.movement = data["movement"]
        self.initial_movement = data["initial_movement"]
        self.position = tuple(data["position"])
        self.rect = self.create_rect()

    def play_attack_sound(self):
        play_sound(f'sounds\\{self.name}.wav')

    def clone_unit(self):
        from Units.Units import Wolf, Barbarian, Settler, Archer, BarbarianHero, WolfHero, BarbarianHorde, Bats, Knight, Spearman
        if self.name == 'Wolf':
            new_unit = Wolf(self.position[0], self.position[1], self.team)
        elif self.name == 'Barbarian':
            new_unit = Barbarian(self.position[0], self.position[1], self.team)
        elif self.name == 'Settler':
            new_unit = Settler(self.position[0], self.position[1], self.team)
        elif self.name == 'Archer':
            new_unit = Archer(self.position[0], self.position[1], self.team)
        elif self.name == 'barbarian-hero':
            new_unit = BarbarianHero(self.position[0], self.position[1], self.team)
        elif self.name == 'wolf-hero':
            new_unit = WolfHero(self.position[0], self.position[1], self.team)
        elif self.name == 'barbarian-horde':
            new_unit = BarbarianHorde(self.position[0], self.position[1], self.team)
        elif self.name == 'Bats':
            new_unit = Bats(self.position[0], self.position[1], self.team)
        elif self.name == 'Knight':
            new_unit = Knight(self.position[0], self.position[1], self.team)
        elif self.name == 'Spearman':
            new_unit = Spearman(self.position[0], self.position[1], self.team)
        new_unit.selected = True
        new_unit.stacked = False
        return new_unit

    def get_info(self, unit_stack):
        unit_stack_label = ""
        if unit_stack:
            unit_stack_label = [unit.name + "," for unit in unit_stack]
        return [f"Name: {self.name}", f"Team: {self.team_name}", f"Health: {self.health}, " \
               f"Attack Power: {self.attack_power}", f"Defense Power: {self.defense_power}, " \
               f"Movement: {self.movement}", f"Unit Stack: {unit_stack_label}"]

    def draw_hovered_effect(self, screen):
        highlight_color = (255, 255, 0, 128)  # RGBA: Yellow with 50% opacity
        highlight_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        highlight_surface.fill(highlight_color)
        screen.blit(highlight_surface, self.rect)

    def draw_damaged_effect(self, screen):
        # Transparent highlight effect for selected unit:
        highlight_color = (255, 0, 0, 100)  # RGBA: Red with 50% opacity
        highlight_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        highlight_surface.fill(highlight_color)
        screen.blit(highlight_surface, self.rect)

    def draw_selected_effect(self, screen):
        # Draw a border around the unit to indicate selection
        highlight_color = (255, 255, 0)  # Yellow
        border_thickness = 2
        pygame.draw.rect(screen, highlight_color, self.rect, border_thickness)

    def draw_stacked_effect(self, screen):
        overlay_image = pygame.image.load("images\\units\\stack.png").convert_alpha()  # Replace with your overlay image
        overlay_rect = overlay_image.get_rect(topleft=self.rect.topleft)
        screen.blit(overlay_image, overlay_rect)

    def draw_team_effect(self, screen):
        team_img = None
        if self.team == Teams.WOLF:
            team_img = pygame.image.load(f'images\\units\\wolf-team.png')
        elif self.team == Teams.BARBARIAN:
            team_img = pygame.image.load(f'images\\units\\barbarian-team.png')
        elif self.team == Teams.ENEMY:
            team_img = pygame.image.load(f'images\\units\\enemy-team.png')
        team_img.convert_alpha()
        overlay_rect = team_img.get_rect(topright=self.rect.topright)
        screen.blit(team_img, overlay_rect)

    def draw_target_effect(self, screen, valid_target=False):
        if valid_target:
            target_image = pygame.image.load(f'images\\target.png')
        else:
            target_image = pygame.image.load(f'images\\target-invalid.png')
        target_image.convert_alpha()
        overlay_rect = target_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        screen.blit(target_image, overlay_rect)

    def draw_spell_effect(self, screen, type=""):
        spell_effect_image = pygame.image.load(f'images\\units\\{type}-potion.png')
        spell_effect_image.convert_alpha()
        overlay_rect = spell_effect_image.get_rect(centerx=self.rect.centerx, centery=self.rect.centery)
        screen.blit(spell_effect_image, overlay_rect)

    def draw(self, screen, hovered_unit=None):
        screen.blit(self.image, self.rect)
        if hovered_unit:
            self.draw_hovered_effect(screen)
        if self.stacked:
            self.draw_stacked_effect(screen)
        if self.is_valid_target:
            self.draw_target_effect(screen, valid_target=True)
        elif self.is_invalid_target:
            self.draw_target_effect(screen, valid_target=False)
        if self.is_selected:
            self.draw_selected_effect(screen)
        elif self.is_hovered:
            self.draw_hovered_effect(screen)
        if self.has_speed_potion:
            self.draw_spell_effect(screen, 'speed')
        elif self.has_bloodlust:
            self.draw_spell_effect(screen, 'bloodlust')
        if (self.health / self.initial_health) < 0.2:
            self.draw_damaged_effect(screen)
        self.draw_team_effect(screen)

    def create_rect(self, img=None):
        if img is None:
            base_img = pygame.image.load(f'images\\units\\{self.name}.png').convert()
        self.image = base_img
        # Draw rectangle around the image
        rect = base_img.get_rect()
        rect.center = self.position
        return rect

    def get_target_image(self):
        if self.team == Teams.WOLF:
            return pygame.image.load(f'images\\units\\{self.name}-wolf-hover-firing.png')
        elif self.team == Teams.BARBARIAN:
            return pygame.image.load(f'images\\units\\{self.name}-barbarian-hover-firing.png')
