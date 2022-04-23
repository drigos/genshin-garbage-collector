Genshin Garbage Collector (G2C)
===============================

Intro
-----

The purpose of this project is to define rules to assess the quality and potential of each artifact allowing for a simpler exclusion of bad artifacts.

### Why use?

Your inventory is always full and you don't have the patience to choose which artifacts to discard.

You want to use wider filters to generate your build, and it's taking hours.

### How it works?

```
+------------------+    +------+    +---------------+    +-----+    +-------------------+
| Inventory Kamera | -> | GOOD | -> | g2c-validator | -> | g2c | -> | Genshin Optimizer |
+------------------+    +------+    +---------------+    +-----+    +-------------------+
                                          /\  ||
                                          ||  \/
                                    +---------------+
                                    |  JSON editor  |
                                    +---------------+
```

- [Inventory Kamera](https://github.com/Andrewthe13th/Inventory_Kamera)
- [GOOD](https://frzyc.github.io/genshin-optimizer/#/doc/)
- [Genshin Optimizer](https://frzyc.github.io/genshin-optimizer/#/)

## Builds

The builds contain two main components: 1) the **filters**; and 2) the **weights** of each sub stats.

Filters are used to limit the artifacts that will be evaluated. Then each artifact receives a score according to the sub stats present.

Undeclared sub stats will be considered as zero.

The weights are normalized when evaluating the artifact score ensuring that every artifact can get points from 0 to 1.

For simplicity's sake, we've abstracted the configuration by creating builds with the relevant artifacts for each character. This ensures that any artifact relevant to a character is preserved.

Each artifact can contain 0 to N scores according to how many builds adhere to it. Additionally, the best score is highlighted in the artifact attributes (in G2C format).

### Output formats

- G2C (Genshin Garbage Collector): used to compute build and scores
- GOOD (Genshin Open Object Description): de facto standard in Genshin community
- Count: amount artifacts returned

### Lock attribute

This attribute indicates the artifacts that must be kept.

### List modes

- `keep`: display only artifacts that must be kept (locked)
- `discard`: display only artifacts that must be discarded (unlocked)
- `all`: display all artifacts (locked and unlocked)

### Filters

Filters are an additional layer for excluding artifacts, allowing you to evaluate artifacts by their best score.

Filters contain two main components: 1) the **selectors**; and 2) the **actions**.

Selectors are a comma-separated list of key and value. Below is a list of supported keys and values:

