import click
import copy
import functools
import json
import math
import os
import uuid


# Artifact formats
# - GOOD (Genshin Open Object Description)
# - G2C (Genshin Garbage Collector)
#
# Wrappers
# - List: [object]
# - Set/Slot format: { set_key: { slot_key: [object] } }
# - ID format: { id: object }

@click.command()
@click.option('-f', '--filters', multiple=True, type=str, help='Filter artifacts according to defined rules.')
def main(filters):
    with open('good/data_3.json') as good_file:
        good = json.load(good_file)

    artifact_list = generate_g2c_artifact_list_from_good(good['artifacts'])
    artifact_list_with_efficiency = hydrate_sub_stats_efficiency(artifact_list)

    artifact_set_slot_format = convert_g2c_list_to_g2c_set_slot_format(artifact_list_with_efficiency)

    build_file_names = find_files_by_extension('builds/', '.json')
    id_format_artifacts = score_artifacts_from_build_definitions(artifact_set_slot_format, build_file_names)

    id_format_artifacts_with_best_score = hydrate_artifacts_with_best_score(id_format_artifacts)

    filter_obj_list = parse_filter_string(filters)
    filtered_artifacts = filter_artifacts(id_format_artifacts_with_best_score, filter_obj_list)

    print(json.dumps(filtered_artifacts, indent=2))
    print(len(filtered_artifacts))

    # implementar parâmetros de CLI como descrito no README
    # tarefas de qualidade de código (typing, code quality tools, unit tests, jsonlint)
    updated_good = update_good_artifacts(good, id_format_artifacts_with_best_score)


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


