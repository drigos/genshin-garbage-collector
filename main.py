import copy
import functools
import json
import os
import uuid


def main():
    with open('good/data_1.json') as good_file:
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
    # função para manter artefatos acima de um determinado best_score
    # função para manter N melhores artefatos

    # escrever builds
    # receber argumentos via CLI (good_file, threshold, amount)
    # tarefas de qualidade de código (typing, code quality tools, unit tests)
    updated_good = update_good_artifacts(good, id_format_artifacts_with_best_score)
    print(json.dumps(updated_good, indent=2))


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


def update_good_artifacts(good, artifacts):
    good = copy.deepcopy(good)
    good_artifacts = [artifact['artifact_data'] for artifact in artifacts.values()]
    good['artifacts'] = good_artifacts
    return good


if __name__ == '__main__':
    main()
