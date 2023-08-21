from source.tool import Control
import os
import pickle

HUMAN_DATA_SAVE_PATH = './human_data.pkl'


def save_state(controller: Control, print_language_form: bool = False) -> None:
    r"""
    Overview:
        Given the controller object, add the current state to ``HUMAN_DATA_SAVE_PATH``
    Arguments:
        controller: the given controller object.
        print_language_form: whether to print the language description about this frame.
    """
    if os.path.exists(HUMAN_DATA_SAVE_PATH):
        with open(HUMAN_DATA_SAVE_PATH, 'rb') as f:
            data = pickle.load(f)
    else:
        data = []
    new_frame = state2dict(controller)
    data.append(new_frame)
    with open(HUMAN_DATA_SAVE_PATH, 'wb') as f:
        pickle.dump(data, f)
    if print_language_form:
        print(dict2language(new_frame))


def state2dict(controller: Control) -> dict:
    r"""
    Overview:
        Given the controller object, convert the game state into dict form.
    Arguments:
        controller: the given controller object.
    Returns:
        total_info: a dict containing the state info.
    """
    state = controller.state
    plant_map = state.map.map

    # The map containing information related to plant.
    reduced_plant_map = []
    for line in range(len(plant_map)):
        reduced_plant_map.append([])
        for row in range(len(plant_map[0])):
            plot_info = plant_map[line][row]
            plants = list(plot_info['plantnames'])

            # Information related to plant has two keys.
            # ``plot_type`` means the type of this grid, e.g. grass, water
            # ``plants`` means the plants in this grid.
            reduced_plant_map[line].append({
                'plot_type': plot_info['plot_type'],
                'plants': plants
            })

    # The map containing information related to zombie.
    zombie_list = state.zombie_groups
    # Init zombie map.
    zombie_map = []
    for line in range(len(plant_map)):
        zombie_map.append([])
        for row in range(len(plant_map[0])):
            zombie_map[line].append([])

    for line_id, line in enumerate(zombie_list):
        for zombie, zombie_place in line.spritedict.items():
            zombie_point = zombie_place.midleft
            grid_idx = state.map.getMapIndex(zombie_point[0], zombie_point[1])

            # Information related to zombie has three keys.
            # ``name`` means the type of this zombie, e.g. NormalZombie
            # ``speed`` means the moving speed of this zombie. This can be affected by plants.
            # ``health`` means the total health of this zombie (helmet + normal_health)
            if grid_idx[0] >= len(reduced_plant_map[0]):
                continue
            zombie_map[line_id][grid_idx[0]].append({
                'name': zombie.name,
                'speed': zombie.speed / zombie.ice_slow_ratio,
                'health': zombie.helmet_health + zombie.helmet_type2_health + zombie.health
            })

    # Other information.
    # ``sun_value``: current sun value acquired.
    # ``has_cars``: does each line has cars.
    meta_info = {
        'sun_value': state.menubar.sun_value,
        'has_cars': [state.cars[i] is not None for i in range(len(state.cars))]
    }

    total_info = {
        'meta_info': meta_info,
        'plant_map': reduced_plant_map,
        'zombie_map': zombie_map
    }

    return total_info


def dict2language(state_dict: dict) -> str:
    r"""
    Overview:
        Given a dict generated from dict, convert this dict into language form.
    Arguments:
        state_dict: the input state dict.
    Returns:
        total_info_str: the converted string.
    """
    # Construct the meta info part.
    meta_info = state_dict['meta_info']
    meta_info_str = f'Current sun value: {meta_info["sun_value"]}.'
    meta_info_str += ' '.join([f"Is car for line {i} ready? {meta_info['has_cars'][i]}."
                               for i in range(len(meta_info['has_cars']))])

    # Construct the grid info part.
    grid_info_str = ""
    for line in range(len(state_dict['plant_map'])):
        for row in range(len(state_dict['plant_map'][0])):
            grid_info_str += f'GRID[{line}][{row}] TYPE: {state_dict["plant_map"][line][row]["plot_type"]} PLANT: ' \
                             f'{state_dict["plant_map"][line][row]["plants"]}' \
                             f' ZOMBIE: {state_dict["zombie_map"][line][row]}\n'

    total_info_str = meta_info_str + '\n' + grid_info_str
    return total_info_str
