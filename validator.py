import math

import click
import json


@click.command()
@click.option('-i', '--input-file', required=True, type=str, help='Specify input file in GOOD format.')
def main(input_file):
    with open(input_file) as good_file:
        good = json.load(good_file)

    good_artifact_list = [artifact for artifact in good['artifacts'] if artifact['rarity'] == 5]
    check_for_null_on_the_first_three_sub_stats(good_artifact_list)
    check_for_null_on_forth_sub_stat_for_upgraded_artifact(good_artifact_list)
    check_max_rarity_for_artifact_sets(good_artifact_list)


def print_header(message, good_artifact_list):
    print('-' * len(message))
    print(message)
    print('Finds: ', len(good_artifact_list))
    print('-' * len(message))
    print(*good_artifact_list, sep='\n')


def check_for_null_on_the_first_three_sub_stats(good_artifact_list):
    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        sub_stat_keys = [sub_stat['key'] for sub_stat in good_artifact['substats'][0:3]]
        if None in sub_stat_keys:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check for null on the first three sub stats',
        artifacts_with_problem
    )


def check_for_null_on_forth_sub_stat_for_upgraded_artifact(good_artifact_list):
    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        rank = math.floor(good_artifact['level'] / 4)
        if rank > 1 and good_artifact['substats'][3]['key'] is None:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check for null on forth sub stat for upgraded artifact',
        artifacts_with_problem
    )


def check_max_rarity_for_artifact_sets(good_artifact_list):
    max_rarity_four_sets = [
        'Berserker',
        'BraveHeart',
        'DefendersWill',
        'Gambler',
        'Instructor',
        'MartialArtist',
        'PrayersForDestiny',
        'PrayersForIllumination',
        'PrayersForWisdom',
        'PrayersToSpringtime',
        'ResolutionOfSojourner',
        'Scholar',
        'TheExile',
        'TinyMiracle',
    ]
    max_rarity_three_sets = [
        'Adventurer',
        'LuckyDog',
        'TravelingDoctor',
    ]

    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        if good_artifact['setKey'] in max_rarity_four_sets and good_artifact['rarity'] > 4:
            artifacts_with_problem.append(good_artifact)
        if good_artifact['setKey'] in max_rarity_three_sets and good_artifact['rarity'] > 3:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check max rarity for artifact sets',
        artifacts_with_problem
    )


if __name__ == '__main__':
    main()
