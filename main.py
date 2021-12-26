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

    id_format_artifacts = dict()

    build_path = 'builds/'
    for root, dirs, files in os.walk(build_path):
        if not len(files):
            continue

        build_file_names = [build_file_name for build_file_name in files if build_file_name.endswith('.json')]
        for build_file_name in build_file_names:
            with open(os.path.join(root, build_file_name)) as build_file:
                build = json.load(build_file)
            matched_artifacts = get_match_artifacts(build, set_type_format_artifacts)
            scored_artifacts = score_artifacts(build, matched_artifacts)

            for scored_artifact in scored_artifacts:
                if scored_artifact['id'] not in id_format_artifacts:
                    id_format_artifacts[scored_artifact['id']] = make_id_format(scored_artifact)
                else:
                    pass
                    # copiar build score para artefato existente

    # reconstruir formato GOOD
    print(json.dumps(id_format_artifacts))


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


def get_match_artifacts_by_main_stat(build, artifacts, type):
    return [artifact for artifact in artifacts if artifact['mainStatKey'] in build['filter'][type]]


def get_match_artifacts(build, artifacts):
    """Return artifact list that match the build"""
    flower = list()
    plume = list()
    sands = list()
    goblet = list()
    circlet = list()

    for artifact_set in build['filter']['set']:
        if artifact_set in artifacts:
            flower.extend(artifacts[artifact_set]['flower'])
            plume.extend(artifacts[artifact_set]['plume'])
            sands.extend(artifacts[artifact_set]['sands'])
            goblet.extend(artifacts[artifact_set]['goblet'])
            circlet.extend(artifacts[artifact_set]['circlet'])

    sands = get_match_artifacts_by_main_stat(build, sands, 'sands')
    goblet = get_match_artifacts_by_main_stat(build, goblet, 'goblet')
    circlet = get_match_artifacts_by_main_stat(build, circlet, 'circlet')

    return [*flower, *plume, *sands, *goblet, *circlet]


# ToDo: usar deepcopy
# ToDo: criar lógica de pontuação
def score_artifacts(build, artifacts):
    for artifact in artifacts:
        artifact['score'] = 1

    return artifacts


def make_id_format(artifact):
    return artifact


# id_format_artifacts = {
#     '123': {
#         id: '123',
#         set: '',
#         type: '',
#         mainStat: '',
#         firstSubstat: '',
#         secondSubstat: '',
#         thirdSubstat: '',
#         forthSubstat: '',
#         buildScore: [
#             {char: 'Zhongli', build: 'Shield Bot', score: 80},
#         ],
#     }
# }

if __name__ == '__main__':
    main()

# ToDo:
# - typing
# - code quality tools
# - unit tests