- `set_key`: [GOOD-like values](https://frzyc.github.io/genshin-optimizer/#/doc/)
- `slot_key`: [GOOD-like values](https://frzyc.github.io/genshin-optimizer/#/doc/)
- `main_stat_key`: [GOOD-like values](https://frzyc.github.io/genshin-optimizer/#/doc/)
- `rarity`: `1-5`
- `level`: `0-20`
- `rank`: `0-5` (rank is `floor(level/4)`, i.e. the number of additional rolls an artifact got by leveling)

_*Only artifacts matched by the selector will be filtered._  
_*Any artifact that don't match the selector will be preserved._

It is possible to use a wildcard character to select all artifacts for filtering, i.e. `*:*`.

It is possible to use a semicolon-separated list to specify more than one value for the selector.

The actions will effectively filter the list of artifacts and can be as follows:

- threshold (`t`): minimum score threshold to keep artifacts (`float`).
- best score (`b`): select the N best artifacts (`int`).

### Groups

As an alternative to filters, you can use groupings to limit the amount of artifacts kept in each group.

The same filter selector keys apply here (except the wildcard character).

### Sort

After all filters are applied it is possible to sort the list of artifacts.

Sort contain two main components: 1) the **key**; and 2) the **order**.

Below is a list of supported keys:

- `set_key`
- `slot_key`
- `main_stat_key`
- `rarity`
- `level`
- `rank`
- `best_score`
- `refer_id`

And as for the order, the possible parameters are:

- `asc`
- `desc`

If not specified an order, asc is assumed.

**Special order keys**

By default, sorting use alphabetical character order, but for some keys Genshin's internal order used.
The purpose of this is to facilitate the mapping between the artifacts exported by G2C and the game.

Below is a list of keys don't use alphabetical order:

- `set_key`
- `slot_key`

**Genshin order**

This section explains the game order if you want to order the output of artifacts exported by this program in the same way.

- `rarity:desc`
- `level:desc`
- `set_key:asc` (specific Genshin order; non-alphabetic order)
- `slot_key:asc` (specific Genshin order; non-alphabetic order)
- Original artifact sub stats amount (it would be necessary to calculate the number of sub stat rolls based on the known values of each sub stat)
- Artifact acquisition date (we cannot obtain this information)

For the last two ordering criteria we suggest using the `best_score`.

Alternatively, the Inventory Kamera adds an identifier (`refer_id`) to the artifact based on the order of collection which can be used to achieve the exact same ordering as in the game. However, when importing into Genshin Optimizer this identifier is removed.

How to run
----------

```
source venv/bin/activate
pip install -r requirements.txt
python validator.py -i ~/good-full.json -vvv
python main.py -i '~/good-full.json' -o good > ~/good-filtered.json
```

### Input file

Specify input file in GOOD format.

```
-i/--input-file input_file
```

**Example:**

```
-i './good.json'
```

### Output format

Specify output format (default: g2c).

```
-o/--output-format [g2c|count|good]
```

### List mode

Specify which artifacts to show (default: keep).

```
-k/--keep
-d/--discard
-a/--all
```

### Weak flag

Display artifacts that are not at the maximum rarity allowed by the set.

```
-w/--weak
```

### Filters

Filter artifacts according to defined rules.  

```
-f/--filter selector_list=action
  selector_list = selector_key:selector_value[,selector_key:selector_value]
  action = action_type:action_value
```

**Example 1:** keep artifacts above score `0.3`  

```
-f '*:*=t:0.3'
```

**Example 2:** use different score based on artifact rank  

```
-f 'rank:0=t:0.15' -f 'rank:1=t:0.20' -f 'rank:2=t:0.25' -f 'rank:3=t:0.30' -f 'rank:4=t:0.35' -f 'rank:5=t:0.40'
-f 'rank:0=t:0.20' -f 'rank:1=t:0.30' -f 'rank:2=t:0.40' -f 'rank:3=t:0.45' -f 'rank:4=t:0.50' -f 'rank:5=t:0.55'
```

**Example 3:** keep artifacts above score `0.4` among `Gladiators Finale` and `Wanderers Troupe` whose rank is between `0` and `2` 

```
-f 'set_key:[GladiatorsFinale,WanderersTroupe],rank:[0,1,2]=t:0.4'
```

**Example 4:** keep the `700` best artifacts  

```
-f '*:*=b:700'
```

**Example 5:** keep the `5` best `plume` from the `Pale Flame` artifact  

```
-f 'set_key:PaleFlame,slot_key:plume=b:5'
```

**Example 6:** keep the `20` best artifacts among `Crimson Witch Of Flames` and `Shimenawas Reminiscence` whose rank is between `0` and `3`  

```
-f 'set_key:[CrimsonWitchOfFlames,ShimenawasReminiscence],rank:[0,1,2,3]=b:20'
```

### Groups

Keeps only N artifacts in each group.

```
-g/--group group_key_list=amount
  group_key_list = set_key,slot_key,main_stat_key,rarity,level,rank
  amount = integer
```

**Examples:**

```
-g 'set_key=25'  # keep the 25 best artifacts each set
-g 'set_key,slot_key=5'  # keep the 5 best artifacts each set and slot
-g 'set_key,slot_key,rank=1'  # keep the best artifact each set, slot and rank
```

### Sort

```
-s/--sort sort_key:sort_order[,sort_key:sort_order]
```

**Examples:**

```
-s 'best_score'  # sort artifacts from highest to lowest based on best_score attribute
-s 'best_score:desc'  # sort artifacts from highest to lowest based on best_score attribute
-s 'best_score:asc'  # sort artifacts from lowest to highest based on best_score attribute
-s 'level:asc,best_score:desc'  # sort artifacts ascending by level and descending by best_score attribute
-s 'rarity:desc,level:desc,set_key,slot_key,best_score:desc'  # genshin inventory order (almost) 
-s 'refer_id'  # genshin inventory order (when using data exported from Inventory Kamera) 
```

Rarity 5 Artifact Validator
---------------------------

- Check for null on the first three sub stats
- Check for null on forth sub stat for upgraded artifact
- Check max rarity for artifact sets
- Check invalid artifact sets

How to contribute
-----------------

## Getting started

```shell
source venv/bin/activate
pip install -r requirements.txt
python main.py -i '~/good.json'
```

## JSON Validator

```shell
jq . builds/**/*.json > /dev/null 2>&1; echo $?
```

## Artifact formats

- GOOD (Genshin Open Object Description)
- G2C (Genshin Garbage Collector)

## Artifact wrappers

- List: `[artifact]`
- Set/Slot format: `{ set_key: { slot_key: [artifact] } }`
- ID format: `{ id: artifact }`

## Extra

```shell
# Follow in order listed on Genshin to see which artifacts can be deleted
python main.py -i 'good/genshinData_GOOD.json' -o g2c -aw | jq '[.[] | {rarity,level,rank,main_stat_key,set_key,slot_key,best_score,best_build,refer_id,location,lock,sub_stats}] | sort_by(.refer_id)' > output/all.json

# To reduce a specific set (e.g. WanderersTroupe or GladiatorsFinale), evaluate total amount...
cat output/all.json | jq '[.[] | select(.set_key == "WanderersTroupe")] | length'
# ...and then create threshold for each rank until you find a satisfactory amount to remove...
cat output/all.json | jq '[.[] | select(.set_key == "WanderersTroupe") | select((.best_score == 0) or (.rank == 0 and .best_score < 0.15) or (.rank == 1 and .best_score < 0.20) or (.rank == 2 and .best_score < 0.25) or (.rank == 3 and .best_score < 0.30) or (.rank == 4 and .best_score < 0.35) or (.rank == 5 and .best_score < 0.40))] | length'
# ...finally get a list of artifacts with the same filter used in the previous command
cat output/all.json | jq '[.[] | select(.set_key == "WanderersTroupe") | select((.best_score == 0) or (.rank == 0 and .best_score < 0.15) or (.rank == 1 and .best_score < 0.20) or (.rank == 2 and .best_score < 0.25) or (.rank == 3 and .best_score < 0.30) or (.rank == 4 and .best_score < 0.35) or (.rank == 5 and .best_score < 0.40))]' > output/wander.json

# To reduce a specific slot (e.g. flower or plume), evaluate total amount...
cat output/all.json | jq '[.[] | select(.slot_key == "plume")] | length'
# ...and then create threshold for each rank until you find a satisfactory amount to remove to remove...
cat output/all.json | jq '[.[] | select(.slot_key == "plume") | select((.best_score == 0) or (.rank == 0 and .best_score < 0.15) or (.rank == 1 and .best_score < 0.20) or (.rank == 2 and .best_score < 0.25) or (.rank == 3 and .best_score < 0.30) or (.rank == 4 and .best_score < 0.35) or (.rank == 5 and .best_score < 0.40))] | length'
# ...finally get a list of artifacts with the same filter used in the previous command
cat output/all.json | jq '[.[] | select(.slot_key == "plume") | select((.best_score == 0) or (.rank == 0 and .best_score < 0.15) or (.rank == 1 and .best_score < 0.20) or (.rank == 2 and .best_score < 0.25) or (.rank == 3 and .best_score < 0.30) or (.rank == 4 and .best_score < 0.35) or (.rank == 5 and .best_score < 0.40))]' > output/plume.json

# To reduce artifact-based builds (e.g. "Circlet - Rare Stats", "Goblet - Elemental DMG", "Sands - Elemental Mastery")...
# ...first, create file with all artifacts and build_score attributes
python main.py -i 'good/genshinData_GOOD.json' -o g2c -aw | jq '[.[] | {rarity,level,rank,main_stat_key,set_key,slot_key,best_score,best_build,refer_id,location,lock,sub_stats,build_score}] | sort_by(.refer_id)' > output/all-with-build-score.json
# ...then evaluate total amount...
cat output/all-with-build-score.json | jq '[.[] | select(.best_build == "Circlet - Rare Stats")] | length'
# ...and then create threshold for each rank until you find a satisfactory amount to remove...
cat output/all-with-build-score.json | jq '[.[] | select(.best_build == "Circlet - Rare Stats") | select((.best_score == 0) or (.rank == 0 and .best_score < 0.15) or (.rank == 1 and .best_score < 0.20) or (.rank == 2 and .best_score < 0.25) or (.rank == 3 and .best_score < 0.30) or (.rank == 4 and .best_score < 0.35) or (.rank == 5 and .best_score < 0.40))] | length'
# ...finally get a list of artifacts with the same filter used in the previous command
cat output/all-with-build-score.json | jq '[.[] | select(.best_build == "Circlet - Rare Stats") | select((.best_score == 0) or (.rank == 0 and .best_score < 0.15) or (.rank == 1 and .best_score < 0.20) or (.rank == 2 and .best_score < 0.25) or (.rank == 3 and .best_score < 0.30) or (.rank == 4 and .best_score < 0.35) or (.rank == 5 and .best_score < 0.40))]' > output/circlet.json
# >>>> Verify whether these artifacts not match with other build thresholds <<<<

# Find better artifacts to upgrade (disable build artifact-*.json)
cat output/all.json | jq '[.[] | select(.rank != 5)] | sort_by(.best_score) | reverse' > output/upgrade.json
# To upgrade artifacts from a specific set (disable build artifact-*.json)
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.set_key == "TenacityOfTheMillelith")] | sort_by(.best_score) | reverse' > output/millelith.json
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.set_key == "PaleFlame")] | sort_by(.best_score) | reverse' > output/pale.json
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.set_key == "EmblemOfSeveredFate")] | sort_by(.best_score) | reverse' > output/emblem.json
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.set_key == "HuskOfOpulentDreams")] | sort_by(.best_score) | reverse' > output/husk.json
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.set_key == "OceanHuedClam")] | sort_by(.best_score) | reverse' > output/ocean.json
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.set_key == "VermillionHereafter")] | sort_by(.best_score) | reverse' > output/vermillion.json

# To upgrade artifacts from a specific build (disable build artifact-*.json)
cat output/all.json | jq '[.[] | select(.rank != 5) | select(.best_build == "Eula - DPS")] | sort_by(.best_score) | reverse' > output/eula-dps.json
```