def generate_g2c_artifact_from_good(good_artifact):
    """Generate G2C artifact structure from GOOD artifact structure

    :param good_artifact: GOOD (Genshin Open Object Description) artifact structure
    :return: G2C (Genshin Garbage Collector) artifact structure
    """
    return {
            'id': str(uuid.uuid4()),
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

            if sub_stat_key == '':  # its condition is for artifacts with less than 4 sub stats
                sub_stat['efficiency'] = 0
            else:
                max_roll_value = artifact_stats_constants[sub_stat_key][artifact_rarity]
                current_value = sub_stat['value']
                average_efficiency = (current_value / max_roll_value) / max_artifact_rolls
                sub_stat['efficiency'] = average_efficiency

    return g2c_artifact_list


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


def score_artifacts_from_build_definitions(artifact_set_type_format, build_file_names):
    """Score artifacts from build definitions

    - convert artifact_set_slot_format to artifact_id_format
    - get artifact that match with builds
    - score artifacts from build definitions

    :param artifact_set_type_format: G2C (Genshin Garbage Collector) artifact Set/Slot format
    :param build_file_names: build file path list
    :return: G2C (Genshin Garbage Collector) artifact ID format
    """
    artifact_id_format = dict()
    for build_file_name in build_file_names:
        with open(build_file_name) as build_file:
            build = json.load(build_file)

        matched_artifacts = get_matched_artifacts(artifact_set_type_format, build)
        artifacts_score = score_artifacts(matched_artifacts, build)

        for matched_artifact in matched_artifacts:
            identifier = matched_artifact['id']
            if identifier not in artifact_id_format.keys():
                artifact_id_format[identifier] = copy.deepcopy(matched_artifact)

            artifact_id_format[identifier]['build_score'].append({
                'character': build['character'],
                'build': build['name'],
                'score': artifacts_score[identifier]
            })
    return artifact_id_format


def get_artifacts_match_with_set(artifacts, artifact_set_names):
    """Filter artifact list based on set names

    artifacts: list with all artifacts
    artifact_set_names: list with allowed set names
    """
    flower = list()
    plume = list()
    sands = list()
    goblet = list()
    circlet = list()

    for artifact_set in artifact_set_names:
        if artifact_set in artifacts.keys():
            flower.extend(artifacts[artifact_set]['flower'])
            plume.extend(artifacts[artifact_set]['plume'])
            sands.extend(artifacts[artifact_set]['sands'])
            goblet.extend(artifacts[artifact_set]['goblet'])
            circlet.extend(artifacts[artifact_set]['circlet'])
    return flower, plume, sands, goblet, circlet


def get_artifacts_match_with_main_stat(artifacts, main_stats):
    """Filter artifact list based on main stat

    artifacts: list with all artifacts
    main_stats: list with allowed main stats
    """
    return [artifact for artifact in artifacts if artifact['main_stat_key'] in main_stats]


def get_matched_artifacts(artifacts, build):
    """Return artifact list that match the build

    artifacts: list with all artifacts
    build: contains the definition of filter rules
    """
    flower, plume, sands, goblet, circlet = get_artifacts_match_with_set(artifacts, build['filter']['set'])

    sands = get_artifacts_match_with_main_stat(sands, build['filter']['sands'])
    goblet = get_artifacts_match_with_main_stat(goblet, build['filter']['goblet'])
    circlet = get_artifacts_match_with_main_stat(circlet, build['filter']['circlet'])

    return [*flower, *plume, *sands, *goblet, *circlet]


def calculate_normalization_factor(sub_stats):
    sorted_sub_status = sorted(sub_stats, reverse=True)[0:4]
    sorted_sub_status[0] *= 6
    return sum(sorted_sub_status) / 9


def score_artifacts(artifacts, build):
    normalization_factor = calculate_normalization_factor(build['sub_stats'].values())

    artifacts_score = dict()
    for artifact in artifacts:
        score = functools.reduce(
            lambda a, b: a + b['efficiency'] * build['sub_stats'].get(b['key'], 0), artifact['sub_stats'], 0)
        artifacts_score[artifact['id']] = round(score / normalization_factor, 2)

    return artifacts_score


def hydrate_artifacts_with_best_score(artifacts):
    hydrated_artifacts = copy.deepcopy(artifacts)
    for artifact in hydrated_artifacts.values():
        best_score = max(artifact['build_score'], key=lambda a: a['score'])
        artifact['best_score'] = best_score['score']

    return hydrated_artifacts


def parse_filter_string(filter_str_list):
    filter_obj_list = list()

    for filter_str in filter_str_list:
        filter_obj = {
            'selectors': [],
            'action': {'key': '', 'value': ''},
        }

        selectors_str, action_str = filter_str.split('=')
        selector_str_list = selectors_str.split(',')

        for selector_str in selector_str_list:
            selector_key, selector_value = selector_str.split(':')
            filter_obj['selectors'].append({
                'key': selector_key,
                'value': selector_value.strip('[]').split(';')
            })

        action_key, action_value = action_str.split(':')
        filter_obj['action']['key'] = action_key
        filter_obj['action']['value'] = action_value

        filter_obj_list.append(filter_obj)

    return filter_obj_list


def filter_artifacts(filtered_artifacts, filter_rules):
    filtered_artifacts = copy.deepcopy(filtered_artifacts)

    actions_functions = {
        't': lambda artifacts, threshold: [artifact for artifact in artifacts if artifact['best_score'] < float(threshold)],
        'b': lambda artifacts, threshold: sorted(artifacts, key=lambda item: item['best_score'], reverse=True)[int(threshold):]
    }

    for filter_rule in filter_rules:
        temp_artifacts = filtered_artifacts.values()
        for selector in filter_rule['selectors']:
            temp_artifacts = [artifact for artifact in temp_artifacts if str(artifact[selector['key']]) in selector['value']]

        action_key, action_value = filter_rule['action'].values()
        temp_artifacts = actions_functions[action_key](temp_artifacts, action_value)

        filtered_artifact_ids = [artifact['id'] for artifact in temp_artifacts]
        [filtered_artifacts.pop(identifier) for identifier in filtered_artifact_ids]

    return filtered_artifacts


def update_good_artifacts(good, artifacts):
    good = copy.deepcopy(good)
    good_artifacts = [artifact['artifact_data'] for artifact in artifacts.values()]
    good['artifacts'] = good_artifacts
    return good


if __name__ == '__main__':
    main()
