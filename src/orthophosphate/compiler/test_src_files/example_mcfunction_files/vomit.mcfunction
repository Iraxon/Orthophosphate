# From Lethal Autonomous Weapon, which adds an infectious
# enemy to the game

# This function controls an attack used by some
# infected mobs

# Notice how terrible this looks to write; this is why we're making
# a compiler

# I have this here primarily so I can think about what I might
# want to add --COMMANDO66

scoreboard objectives add LAWRN__atk_cd dummy
scoreboard players add @e[tag=LAWRN__selected] LAWRN__atk_cd 0

execute as @e[tag=LAWRN__selected,scores={LAWRN__atk_cd=0}] at @s anchored eyes positioned ~ ~ ~ if entity @e[sort=nearest,limit=1,tag=LAWRN__target,distance=..12] run tag @s add LAWRN__attacking
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 at @e[tag=LAWRN__target,distance=..16] run damage @e[sort=nearest,limit=1,tag=LAWRN__target,distance=..0.01] 0 mob_attack by @s
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 run summon marker ~ ~ ~ {Tags:["LAWRN__summon_cloud"]}
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 run playsound minecraft:block.slime_block.place hostile @a ~ ~ ~ 1 0.5
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 run playsound minecraft:block.slime_block.hit hostile @a ~ ~ ~ 1 1
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 run playsound minecraft:entity.player.burp hostile @a ~ ~ ~ 1 0.5
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 run playsound minecraft:entity.villager.work_cleric hostile @a ~ ~ ~ 1 2
    execute as @e[tag=LAWRN__attacking] at @s anchored eyes positioned ^ ^ ^1 run playsound minecraft:block.lever.click hostile @a ~ ~ ~ 1 2
    scoreboard players set @e[tag=LAWRN__attacking] LAWRN__atk_cd 140
tag @e remove LAWRN__attacking

scoreboard players remove @e[tag=LAWRN__selected,scores={LAWRN__atk_cd=1..}] LAWRN__atk_cd 1
