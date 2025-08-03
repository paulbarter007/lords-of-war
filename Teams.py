from Units.Spaces import SpaceTypes

GOLD_PER_CITY = 1
RESOURCES_PER_CITY = 2
RESOURCES_PER_BARBARIAN_VILLAGE = 1
GOLD_FOR_SETTLER = 5

class Teams():
    WOLF = 1
    BARBARIAN = 2

class BaseTeam():
    def __init__(self):
        self.name = ""
        self.points = 0
        self.turn_nr = 0
        self.owned_cities = []
        self.total_gold = 0
        self.total_resources = 0
        self.researched_roads = False
        self.researched_archery = False
        self.researched_knight = False
        self.researched_speed_spell = False
        self.researched_bloodlust_spell = False
        self.researched_spearman = False

    def to_dict(self):
        return {
            'name': self.name,
            'points': self.points,
            'turn_nr': self.turn_nr,
            'owned_cities': [city.to_dict() for city in self.owned_cities],
            'total_gold': self.total_gold,
            'total_resources': self.total_resources
        }

    def from_dict(self, data):
        from Units.Spaces import City
        self.name = data['name']
        self.points = data['points']
        self.turn_nr = data['turn_nr']
        self.owned_cities = []
        for city in data['owned_cities']:
            space = City(1, 2)
            space.from_dict(city, None, None)
            self.owned_cities.append(space)
        self.total_gold = data['total_gold']
        self.total_resources = data['total_resources']

    def calculate_resources(self):
        # TODO - add for farms etc... create city class
        total_cities_owned = len([city for city in self.owned_cities if city.type == SpaceTypes.CITY])
        total_barbarian_villages_owned = len([city for city in self.owned_cities if city.type == SpaceTypes.BARBARIAN_VILLAGE])
        self.total_gold += (GOLD_PER_CITY * total_cities_owned)
        self.total_resources += (RESOURCES_PER_CITY * total_cities_owned) + (RESOURCES_PER_BARBARIAN_VILLAGE * total_barbarian_villages_owned)

    def buy_unit(self, city, new_unit):
        if self.total_gold >= new_unit.gold_cost:
            self.total_gold -= new_unit.gold_cost
            city.add_unit(new_unit)

    def get_info(self):
        return [f"Name: {self.name}", f"Points: {self.points}", f"Turn: {self.turn_nr}",
                f"Gold: {self.total_gold}, Resources: {self.total_resources}"]

class WolfTeam(BaseTeam):
    def __init__(self):
        super().__init__()
        self.name = "Wolf"
        self.type = Teams.WOLF

class BarbarianTeam(BaseTeam):
    def __init__(self):
        super().__init__()
        self.name = "Barbarian"
        self.type = Teams.BARBARIAN

team_wolf = WolfTeam()
team_barbarian = BarbarianTeam()