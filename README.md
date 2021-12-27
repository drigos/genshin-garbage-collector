# Genshin Garbage Collector

## CLI Parameters

### Filter

Filter artifacts according to defined rules.  
_*Only artifacts matched by the selector will be filtered._  
_*Any artifact that don't match the selector will be preserved._

```
-f selector_list=filter_list
  selector_list = selector_key:selector_value[,selector_key:selector_value]
    selector_key = set_key,slot_key,main_stat_key,rarity,level,rank
    selector_value = GOOD-like
  filter_list = filter_type:filter_value[,filter_type:filter_value]
    filter_type = t (stands for threshold) and b (stands for best)
    filter_value = float (when type is `t`) or integer (when type is `b`)
```

See [GOOD format description](https://frzyc.github.io/genshin-optimizer/#/doc/) for reference about the possible selector values.

**Example 1:** keep artifacts above score `0.3`  
```
-f '*=t:0.3'
```

**Example 2:** use different score based on artifact rank  
```
-f 'rank:0=t:0.2' -f 'rank:1=t:0.25' -f 'rank:2=t:0.3' -f 'rank:3=t:0.35' -f 'rank:4=t:0.4' -f 'rank:5=t:0.5'
```

**Example 3:** keep artifacts above score `0.4` among `Gladiators Finale` and `Wanderers Troupe` whose rank is between `0` and `2` 
```
-f 'set_key:[GladiatorsFinale,WanderersTroupe],rank:[0,1,2]=t:0.4'
```

**Example 4:** keep the `700` best artifacts  
```
-f *=b:700
```

**Example 5:** keep the `5` best `plume` from the `Pale Flame` artifact  
```
-f set_key:PaleFlame,slot_key:plume=b:5]
```

**Example 6:** keep the `20` best artifacts among `Crimson Witch Of Flames` and `Shimenawas Reminiscence` whose rank is between `0` and `3`  
```
-f set_key:[CrimsonWitchOfFlames,ShimenawasReminiscence],rank:[0,1,2,3]=b:20
```

### Group

Keep the N best artifacts from each group defined in rules.  
_*All artifacts will be pruned._

```
-g group_key_list=amount
  group_key_list = set_key,slot_key,main_stat_key,rarity,level,rank
  amount = integer
```

**Examples:**
```
  -g set_key=25  # keep the 25 best artifacts each set
  -g set_key,slot_key=5  # keep the 5 best artifacts each set and slot
  -g set_key,slot_key,rank=1  # keep the best artifact each set, slot and rank
```

### Sort artifacts

```
-s sort_key_list
  sort_key_list = set_key,slot_key,main_stat_key,rarity,level,rank,best_score
```

**Examples:**
```
  -s best_score  # sort artifacts from highest to lowest based on best_score attribute
  -s best_score:desc  # sort artifacts from highest to lowest based on best_score attribute
  -s best_score:asc  # sort artifacts from lowest to highest based on best_score attribute
  -s level:asc,best_score:desc  # sort artifacts ascending by level and descending by best_score attribute
```

### Export

Export file in GOOD format
```
-e destination_file
  destination_file = path to file
```

**Examples:**
```
  -e ./output.json
```

## JSON Validator

```shell script
jq . builds/*.json > /dev/null 2>&1; echo $?
```
