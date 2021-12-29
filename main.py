import click
import copy
import functools
import json
import math
import os


# Artifact formats
# - GOOD (Genshin Open Object Description)
# - G2C (Genshin Garbage Collector)

# Artifact wrappers
# - List: [artifact]
# - Set/Slot format: { set_key: { slot_key: [artifact] } }
# - ID format: { id: artifact }

@click.command()
@click.option('-i', '--input-file', required=True, type=str, help='Specify GOOD file.')
@click.option('-f', '--filters', multiple=True, type=str, help='Filter artifacts according to defined rules.')
@click.option('-e', '--export', is_flag=True, help='Display artifacts in GOOD format (default is G2C format)')
def main(input_file, filters, export):
    with open(input_file) as good_file:
        good = json.load(good_file)

    artifact_list = generate_g2c_artifact_list_from_good(good['artifacts'])
    artifact_list = hydrate_sub_stats_efficiency(artifact_list)

    build_file_name_list = find_files_by_extension('builds/', '.json')
    artifact_id_format = get_artifacts_with_build_scores(artifact_list, build_file_name_list)

    if filters:
        filter_rule_list = parse_cli_filter_string(filters)
        artifact_id_format = filter_artifacts(artifact_id_format, filter_rule_list)

    output = artifact_id_format
    if export:
        output = update_good_artifacts(good, artifact_id_format)

    print(json.dumps(output, indent=2))
    print(len(output))

    # implementar parâmetros de CLI como descrito no README
    # tarefas de qualidade de código (typing, code quality tools, unit tests, jsonlint)


def find_files_by_extension(path, extension):
    """Return list of paths for all files with specified extension

    :param path: directory to search
    :param extension: extension to search
    :return: list of paths for all files that match conditions
    """
    file_names = list()
    for root, dirs, files in os.walk(path):
        if not len(files):
            continue

        file_names.extend([os.path.join(root, file_name) for file_name in files if file_name.endswith(extension)])

    return file_names


def parse_cli_filter_string(filter_str_list):
    """Parse -f/--filter CLI argument

    Filter rules format:
    {'selectors': [{'key': 'rank', 'value': ['0']}], 'action': {'key': 't','value': '0.2'}}

    :param filter_str_list: string with 'selector_list=action'
    :return: filter rules format
    """
    filter_rule_list = list()

    for filter_str in filter_str_list:
        filter_rule = {
            'selectors': [],
            'action': {'key': '', 'value': ''},
        }

        selectors_str, action_str = filter_str.split('=')
        selector_str_list = selectors_str.split(',')

        for selector_str in selector_str_list:
            selector_key, selector_value = selector_str.split(':')
            filter_rule['selectors'].append({
                'key': selector_key,
                'value': selector_value.strip('[]').split(';')
            })

        action_key, action_value = action_str.split(':')
        filter_rule['action']['key'] = action_key
        filter_rule['action']['value'] = action_value

        filter_rule_list.append(filter_rule)

    return filter_rule_list


def generate_g2c_artifact_from_good(good_artifact):
    """Generate G2C artifact structure from GOOD artifact structure

    :param good_artifact: GOOD (Genshin Open Object Description) artifact structure
    :return: G2C (Genshin Garbage Collector) artifact structure
    """
    return {
            'id': good_artifact['Id'],
            'set_key': good_artifact['setKey'],
            'slot_key': good_artifact['slotKey'],
            'main_stat_key': good_artifact['mainStatKey'],
            'rarity': good_artifact['rarity'],
            'level': good_artifact['level'],
            'rank': math.floor(good_artifact['level'] / 4),
            'sub_stats': copy.deepcopy(good_artifact['substats']),
            'best_score': 0,
            'build_score': [],
            'artifact_data': copy.deepcopy(good_artifact)
        }


def generate_g2c_artifact_list_from_good(good_artifact_list):
    """Generate G2C artifact list from GOOD artifact list

    :param good_artifact_list: GOOD (Genshin Open Object Description) artifact list
    :return: G2C (Genshin Garbage Collector) artifact list
    """
    return [generate_g2c_artifact_from_good(artifact) for artifact in good_artifact_list]


