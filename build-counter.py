import click
import json

from collections import defaultdict


@click.command()
@click.option('-i', '--input-file', required=True, type=str, help='Specify input file with artifact builds.')
def main(input_file):
    builds = defaultdict(int)

    with open(input_file) as artifact_file:
        artifacts = json.load(artifact_file)

    for artifact in artifacts:
        for build in artifact['build_score']:
            build_name = f"{build['character']} - {build['name']}"
            builds[build_name] += 1

    sorted_builds = dict(sorted(builds.items(), key=lambda x: x[1], reverse=True))
    for build_name, build_count in sorted_builds.items():
        print(f'{build_count}: {build_name}')


if __name__ == '__main__':
    main()

