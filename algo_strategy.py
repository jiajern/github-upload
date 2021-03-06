import gamelib
import random
import math
from sys import maxsize


"""
You are able to implement your own algo by subclassing the `AlgoCore` class and
overriding the methods `process_config(config_string)` and `step(game_map)`.
Most of the algo code you write will be in this file unless you create new
modules yourself.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def process_config(self, config):
        """ Tweak strategy based on config and perform any initial algo setup """
        gamelib.debug_write('Configuring your custom algo strategy...')

        self.config = config

    def step(self, game_map):
        """
        This step function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_map.turn_number))

        self.starter_strategy(game_map)  # replace with your own strategy

        game_map.send_messages()

    # NOTE: all the methods after this point are part of the sample funnel strategy
    def starter_strategy(self, game_map):
        first_turn = game_map.turn_number == 0
        if first_turn:
            self.turn_one_defences(game_map)
        else:
            self.build_defences(game_map)
            self.deploy_attackers(game_map)

    #On turn one, we make the C1 Logo!
    def turn_one_defences(self, game_map):
        #Deploy FF creating a V shape
        tower_locations = [[0, 13], [1, 13], [2,13], [3, 13], [4, 13], [5, 13],
                           [22, 13], [23, 13], [24, 13], [25, 13], [26, 13], [27, 13],
                           [6, 12], [7, 11], [8, 10], [9, 9], [10, 8], [11, 7], [12, 6],
                           [21, 12], [20, 11], [19, 10], [18, 9], [17, 8], [16, 7]]
        game_map.attempt_spawn_multiple("FF", tower_locations)

        #Deploy DF at the vertex of V
        tower_locations = [[11, 6], [16, 6]]
        game_map.attempt_spawn_multiple("DF", tower_locations)
        self.deploy_attackers(game_map)

    def build_defences(self, game_map):
        #Choose to spend a random amount of cores
        starting_cores = game_map.get_resource('cores')
        '''cores_to_spend = random.randint(0, math.floor(starting_cores))'''

        #Get all locations on the bottom half of the map
        '''all_locations = [[0, 0]]
        for i in range(game_map.arena_size):
            for j in range(math.floor(game_map.arena_size / 2)):
                all_locations.append([i, j])
        possible_locations = game_map.filter_blocked_locations(all_locations)'''
        all_v_location =[[0, 13], [1, 13], [2,13], [3, 13], [4, 13], [5, 13],
                         [22, 13], [23, 13], [24, 13], [25, 13], [26, 13], [27, 13],
                         [6, 12], [7, 11], [8, 10], [9, 9], [10, 8], [11, 7], [12, 6],
                         [21, 12], [20, 11], [19, 10], [18, 9], [17, 8], [16, 7], [15, 6]]
        possible_v_location = game_map.filter_blocked_locations(all_v_location)
        needed_v = len(possible_v_location)
        cores_needed = needed_v * 1.5
        while cores_needed > starting_cores:
            needed_v -= 1
            cores_needed -= 1.5
        game_map.attempt_spawn_multiple("FF", possible_v_location[0:needed_v])
        starting_cores -= cores_needed

        all_df_location = [[11,6], [11,5], [10,7], [9,8], [8,9], [7,10], [6, 11],
                           [16, 6], [16, 5], [17, 7], [18, 8], [19, 9], [20, 10], [21, 11]]
        all_ef_location = [[10,6], [10,5], [9,7], [8,8], [7,9], [6,10], [5, 11]
                           [17, 6], [17, 5], [18, 7], [19, 8], [20, 9], [21, 10], [22, 11]]
        all_df_location = game_map.filter_blocked_locations(all_df_location)
        all_ef_location = game_map.filter_blocked_locations(all_ef_location)




        #While we still want to spend more cores, build a random firewall
        while starting_cores >= 6 and (len(all_df_location) > 0 or len(all_ef_location) > 0):
            '''location_index = random.randint(0, len(possible_locations) - 1)
            build_location = possible_locations[location_index]
            possible_locations.remove(build_location)'''

            firewall_number = random.randint(1, 2)
            if firewall_number == 1 or starting_cores < 8:
                location_index = random.randint(0, len(all_df_location) - 1)
                build_location = all_df_location[location_index]
                all_df_location.remove(build_location)
                starting_cores -= 6
                firewall_to_build = "DF"
            else:
                location_index = random.randint(0, len(all_ef_location) - 1)
                build_location = all_ef_location[location_index]
                all_ef_location.remove(build_location)
                starting_cores -= 8
                firewall_to_build = "EF"

            game_map.attempt_spawn(firewall_to_build, build_location)

        all_locations = [[0, 0]]
        for i in range(game_map.arena_size):
            for j in range(math.floor(game_map.arena_size / 2)):
                all_locations.append([i, j])
        possible_locations = game_map.filter_blocked_locations(all_locations)
        while starting_cores >= 1.5 and len(possible_locations) > 0:
            location_index = random.randint(0, len(possible_locations) - 1)
            build_location = possible_locations[location_index]
            possible_locations.remove(build_location)
            starting_cores -= 1.5
            firewall_to_build = "FF"
            game_map.attempt_spawn(firewall_to_build, build_location)

    def deploy_attackers(self, game_map):
        #Get some variebles we will use
        starting_bits = game_map.get_resource('bits')
        bits_to_spend = random.randint(0, math.floor(starting_bits))
        enemy_bits = game_map.get_resource('bits', 1)
        current_health = game_map.my_integrity
        enemy_health = game_map.enemy_integrity
        friendly_edges = game_map.get_edge_locations("bottom_left") + game_map.get_edge_locations("bottom_right")
        deploy_locations = game_map.filter_blocked_locations(friendly_edges)

        #While we still want to spend more bits, deploy a random information unit
        while bits_to_spend >= 1 and len(deploy_locations) > 0:
            ping_value = 1
            scrambler_value = 1
            emp_value = 1

            #Stop if values were set below zero
            if ping_value + scrambler_value + emp_value < 1:
                break

            #Choose a random deploy location
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            #Adjust weights slightly based on game state
            if enemy_health <= 5:
                ping_value *= 2

            if enemy_bits > starting_bits or current_health <= 5:
                scrambler_value *= 2
            if bits_to_spend < 3:
                emp_value = 0

            #Choose a random unit based on weights, higher weights are more likely to be chosen
            total_value = ping_value + scrambler_value + emp_value
            choice = random.randint(1, total_value)

            if choice <= ping_value:
                bits_to_spend -= 1
                unit_to_spawn = "PI"
            elif choice <= ping_value + scrambler_value:
                bits_to_spend -= 1
                unit_to_spawn = "SI"
            else:
                bits_to_spend -= 3
                unit_to_spawn = "EI"

            game_map.attempt_spawn(unit_to_spawn, deploy_location)

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
