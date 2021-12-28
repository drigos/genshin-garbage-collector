import copy
import functools
import json
import math
import os
import uuid


def main():
    with open('good/data_3.json') as good_file:
        good = json.load(good_file)

    artifacts = generate_output_format_from_good(good['artifacts'])
    artifacts_with_efficiency = calculate_sub_stats_efficiency(artifacts)

    set_type_format_artifacts = convert_list_to_set_type_format(artifacts_with_efficiency)

    build_file_names = find_files_by_extension('builds/', '.json')
    id_format_artifacts = dict()

    for build_file_name in build_file_names:
        with open(build_file_name) as build_file:
            build = json.load(build_file)

        matched_artifacts = get_matched_artifacts(set_type_format_artifacts, build)
        artifacts_score = score_artifacts(matched_artifacts, build)

        for matched_artifact in matched_artifacts:
            identifier = matched_artifact['id']
            if identifier not in id_format_artifacts.keys():
                id_format_artifacts[identifier] = copy.deepcopy(matched_artifact)

            id_format_artifacts[identifier]['build_score'].append({
                'character': build['character'],
                'build': build['name'],
                'score': artifacts_score[identifier]
            })

    id_format_artifacts_with_best_score = hydrate_artifacts_with_best_score(id_format_artifacts)

    filter_str_list = [
        'rank:0=t:0.2',
        'rank:1=t:0.25',
        'rank:2=t:0.3',
        'rank:3=t:0.35',
        'rank:4=t:0.4',
        'rank:5=t:0.5'
    ]
    # filter_str_list = [
    #     'set_key:[GladiatorsFinale;WanderersTroupe],rank:[0;1;2;3]=b:20',
    #     'set_key:[GladiatorsFinale;WanderersTroupe],rank:[0;1;2;3]=t:0.2',
    #     'rank:5=t:0.5'
    # ]
    filter_obj_list = parse_filter_string(filter_str_list)
    filtered_artifacts = filter_artifacts(id_format_artifacts_with_best_score, filter_obj_list)

    print(json.dumps(filtered_artifacts, indent=2))

    # receber argumentos via CLI (good_file, threshold, amount)
    # tarefas de qualidade de código (typing, code quality tools, unit tests, jsonlint)
    updated_good = update_good_artifacts(good, id_format_artifacts_with_best_score)


def find_files_by_extension(path, extension):
    file_names = list()
    for root, dirs, files in os.walk(path):
        if not len(files):
            continue

        file_names.extend([os.path.join(root, file_name) for file_name in files if file_name.endswith(extension)])

    return file_names


def generate_output_format_from_good(artifacts):
    output_format_artifacts = list()
    for artifact in artifacts:
        output_format_artifacts.append({
            'id': str(uuid.uuid4()),
            'set_key': artifact['setKey'],
            'slot_key': artifact['slotKey'],
            'main_stat_key': artifact['mainStatKey'],
            'rarity': artifact['rarity'],
            'level': artifact['level'],
            'rank': math.floor(artifact['level'] / 4),
            'sub_stats': copy.deepcopy(artifact['substats']),
            'best_score': 0,
            'build_score': [],
            'artifact_data': copy.deepcopy(artifact)
        })
    return output_format_artifacts


def calculate_sub_stats_efficiency(artifacts):
    """Calculate average efficiency for each sub stat

    The greatest efficiency is achieved when the artifact contains:
    - 9 rolls (only in rarity equal 5 stars begin with 4 sub stats)
    - Each roll in max value for specific sub stat (others possible values are 70%, 80% and 90%)
    """
    artifacts = copy.deepcopy(artifacts)

    max_artifact_rolls = 9

    with open('artifact-max-stats.json') as artifact_stats_file:
        artifact_stats_constants = json.load(artifact_stats_file)

    for artifact in artifacts:
        artifact_rarity = str(artifact['rarity'])

        for sub_stat in artifact['sub_stats']:
            sub_stat_key = sub_stat['key']

            if sub_stat_key == '':  # its condition is for artifacts with less than 4 sub stats
                sub_stat['efficiency'] = 0
            else:
                max_roll_value = artifact_stats_constants[sub_stat_key][artifact_rarity]
                current_value = sub_stat['value']
                average_efficiency = (current_value / max_roll_value) / max_artifact_rolls
                sub_stat['efficiency'] = average_efficiency

    return artifacts


def convert_list_to_set_type_format(artifacts):
    """Convert artifact list to Set/Type format

    Output format example:
    - { SetName: { typeName: [...] } }
    - { HuskOfOpulentDreams: { flower: [], plume: [], sands: [], circlet: [], goblet: [] } }
    """
    set_type_format_artifacts = dict()
    for artifact in artifacts:
        artifact_set_key = artifact['set_key']
        artifact_slot_key = artifact['slot_key']
        if artifact_set_key not in set_type_format_artifacts.keys():
            set_type_format_artifacts[artifact_set_key] = dict({
                'flower': [],
                'plume': [],
                'sands': [],
                'goblet': [],
                'circlet': [],
            })

        set_type_format_artifacts[artifact_set_key][artifact_slot_key].append(artifact)

    return set_type_format_artifacts


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
