import copy
import json
import uuid


def main():
    with open('good/data_1.json') as good_file:
        good = json.load(good_file)

    # buildFiles = []  # listar arquivos do diretório
    # builds = []  # ler arquivos e converter para objeto iterando sobre buildFiles
    with open('builds/zhongli-shield-bot.json') as zhongli_build_file:
        zhongli_build = json.load(zhongli_build_file)

    good_with_efficiency = hydrate_artifact_with_efficiency(good)
    good_with_id = hydrate_artifact_with_id(good_with_efficiency)
    artifacts = good_to_set_type_format(good_with_id)

    filtered_artifacts = filter_mismatched_artifacts(zhongli_build, artifacts)

    print(json.dumps(filtered_artifacts))


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
    good = copy.deepcopy(good)

    for artifact in good['artifacts']:
        artifact['id'] = str(uuid.uuid4())

    return good


def good_to_set_type_format(good):
    """Convert GOOD format to Set/Type format

    Set/Type format example:
    { HuskOfOpulentDreams: { flower: [], plume: [], sands: [], circlet: [], goblet: [] } }
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


def filter_mismatched_artifacts(build, artifacts):
    filtered_artifacts = dict({'flower': [], 'plume': [], 'sands': [], 'goblet': [], 'circlet': []})

    for artifact_set in build['filter']['set']:
        if artifact_set in artifacts:
            filtered_artifacts['flower'].extend(artifacts[artifact_set]['flower'])
            filtered_artifacts['plume'].extend(artifacts[artifact_set]['plume'])
            filtered_artifacts['sands'].extend(artifacts[artifact_set]['sands'])
            filtered_artifacts['goblet'].extend(artifacts[artifact_set]['goblet'])
            filtered_artifacts['circlet'].extend(artifacts[artifact_set]['circlet'])

    filtered_artifacts['sands'] = filter_sands(build, filtered_artifacts['sands'])
    # filtered_artifacts['goblet'] = filter_goblet(build, filtered_artifacts['goblet'])
    # filtered_artifacts['circlet'] = filter_circlet(build, filtered_artifacts['circlet'])

    return filtered_artifacts


def filter_sands(build, artifacts):
    return [artifact for artifact in artifacts if artifact['mainStatKey'] in build['filter']['sands']]

# filtered_artifacts
# {
#     flower: [],
#     feather: [],
#     sands: [],
#     goblet: [],
#     circlet: [],
# }

# result = [
#     {
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
# ]

if __name__ == '__main__':
    main()


# tipagem
# ferramentas de qualidade de código
# teste unitário
