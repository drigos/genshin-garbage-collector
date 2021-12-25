import json


def main():
    with open('good/data_2.json') as good_file:
        good = json.load(good_file)

    hydrated_good = hydrate_artifact_with_efficiency(good)
    artifacts = good_to_set_type_format(hydrated_good)
    print(json.dumps(artifacts))


def hydrate_artifact_with_efficiency(good):
    """Calculate average efficiency for each sub stat"""
    max_artifact_rolls = 9

    with open('artifact-max-stats.json') as artifact_stats_file:
        artifact_stats_constants = json.load(artifact_stats_file)

    for artifact in good['artifacts']:
        artifact_rarity = str(artifact['rarity'])

        for sub_stats in artifact['substats']:
            sub_stat_key = sub_stats['key']

            max_roll_value = artifact_stats_constants[sub_stat_key][artifact_rarity]
            current_value = sub_stats['value']
            average_efficiency = (current_value / max_roll_value) / max_artifact_rolls
            sub_stats['efficiency'] = average_efficiency

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

# buildFiles = []  # listar arquivos do diretório
# builds = []  # ler arquivos e converter para objeto iterando sobre buildFiles

# def filter(build, artifacts):
#     filtered_artifacts = {flower: [], feather: [], sands: [], goblet: [], circlet: []}
#
#     for artifactSet in build.filter.set:
#         filtered_artifacts.flower.extend(artifacts[artifactSet].flower)
#         filtered_artifacts.feather.extend(artifacts[artifactSet].feather)
#         filtered_artifacts.sands.extend(artifacts[artifactSet].sands)
#         filtered_artifacts.goblet.extend(artifacts[artifactSet].goblet)
#         filtered_artifacts.circlet.extend(artifacts[artifactSet].circlet)
#
#     filtered_artifacts.sands = filter_sands(build, filtered_artifacts.sands)
#     filtered_artifacts.goblet = filter_goblet(build, filtered_artifacts.goblet)
#     filtered_artifacts.circlet = filter_circlet(build, filtered_artifacts.circlet)

# filtered_artifacts
# {
#     flower: [],
#     feather: [],
#     sands: [],
#     goblet: [],
#     circlet: [],
# }


# def main():
#     for build in builds:
#         filtered_artifacts = filter(build, artifacts)
#         # var = calculate(artifacts)


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
