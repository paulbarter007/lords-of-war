from Attack import show_popup
from Teams import BaseTeam, WolfTeam, BarbarianTeam
from Units.Spaces import restore_movement_units, Plain, City, Mountain, Forest, Road, River
import random
import pygame
import json
import datetime

from Units.Units import Bats
from sounds.Sounds import play_sound

pygame.init()
font = pygame.font.SysFont(None, 32)

def save_game(board, current_active_team, team_wolf, team_barbarian):
    import json
    game_data = {
        'board': [space.to_dict() for space in board],
        'current_active_team': current_active_team.name,
        'team_wolf': team_wolf.to_dict(),
        'team_barbarian': team_barbarian.to_dict()
    }
    with open(f"saved_games\\{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_game.json", "w") as f:
        json.dump(game_data, f)
    show_popup(pygame.display.get_surface(), "Game saved successfully!", font)

def get_space_object_by_name(space_name, x, y):
    if space_name == "Plain":
        return Plain(x, y)
    elif space_name == "City":
        return City(x, y)
    elif space_name == "Mountain":
        return Mountain(x, y)
    elif space_name == "Forest":
        return Forest(x, y)
    elif space_name == "Road":
        return Road(x, y)
    elif space_name == "River":
        return River(x, y)

def load_game(file_path):
    with open(file_path, "r") as f:
        game_data = json.load(f)
    active_team_name = game_data['current_active_team']
    team_wolf = WolfTeam()
    team_wolf.from_dict(game_data['team_wolf'])
    team_barbarian = BarbarianTeam()
    team_barbarian.from_dict(game_data['team_barbarian'])
    if active_team_name == "Wolf":
        current_active_team = team_wolf
    else:
        current_active_team = team_barbarian
    board = []
    for space_data in game_data['board']:
        space = get_space_object_by_name(space_data['name'], space_data['x'], space_data['y'])
        space.from_dict(space_data, team_wolf, team_barbarian)
        board.append(space)
    return board, current_active_team, team_wolf, team_barbarian

def handle_end_turn(board, screen, current_active_team, moving, current_active_unit, active_space,
                                possible_dest_space_ids, team_wolf, team_barbarian):
    from Screens import clear_all_temp_visibility
    restore_movement_units(board, current_active_team)
    current_active_team = team_barbarian if current_active_team.name == 'Wolf' else team_wolf
    moving = False
    current_active_unit = None
    active_space = None
    possible_dest_space_ids = []
    if current_active_team.name == 'Wolf':
        team_wolf.turn_nr += 1
    else:
        team_barbarian.turn_nr += 1
    current_active_team.calculate_resources()
    handle_random_event(current_active_team, screen, team_wolf, team_barbarian, board)
    clear_all_temp_visibility(board)
    return current_active_team, moving, current_active_unit, active_space, possible_dest_space_ids, team_wolf, team_barbarian

def increase_random_unit_attack_strength(team, board):
    for space in board:
        if space.units:
            random_unit = random.choice(space.units)
            if random_unit.team == team.type and random_unit.name != 'Settler':
                random_unit.attack_power += 50
                return random_unit

def get_random_text(type):
    if type == 'gold':
        return random.choice(random_gaining_gold_events)
    elif type == 'resources':
        return random.choice(random_gaining_resource_events)
    elif type == 'lose_health':
        return random.choice(random_lose_health_events)
    else:
        return "Unknown event type"

random_gaining_gold_events = ['You discover gold in an old city!', 'You find a hidden treasure chest!',
                              'You earn gold trading with natives!']
random_gaining_resource_events = ['You find a rich resource deposit!', 'A new trade route opens gaining resources']
random_lose_health_events = ['You battle a dragon and are injured!', 'You walk into a poison dart trap!']

def handle_random_event(current_active_team, screen, team_wolf, team_barbarian, board):
    if current_active_team.name == 'Wolf':
        # End of barbarian's turn is end of both turns
        random_choice = random.randint(1, 10)
        if random_choice > 6:
            play_sound('sounds\\random_event.mp3')
            random_team = random.randint(1, 2)
            event_team = team_wolf if random_team == 1 else team_barbarian
            random_event = random.randint(1, 3)
            if random_event == 1:
                inc_gold = random.randint(1, 5)
                event_team.total_gold += 5
                show_popup(screen, f"{event_team.name}: {get_random_text('gold')}! Gain {inc_gold} Gold!", font)
            elif random_event == 2:
                inc_resources = random.randint(1, 5)
                show_popup(screen, f"{event_team.name}: {get_random_text('resources')}! Gain {inc_resources} Resources!", font)
                event_team.total_resources += 5
            else:
                random_unit = increase_random_unit_attack_strength(event_team, board)
                if random_unit:
                    show_popup(screen, f"{event_team.name}: {random_unit.name} has levelled up and gains 50 attack strength!", font)
                else:
                    show_popup(screen, f"{event_team.name}: Nothing happens", font)

def handle_ruins_searched(space, current_active_team, screen, hero):
    random_choice = random.randint(1, 6)
    if random_choice == 1:
        inc_gold = random.randint(1, 5)
        current_active_team.total_gold += inc_gold
        show_popup(screen, f"You discover {inc_gold} gold in the ruins!", font)
    elif random_choice == 2:
        inc_resources = random.randint(1, 5)
        current_active_team.total_resources += inc_resources
        show_popup(screen, f"You discover {inc_resources} resources in the ruins!", font)
    elif random_choice == 3:
        hero.attack_power += 50
        show_popup(screen, f"Your hero has levelled up and gains 50 attack strength!", font)
    elif random_choice == 4:
        lose_health = random.randint(1, 30)
        hero.health -= lose_health
        show_popup(screen, f"{get_random_text('lose_health')}. You lose {lose_health} health.", font)
        if hero.health <= 0:
            space.remove_unit(space.units[0])
            show_popup(screen, f"Your hero has been slain!", font)
            play_sound('sounds\\die.wav')
    elif random_choice == 5:
        bats = Bats(space.rect.centerx, space.rect.centery, current_active_team.type)
        space.add_unit(bats)
        play_sound("sounds\\scary.wav")
        show_popup(screen, f"A flock of vampire bats joins you!", font)
    else:
        play_sound("sounds\\wrong-answer.wav")
        show_popup(screen, f"You find nothing in the ruins.", font)

def get_space_unit_is_in(board, unit):
    for space in board:
        if unit in space.units:
            return space
    return None