def hydrate_sub_stats_efficiency(g2c_artifact_list):
    """Calculate average efficiency for each sub stat

    The greatest efficiency is achieved when the artifact contains:
    - 9 rolls (only in rarity equal 5 stars begin with 4 sub stats)
    - Each roll in max value for specific sub stat (others possible values are 70%, 80% and 90%)

    :param g2c_artifact_list: G2C (Genshin Garbage Collector) artifact list (without efficiency)
    :return: G2C (Genshin Garbage Collector) artifact list (with efficiency)
    """
    g2c_artifact_list = copy.deepcopy(g2c_artifact_list)

    max_artifact_rolls = 9

    with open('artifact-max-stats.json') as artifact_stats_file:
        artifact_stats_constants = json.load(artifact_stats_file)

    for g2c_artifact in g2c_artifact_list:
        artifact_rarity = str(g2c_artifact['rarity'])

        for sub_stat in g2c_artifact['sub_stats']:
            sub_stat_key = sub_stat['key']

            if sub_stat_key is None:  # its condition is for artifacts with less than 4 sub stats
                sub_stat['efficiency'] = 0
            else:
                max_roll_value = artifact_stats_constants[sub_stat_key][artifact_rarity]
                current_value = sub_stat['value']
                average_efficiency = (current_value / max_roll_value) / max_artifact_rolls
                sub_stat['efficiency'] = average_efficiency

    return g2c_artifact_list


def get_artifacts_with_build_scores(g2c_artifact_list, build_file_name_list):
    """Get artifacts with build scores

    :param g2c_artifact_list: G2C (Genshin Garbage Collector) artifact list
    :param build_file_name_list: build file path list
    :return: G2C (Genshin Garbage Collector) artifact list
    """
    g2c_artifact_set_slot_format = convert_g2c_list_to_g2c_set_slot_format(g2c_artifact_list)

    g2c_artifact_id_format = dict()
    for build_file_name in build_file_name_list:
        with open(build_file_name) as build_file:
            build = json.load(build_file)

        matched_artifact_list = get_artifacts_that_match_build(g2c_artifact_set_slot_format, build)

        for matched_artifact in matched_artifact_list:
            artifact_id = matched_artifact['id']
            if artifact_id not in g2c_artifact_id_format.keys():
                g2c_artifact_id_format[artifact_id] = copy.deepcopy(matched_artifact)

        artifacts_score = score_artifacts(matched_artifact_list, build)

        for artifact_id, artifact_score in artifacts_score.items():
            g2c_artifact_id_format[artifact_id]['build_score'].append({
                'character': build['character'],
                'build': build['name'],
                'score': artifact_score
            })

    for g2c_artifact in g2c_artifact_id_format.values():
        best_score = max(g2c_artifact['build_score'], key=lambda artifact: artifact['score'])
        g2c_artifact['best_score'] = best_score['score']

    return g2c_artifact_id_format


def convert_g2c_list_to_g2c_set_slot_format(g2c_artifact_list):
    """Convert G2C artifact list to G2C artifact Set/Slot format

    :param g2c_artifact_list: G2C (Genshin Garbage Collector) artifact list
    :return: G2C (Genshin Garbage Collector) artifact Set/Slot format
    """
    g2c_artifact_set_slot_format = dict()
    for g2c_artifact in g2c_artifact_list:
        artifact_set_key = g2c_artifact['set_key']
        artifact_slot_key = g2c_artifact['slot_key']
        if artifact_set_key not in g2c_artifact_set_slot_format.keys():
            g2c_artifact_set_slot_format[artifact_set_key] = dict({
                'flower': [],
                'plume': [],
                'sands': [],
                'goblet': [],
                'circlet': [],
            })

        g2c_artifact_set_slot_format[artifact_set_key][artifact_slot_key].append(g2c_artifact)

    return g2c_artifact_set_slot_format


def get_artifacts_that_match_build(g2c_artifact_set_slot_format, build):
    """Return artifact list that match build

    :param g2c_artifact_set_slot_format: G2C (Genshin Garbage Collector) artifact Set/Slot format
    :param build: contains the definition of filter rules
    :return: filtered G2C (Genshin Garbage Collector) artifact list
    """
    flower, plume, sands, goblet, circlet = get_artifacts_match_set_key(
        g2c_artifact_set_slot_format,
        build['filter']['set']
    )

    sands = get_artifacts_match_main_stat(sands, build['filter']['sands'])
    goblet = get_artifacts_match_main_stat(goblet, build['filter']['goblet'])
    circlet = get_artifacts_match_main_stat(circlet, build['filter']['circlet'])

    return [*flower, *plume, *sands, *goblet, *circlet]


