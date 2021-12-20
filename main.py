
good = {}  # ler arquivo .GOOD
buildFiles = []  # listar arquivos do diretório
builds = []  # ler arquivos e converter para objeto iterando sobre buildFiles

artifacts = []  # convert GOOD format to set/type format

# artifacts
# {
#     millelith: {
#         flower: [],
#         feather: [],
#         sands: [],
#         goblet: [],
#         circlet: [],
#     }
# }

# Hidratar
# pode ser necessário criar um ID único nessa etapa
# calcular eficiência de cada sub status (descobrir número de rolamentos)

def filter(build, artifacts):
    filtered_artifacts = {flower: [], feather: [], sands: [], goblet: [], circlet: []}

    for artifactSet in build.filter.set:
        filtered_artifacts.flower.extend(artifacts[artifactSet].flower)
        filtered_artifacts.feather.extend(artifacts[artifactSet].feather)
        filtered_artifacts.sands.extend(artifacts[artifactSet].sands)
        filtered_artifacts.goblet.extend(artifacts[artifactSet].goblet)
        filtered_artifacts.circlet.extend(artifacts[artifactSet].circlet)

    filtered_artifacts.sands = filter_sands(build, filtered_artifacts.sands)
    filtered_artifacts.goblet = filter_goblet(build, filtered_artifacts.goblet)
    filtered_artifacts.circlet = filter_circlet(build, filtered_artifacts.circlet)

# filtered_artifacts
# {
#     flower: [],
#     feather: [],
#     sands: [],
#     goblet: [],
#     circlet: [],
# }


def main():
    for build in builds:
        filtered_artifacts = filter(build, artifacts)
        # var = calculate(artifacts)


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


