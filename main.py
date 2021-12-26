import copy
import json
import os
import uuid


def main():
    with open('good/data_1.json') as good_file:
        good = json.load(good_file)

    good_with_efficiency = hydrate_artifact_with_efficiency(good)
    good_with_id = hydrate_artifact_with_id(good_with_efficiency)

    set_type_format_artifacts = good_to_set_type_format(good_with_id)

    build_file_names = find_files_by_extension('builds/', '.json')
    id_format_artifacts = dict()

    for build_file_name in build_file_names:
        with open(build_file_name) as build_file:
            build = json.load(build_file)
        matched_artifacts = get_match_artifacts(set_type_format_artifacts, build)
        scored_artifacts = score_artifacts(matched_artifacts, build)

        for scored_artifact in scored_artifacts:
            if scored_artifact['id'] not in id_format_artifacts:
                id_format_artifacts[scored_artifact['id']] = make_id_format(scored_artifact, build)
            else:
                pass
                # copiar build score para artefato existente

    # reconstruir formato GOOD
    print(json.dumps(id_format_artifacts))


def find_files_by_extension(path, extension):
    file_names = list()
    for root, dirs, files in os.walk(path):
        if not len(files):
            continue

        file_names.extend([os.path.join(root, file_name) for file_name in files if file_name.endswith(extension)])

    return file_names


def hydrate_artifact_with_efficiency(good):
    """Calculate average efficiency for each sub stat

    The greatest efficiency is achieved when the artifact contains:
    - 9 rolls (only in rarity equal 5 stars begin with 4 sub stats)
    - Each roll in max value for specific sub stat (others possible values are 70%, 80% and 90%)
    """
    good = copy.deepcopy(good)

    max_artifact_rolls = 9

    with open('artifact-max-stats.json') as artifact_stats_file:
        artifact_stats_constants = json.load(artifact_stats_file)

    for artifact in good['artifacts']:
        artifact_rarity = str(artifact['rarity'])

        for sub_stats in artifact['substats']:
            sub_stat_key = sub_stats['key']

            if sub_stat_key != '':
                max_roll_value = artifact_stats_constants[sub_stat_key][artifact_rarity]
                current_value = sub_stats['value']
                average_efficiency = (current_value / max_roll_value) / max_artifact_rolls
                sub_stats['efficiency'] = average_efficiency
            else:
                sub_stats['efficiency'] = 0

    return good


def hydrate_artifact_with_id(good):
    """Generate random ID for each artifact"""
    good = copy.deepcopy(good)

    for artifact in good['artifacts']:
        artifact['id'] = str(uuid.uuid4())

    return good


def good_to_set_type_format(good):
    """Convert GOOD format to Set/Type format

    Output format example:
    - { SetName: { typeName: [...] } }
    - { HuskOfOpulentDreams: { flower: [], plume: [], sands: [], circlet: [], goblet: [] } }
    """
    artifacts = dict()
    for artifact in good['artifacts']:
        if artifact['setKey'] not in artifacts:
            artifacts[artifact['setKey']] = dict({
                'flower': [],
                'plume': [],
                'sands': [],
                'goblet': [],
                'circlet': [],
            })

        artifacts[artifact['setKey']][artifact['slotKey']].append(artifact)

    return artifacts


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
    return [artifact for artifact in artifacts if artifact['mainStatKey'] in main_stats]


def get_match_artifacts(artifacts, build):
    """Return artifact list that match the build

    artifacts: list with all artifacts
    build: contains the definition of filter rules
    """
    flower, plume, sands, goblet, circlet = get_artifacts_match_with_set(artifacts, build['filter']['set'])

    sands = get_artifacts_match_with_main_stat(sands, build['filter']['sands'])
    goblet = get_artifacts_match_with_main_stat(goblet, build['filter']['goblet'])
    circlet = get_artifacts_match_with_main_stat(circlet, build['filter']['circlet'])

    return [*flower, *plume, *sands, *goblet, *circlet]


# ToDo: usar deepcopy
# ToDo: criar lógica de pontuação
def score_artifacts(artifacts, build):
    for artifact in artifacts:
        artifact['score'] = 1

    return artifacts


def make_id_format(artifact, build):
    id_format_artifact = copy.deepcopy(artifact)
    # ToDo: criar função para adicionar score na list
    id_format_artifact['build_score'] = [{
        'character': build['character'],
        'build': build['build'],
        'score': artifact['score']
    }]
    del id_format_artifact['score']
    return id_format_artifact


# id_format_artifacts = {
#     '123': {
#         id: '123',
#         set: '',
#         type: '',
#         main_stat: '',
#         first_substat: '',
#         second_substat: '',
#         third_substat: '',
#         forth_substat: '',
#         buildScore: [
#             {character: 'Zhongli', build: 'Shield Bot', score: 80},
#         ],
#     }
# }

if __name__ == '__main__':
    main()

# ToDo:
# - typing
# - code quality tools
# - unit tests