def get_artifacts_match_set_key(g2c_artifact_set_slot_format, artifact_set_keys):
    """Filter artifact list based on set keys

    :param g2c_artifact_set_slot_format: G2C (Genshin Garbage Collector) artifact Set/Slot format
    :param artifact_set_keys: list with allowed set keys
    :return: filtered G2C (Genshin Garbage Collector) artifact list separate for slot
    """
    flower = list()
    plume = list()
    sands = list()
    goblet = list()
    circlet = list()

    for artifact_set_key in artifact_set_keys:
        if artifact_set_key in g2c_artifact_set_slot_format.keys():
            flower.extend(g2c_artifact_set_slot_format[artifact_set_key]['flower'])
            plume.extend(g2c_artifact_set_slot_format[artifact_set_key]['plume'])
            sands.extend(g2c_artifact_set_slot_format[artifact_set_key]['sands'])
            goblet.extend(g2c_artifact_set_slot_format[artifact_set_key]['goblet'])
            circlet.extend(g2c_artifact_set_slot_format[artifact_set_key]['circlet'])
    return flower, plume, sands, goblet, circlet


def get_artifacts_match_main_stat(g2c_artifact_list, artifact_main_stats):
    """Filter artifact list based on main stats

    :param g2c_artifact_list: G2C (Genshin Garbage Collector) artifact list
    :param artifact_main_stats: list with allowed main stats
    :return filtered G2C (Genshin Garbage Collector) artifact list
    """
    return [artifact for artifact in g2c_artifact_list if artifact['main_stat_key'] in artifact_main_stats]


def score_artifacts(g2c_artifact_list, build):
    """Return score for each artifact in the list

    :param g2c_artifact_list: G2C (Genshin Garbage Collector) artifact list
    :param build: contains the definition of filter rules
    :return: dict {id: score} for each G2C (Genshin Garbage Collector) artifact
    """
    normalization_factor = calculate_normalization_factor(build['sub_stats'].values())

    artifacts_score = dict()
    for g2c_artifact in g2c_artifact_list:
        score = functools.reduce(
            lambda acc, sub_stat: acc + sub_stat['efficiency'] * build['sub_stats'].get(sub_stat['key'], 0),
            g2c_artifact['sub_stats'],
            0
        )
        artifacts_score[g2c_artifact['id']] = round(score / normalization_factor, 2)

    return artifacts_score


def calculate_normalization_factor(sub_stats):
    """Calculate the optimal sub stats to find the normalization factor

    :param sub_stats: sub stat list with weight
    :return: float representing the normalization factor
    """
    sorted_sub_status = sorted(sub_stats, reverse=True)[0:4]
    sorted_sub_status[0] *= 6
    return sum(sorted_sub_status) / 9


def filter_artifacts(g2c_artifact_id_format, filter_rule_list):
    """Filter artifacts according to defined rules

    Only artifacts matched by the selector will be filtered
    Any artifact that don't match the selector will be preserved

    :param g2c_artifact_id_format: G2C (Genshin Garbage Collector) artifact ID format
    :param filter_rule_list: list with selector and action to filter artifacts
    :return: G2C (Genshin Garbage Collector) artifact list
    """
    g2c_artifact_id_format = copy.deepcopy(g2c_artifact_id_format)

    actions_functions = {
        't': lambda artifacts, threshold: [artifact for artifact in artifacts if artifact['best_score'] < float(threshold)],
        'b': lambda artifacts, threshold: sorted(artifacts, key=lambda item: item['best_score'], reverse=True)[int(threshold):]
    }

    for filter_rule in filter_rule_list:
        exclusion_artifact_list = g2c_artifact_id_format.values()
        for selector in filter_rule['selectors']:
            if selector['key'] != '*':
                exclusion_artifact_list = [
                    artifact for artifact in exclusion_artifact_list
                    if str(artifact[selector['key']]) in selector['value']
                ]

        action_key, action_value = filter_rule['action'].values()
        exclusion_artifact_list = actions_functions[action_key](exclusion_artifact_list, action_value)

        filtered_artifact_ids = [artifact['id'] for artifact in exclusion_artifact_list]
        [g2c_artifact_id_format.pop(identifier) for identifier in filtered_artifact_ids]

    return g2c_artifact_id_format


def update_good_artifacts(good, artifact_id_format):
    good = copy.deepcopy(good)
    good_artifacts = [artifact['artifact_data'] for artifact in artifact_id_format.values()]
    good['artifacts'] = good_artifacts
    return good


if __name__ == '__main__':
    main()
