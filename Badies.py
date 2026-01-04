import random

import pygame

from Attack import show_popup, Attack
from Units.BaseUnit import BaseUnit, Teams
from Units.Spaces import SpaceTypes, closest_city_space, total_terrain_move_penalty, calculate_city_occupied, Plain


class BadieTypes:
    Ogre = "Ogre"


def spawn_ogre(board, screen):
    ogre_added = False
    space_counter = 0
    ogre_space = None
    ogre = None
    for space in board:
        if space_counter > 5:   # Prevent Ogre spawning too close to initial city
            rand_value = random.random()
            if rand_value > 0.95 and not space.units and not space.type in (SpaceTypes.CITY, SpaceTypes.RIVER):
                ogre = Ogre(space.x, space.y, Teams.ENEMY)
                space.add_unit(ogre)
                ogre_added = True
                ogre_space = space
                break
        else:
            space_counter += 1
    if not ogre_added:
        ogre_space = board[4]
        ogre = Ogre(ogre_space.x, ogre_space.y, Teams.ENEMY)
        ogre_space.add_unit(ogre)
    show_popup(screen, f"An Ogre is on the loose!!!")
    return ogre_space, ogre

def move_badies(move_nr, board, screen, ogre_space, ogre):
    if move_nr <= 1:
        return None, None
    if not ogre and move_nr == 2:
        ogre_space, ogre = spawn_ogre(board, screen)
    elif ogre:  # Move an existing Ogre
        ogre_space, ogre = move_badie(ogre_space, BadieTypes.Ogre, ogre, board)
    return ogre_space, ogre

def handle_potential_attack_for_badie(attacker_space, defender_space, unit, board):
    did_badie_move_forward = False
    if len(defender_space.units) > 0 and defender_space.units[0].team != unit.team:
        enemy = defender_space.units[0]
        defeated = Attack(unit, enemy, attacker_space, defender_space).execute()
        if defeated:
            defender_space.remove_unit(enemy)
    # Badie moves to barbarian horde space
    if len(defender_space.units) > 0 and defender_space.units[0].team == unit.team:
        defender_space.add_unit(unit)
        unit.position = defender_space.rect.center
        unit.rect.center = defender_space.rect.center
        did_badie_move_forward = True
    if len(defender_space.units) == 0 or defender_space.units[0].id == unit.id:
        defender_space.add_unit(unit)
        attacker_space.remove_unit(unit)
        unit.position = defender_space.rect.center
        unit.rect.center = defender_space.rect.center
        did_badie_move_forward = True
        if defender_space.type in [SpaceTypes.CITY]:
            new_space = Plain(defender_space.rect.centerx, defender_space.rect.centery)
            new_space.units = [unit]
            number_on_board = 0
            for space in board:
                if space.id == new_space.id:
                    break
                number_on_board += 1
            board[number_on_board] = new_space
    return did_badie_move_forward

def get_route_to_dest(source_space, dest_space, board, unit):
    # source_point = (source_space.rect.centerx, source_space.rect.centery)
    source_point = unit.position
    dest_point = (dest_space.rect.centerx, dest_space.rect.centery)
    spaces_en_route = []
    for space in board:
        if space.rect.clipline(source_point, dest_point) and source_space.id != space.id:
            spaces_en_route.append(space)
    reference_point = pygame.math.Vector2(source_space.rect.centerx,
                                          source_space.rect.centery)

    # Sort the list in-place by distance to the center of each rect
    spaces_en_route.sort(key=lambda obj: pygame.math.Vector2(obj.rect.center).distance_to(reference_point))
    return spaces_en_route

def move_badie(badie_space, badie_type, badie, board):
    if badie_type == BadieTypes.Ogre:
        target_city_space = closest_city_space(board, badie_space.x, badie_space.y)
        spaces_en_route_to_city = get_route_to_dest(badie_space, target_city_space, board, badie)
        # just move one space, then re-draw to show badie movement
        for space in spaces_en_route_to_city:
            if space.id == badie_space.id:
                continue
            if badie.movement >= space.move_penalty:
                badie.movement -= space.move_penalty
                if handle_potential_attack_for_badie(badie_space, space, badie, board):
                    badie_space = space
                break
            else:
                break
    return badie_space, badie

class Ogre(BaseUnit):
    def __init__(self, x, y, team):
        self.name = "Ogre"
        super().__init__(x, y, team)
        self.health = 300
        self.initial_health = 300
        self.can_shoot = False
        self.attack_power = 70
        self.movement = 450
        self.initial_movement = 450
        self.defense_power = 50