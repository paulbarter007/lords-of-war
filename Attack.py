import pygame
from sounds.Sounds import play_sound

pygame.init()
font = pygame.font.SysFont(None, 32)

def show_popup(screen, message, font=None):
    if not font:
        font = pygame.font.SysFont(None, 32)

    # Draw semi-transparent overlay
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with alpha
    screen.blit(overlay, (0, 0))

    # Draw popup rectangle
    popup_rect = pygame.Rect(0, 0, 1600, 200)
    popup_rect.center = screen.get_rect().center
    pygame.draw.rect(screen, (255, 255, 255), popup_rect)
    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)

    # Render message
    text_surface = font.render(message, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=popup_rect.center)
    screen.blit(text_surface, text_rect)

    pygame.display.update()

    # Wait for user to close popup
    waiting = True
    while waiting:
         for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                waiting = False

class Attack():
    def __init__(self, attacker, defender, source_space, attacked_space):
        self.attacker = attacker
        self.defender = defender
        self.attack_power = attacker.attack_power
        self.defense_power = defender.defense_power
        self.source_space = source_space
        self.attacked_space = attacked_space

    def calculate_damage(self, attack_power=None, defense_power=None):
        from Units.Spaces import SpaceTypes
        # Simple damage calculation: random percentage of attack power minus a percentage of the damage based on defense power
        # Eg: defence power of 50 means that 50% of the damage is reduced
        import random
        if self.attacked_space.type == SpaceTypes.CITY:
            # If attacking a city, the defender's defense power is doubled
            defense_power = self.defender.defense_power * 1.5
        if not attack_power:
            attack_power = self.attack_power
        if not defense_power:
            defense_power = self.defense_power
        damage = max(0, int(round(attack_power * random.random(), 0)))
        damage = damage - int(round(damage * round((defense_power / 100), 2), 0))
        if damage <= 0:
            damage = random.randint(1, 5)  # Ensure at least some damage is done
        return damage

    def execute(self):
        if self.defender.name == "Barbarian-horde" and not self.attacker.can_shoot:
            horde_inflicts_damage = self.calculate_damage(self.defender.attack_power,self.attacker.defense_power)
            self.attacker.health -= horde_inflicts_damage
            self.defender.play_attack_sound()
            if self.attacker.health <= 0:
                show_popup(pygame.display.get_surface(), f"{self.attacker.name} has been defeated by the Barbarian horde!", font)
                play_sound('sounds\\die.wav')
                self.source_space.remove_unit(self.attacker)
            else:
                show_popup(pygame.display.get_surface(), f"{self.attacker.name} takes {horde_inflicts_damage} damage from Barbarian horde!"
                                                     f" health left: {self.attacker.health}", font)
        damage = self.calculate_damage()
        self.defender.health -= damage
        self.attacker.movement = 0  # Attacker cannot move after attacking
        if self.defender.health <= 0:
            self.attacker.play_attack_sound()
            play_sound('sounds\\die.wav')
            show_popup(pygame.display.get_surface(), f"{self.defender.name} has been defeated!", font)
            return True  # Defender is defeated
        else:
            self.attacker.play_attack_sound()
            show_popup(pygame.display.get_surface(), f"{self.defender.name} takes {damage} damage!"
                                                     f" health left: {self.defender.health}", font)
            return False  # Defender survives