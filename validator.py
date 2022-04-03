import click
import json
import math

import src.database.artifacts as artifact_database


@click.command()
@click.option('-i', '--input-file', required=True, type=str, help='Specify input file in GOOD format.')
@click.option('-v', '--verbose', count=True, help='Make the operation more talkative.')
def main(input_file, verbose):
    with open(input_file) as good_file:
        good = json.load(good_file)

    good_artifact_list = [artifact for artifact in good['artifacts'] if artifact['rarity'] == 5]

    check_for_null_on_the_first_three_sub_stats(good_artifact_list, verbose)
    check_for_null_on_forth_sub_stat_for_upgraded_artifact(good_artifact_list, verbose)
    check_max_rarity_for_artifact_sets(good_artifact_list, verbose)
    check_invalid_artifact_sets(good_artifact_list, verbose)


def print_header(message, good_artifact_list, verbose=1):
    if not len(good_artifact_list):
        return

    verbose_level = min(verbose - 1, 2)
    verbose_info = [
        ['Id', 'setKey'],
        ['Id', 'setKey', 'soltKey', 'mainStatKey', 'level'],
        good_artifact_list[0].keys()
    ]

    formatted_artifact_list = []
    for good_artifact in good_artifact_list:
        formatted_artifact_list.append({k: v for k, v in good_artifact.items() if k in verbose_info[verbose_level]})

    column_size = 8
    for formatted_artifact in formatted_artifact_list:
        formatted_artifact['line'] = math.floor((formatted_artifact['Id'] / column_size) + 1)
        formatted_artifact['column'] = (formatted_artifact['Id'] % column_size) + 1

    print('-' * len(message))
    print(message)
    print('Finds: ', len(good_artifact_list))
    print('-' * len(message))
    print(*formatted_artifact_list, sep='\n')


def check_for_null_on_the_first_three_sub_stats(good_artifact_list, verbose):
    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        sub_stat_keys = [sub_stat['key'] for sub_stat in good_artifact['substats'][0:3]]
        if None in sub_stat_keys:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check for null on the first three sub stats',
        artifacts_with_problem,
        verbose
    )


def check_for_null_on_forth_sub_stat_for_upgraded_artifact(good_artifact_list, verbose):
    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        rank = math.floor(good_artifact['level'] / 4)
        if rank > 1 and good_artifact['substats'][3]['key'] is None:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check for null on forth sub stat for upgraded artifact',
        artifacts_with_problem,
        verbose
    )


def check_max_rarity_for_artifact_sets(good_artifact_list, verbose):
    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        if good_artifact['setKey'] in artifact_database.rarity_four and good_artifact['rarity'] > 4:
            artifacts_with_problem.append(good_artifact)
        if good_artifact['setKey'] in artifact_database.rarity_three and good_artifact['rarity'] > 3:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check max rarity for artifact sets',
        artifacts_with_problem,
        verbose
    )


def check_invalid_artifact_sets(good_artifact_list, verbose):
    artifacts_with_problem = []
    for good_artifact in good_artifact_list:
        if good_artifact['setKey'] not in artifact_database.set_key_order:
            artifacts_with_problem.append(good_artifact)

    print_header(
        'Check invalid artifact sets',
        artifacts_with_problem,
        verbose
    )


if __name__ == '__main__':
    main()
