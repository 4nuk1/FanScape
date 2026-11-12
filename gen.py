import json, os, random, struct, zlib, math
R = 'src/main/resources'
D = R + '/data/fanscape'
W = D + '/worldgen'
A = R + '/assets/fanscape'

def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

# ---------------- noises ----------------
def noise(name, first, amps): w(f'{W}/noise/{name}.json', {"firstOctave": first, "amplitudes": amps})
noise('rolling', -7, [1.0, 1.0, 0.5])
noise('cliff', -9, [1.0, 1.0, 0.5])
noise('ledge', -8, [1.0, 1.0])
noise('river', -11, [1.0, 0.4, 0.2])
noise('lake', -9, [1.0, 1.0, 0.5])
noise('temperature', -9, [1.0, 0.5, 0.5])
noise('humidity', -9, [1.0, 1.0, 0.5])
noise('detail', -4, [1.0, 1.0, 1.0])

# ---------------- density functions ----------------
def nz(n, y=0.0): return {"type": "minecraft:noise", "noise": f"fanscape:{n}", "xz_scale": 1.0, "y_scale": y}
def add(a, b): return {"type": "minecraft:add", "argument1": a, "argument2": b}
def mul(a, b): return {"type": "minecraft:mul", "argument1": a, "argument2": b}
def mn(a, b): return {"type": "minecraft:min", "argument1": a, "argument2": b}
def clamp(x, lo, hi): return {"type": "minecraft:clamp", "input": x, "min": lo, "max": hi}
def spline(coord, pts):
    return {"type": "minecraft:spline", "spline": {"coordinate": coord,
            "points": [{"location": float(l), "value": float(v), "derivative": 0.0} for l, v in pts]}}
def df(name, obj): w(f'{W}/density_function/{name}.json', obj)

df('y', {"type": "minecraft:y_clamped_gradient", "from_y": -64, "to_y": 320, "from_value": -64.0, "to_value": 320.0})
df('cliff_mask', nz('cliff'))
df('ledge_mask', nz('ledge'))
df('plateau', spline("fanscape:cliff_mask", [(-1, 0), (0.2, 0), (0.22, 110), (0.5, 125), (1, 150)]))
df('ledge', spline("fanscape:ledge_mask", [(-1, 0), (0.3, 0), (0.33, 30), (1, 30)]))
df('terrain', add(add(70.0, mul(8.0, nz('rolling'))), add("fanscape:plateau", "fanscape:ledge")))
df('river_bed', spline({"type": "minecraft:abs", "argument": nz('river')},
                       [(0, 40), (0.04, 48), (0.07, 62), (0.10, 90), (0.16, 300), (1, 300)]))
df('lake_bed', spline(nz('lake'), [(-1, 300), (0.4, 300), (0.5, 90), (0.58, 46), (1, 40)]))
df('height', {"type": "minecraft:cache_2d",
              "argument": mn(mn("fanscape:terrain", "fanscape:river_bed"), "fanscape:lake_bed")})
df('solidity', mul(0.1, add("fanscape:height", mul(-1.0, "fanscape:y"))))
df('final_density', {"type": "minecraft:interpolated",
                     "argument": clamp(add("fanscape:solidity", mul(0.12, nz('detail', 1.0))), -1.0, 1.0)})
df('initial_density', add("fanscape:solidity", 0.390625))
df('depth', clamp(mul(0.01, add("fanscape:height", mul(-1.0, "fanscape:y"))), -2.0, 2.0))
df('continents', clamp(mul(0.1, add("fanscape:height", -62.5)), -1.0, 1.0))
df('temperature', nz('temperature'))
df('humidity', nz('humidity'))

# ---------------- surface rule ----------------
def block(n): return {"type": "minecraft:block", "result_state": {"Name": n}}
def cond(c, t): return {"type": "minecraft:condition", "if_true": c, "then_run": t}
def seq(*r): return {"type": "minecraft:sequence", "sequence": list(r)}
top = {"type": "minecraft:stone_depth", "offset": 0, "surface_type": "floor", "add_surface_depth": False, "secondary_depth_range": 0}
sub = dict(top, add_surface_depth=True)
not_under_water = {"type": "minecraft:water", "offset": -1, "surface_depth_multiplier": 0, "add_stone_depth": False}
def biome_is(*b): return {"type": "minecraft:biome", "biome_is": list(b)}

surface = seq(
    cond({"type": "minecraft:vertical_gradient", "random_name": "minecraft:bedrock_floor",
          "true_at_and_below": {"above_bottom": 0}, "false_at_and_above": {"above_bottom": 5}}, block("minecraft:bedrock")),
    cond({"type": "minecraft:above_preliminary_surface"}, seq(
        cond(biome_is("fanscape:crystal_waters"), cond(sub, block("minecraft:sand"))),
        cond(biome_is("fanscape:crystal_wastes", "fanscape:crystal_peaks"), seq(
            cond(top, seq(cond(not_under_water, block("minecraft:snow_block")), block("minecraft:gravel"))),
            cond(sub, block("minecraft:calcite")))),
        cond(top, seq(cond(not_under_water, block("minecraft:grass_block")), block("minecraft:dirt"))),
        cond(sub, block("minecraft:dirt")))))

w(W + '/noise_settings/fanscape.json', {
    "sea_level": 63, "disable_mob_generation": False, "aquifers_enabled": False,
    "ore_veins_enabled": False, "legacy_random_source": False,
    "default_block": {"Name": "minecraft:stone"},
    "default_fluid": {"Name": "minecraft:water", "Properties": {"level": "0"}},
    "noise": {"min_y": -64, "height": 384, "size_horizontal": 1, "size_vertical": 2},
    "noise_router": {
        "barrier": 0.0, "fluid_level_floodedness": 0.0, "fluid_level_spread": 0.0, "lava": 0.0,
        "temperature": "fanscape:temperature", "vegetation": "fanscape:humidity",
        "continents": "fanscape:continents", "erosion": "fanscape:cliff_mask",
        "depth": "fanscape:depth", "ridges": 0.0,
        "initial_density_without_jaggedness": "fanscape:initial_density",
        "final_density": "fanscape:final_density",
        "vein_toggle": 0.0, "vein_ridged": 0.0, "vein_gap": 0.0},
    "spawn_target": [{"temperature": [-1, 1], "humidity": [-1, 1], "continentalness": [0.0, 1],
                      "erosion": [-1, 0.2], "depth": 0.0, "weirdness": [-1, 1], "offset": 0.0}],
    "surface_rule": surface})

# ---------------- configured features ----------------
def cf(name, type_, config): w(f'{W}/configured_feature/{name}.json', {"type": type_, "config": config})
leaf_props = {"distance": "1", "persistent": "true", "waterlogged": "false"}
def tree(name, style, log, leaves, lantern, minh, maxh, R, ch, tr, hang, hlen, lch):
    cf(name, 'fanscape:giant_tree', {
        "trunk": {"Name": log, "Properties": {"axis": "y"}},
        "leaves": {"Name": leaves, "Properties": leaf_props},
        "lantern": {"Name": lantern},
        "style": style, "min_height": minh, "max_height": maxh, "canopy_radius": R, "canopy_height": ch,
        "trunk_radius": tr, "hang": hang, "hang_length": hlen, "lantern_chance": lch})
CR = "fanscape:crystal_block"; SH = "minecraft:shroomlight"
tree('pink_umbrella', 'umbrella', 'minecraft:cherry_log', 'minecraft:cherry_leaves', CR, 26, 40, 12, 8, 3.3, 0, 0, 7)
tree('pink_bonsai', 'bonsai', 'minecraft:cherry_log', 'minecraft:cherry_leaves', CR, 20, 30, 11, 5, 2.0, 6, 4, 7)
tree('azure_bonsai', 'bonsai', 'minecraft:birch_log', 'fanscape:azure_leaves', CR, 22, 32, 11, 5, 2.2, 8, 5, 7)
tree('azure_gnarled', 'gnarled', 'minecraft:dark_oak_log', 'fanscape:azure_leaves', CR, 16, 26, 12, 6, 3.0, 3, 3, 4)
tree('teal_tiered', 'tiered', 'minecraft:jungle_log', 'fanscape:teal_leaves', CR, 30, 46, 9, 3, 1.3, 0, 0, 6)
tree('ember_banyan', 'banyan', 'minecraft:birch_log', 'fanscape:ember_leaves', SH, 14, 20, 12, 7, 4.5, 14, 10, 5)
tree('scarlet_tall', 'tall', 'minecraft:birch_log', 'fanscape:scarlet_leaves', CR, 28, 44, 9, 3, 1.2, 0, 0, 6)
tree('scarlet_weeping', 'gnarled', 'minecraft:dark_oak_log', 'fanscape:scarlet_leaves', SH, 16, 26, 12, 6, 3.0, 18, 12, 3)
tree('small_pink', 'umbrella', 'minecraft:cherry_log', 'minecraft:cherry_leaves', CR, 7, 11, 4, 3, 0.7, 0, 0, 8)
tree('small_azure', 'umbrella', 'minecraft:birch_log', 'fanscape:azure_leaves', CR, 7, 11, 4, 3, 0.7, 0, 0, 8)
tree('small_scarlet', 'umbrella', 'minecraft:birch_log', 'fanscape:scarlet_leaves', CR, 7, 12, 4, 3, 0.7, 0, 0, 8)
for n in ['boulder', 'crystal_spire', 'crystal_clusters', 'canopy_light']:
    cf(n, 'fanscape:' + n, {})

def patch(blocks, tries):
    return {"tries": tries, "xz_spread": 7, "y_spread": 3, "feature": {
        "feature": {"type": "minecraft:simple_block", "config": {"to_place": {
            "type": "minecraft:weighted_state_provider",
            "entries": [{"weight": wt, "data": {"Name": b}} for b, wt in blocks]}}},
        "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {
            "type": "minecraft:all_of", "predicates": [
                {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                {"type": "minecraft:matching_blocks", "offset": [0, -1, 0], "blocks": ["minecraft:grass_block"]}]}}]}}
cf('flowers', 'minecraft:random_patch', patch([("minecraft:poppy", 2), ("minecraft:dandelion", 2), ("minecraft:azure_bluet", 2),
    ("minecraft:cornflower", 3), ("minecraft:allium", 1), ("minecraft:pink_tulip", 2), ("minecraft:oxeye_daisy", 2)], 24))
cf('grass', 'minecraft:random_patch', patch([("minecraft:short_grass", 1)], 48))

# ---------------- placed features ----------------
SURF = [{"type": "minecraft:in_square"}, {"type": "minecraft:heightmap", "heightmap": "WORLD_SURFACE_WG"}, {"type": "minecraft:biome"}]
def pf(name, feature, pre): w(f'{W}/placed_feature/{name}.json', {"feature": f"fanscape:{feature}", "placement": pre})
def rare(n): return [{"type": "minecraft:rarity_filter", "chance": n}] + SURF
def count(n): return [{"type": "minecraft:count", "count": n}] + SURF
for n, r in [('pink_umbrella', 6), ('pink_bonsai', 9), ('azure_bonsai', 3), ('azure_gnarled', 3), ('teal_tiered', 6),
             ('ember_banyan', 10), ('scarlet_weeping', 3)]:
    pf(n, n, rare(r))
pf('pink_umbrella_rare', 'pink_umbrella', rare(12))
pf('teal_tiered_rare', 'teal_tiered', rare(12))
pf('ember_banyan_rare', 'ember_banyan', rare(20))
pf('scarlet_tall', 'scarlet_tall', count(3))
pf('small_pink', 'small_pink', count(2))
pf('small_azure', 'small_azure', count(2))
pf('small_scarlet', 'small_scarlet', count(4))
pf('boulders', 'boulder', rare(2))
pf('boulders_few', 'boulder', rare(5))
pf('spires', 'crystal_spire', rare(6))
pf('spires_dense', 'crystal_spire', rare(3))
pf('surface_clusters', 'crystal_clusters', count(3))
pf('cave_clusters', 'crystal_clusters', [
    {"type": "minecraft:count", "count": 40}, {"type": "minecraft:in_square"},
    {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform",
        "min_inclusive": {"absolute": -50}, "max_inclusive": {"absolute": 90}}},
    {"type": "minecraft:biome"}])
pf('canopy_light', 'canopy_light', SURF)
pf('flowers', 'flowers', count(2))
pf('grass', 'grass', count(3))

# ---------------- biomes ----------------
ORES = ["ore_dirt", "ore_gravel", "ore_granite_upper", "ore_granite_lower", "ore_diorite_upper", "ore_diorite_lower",
        "ore_andesite_upper", "ore_andesite_lower", "ore_tuff", "ore_coal_upper", "ore_coal_lower", "ore_iron_upper",
        "ore_iron_middle", "ore_iron_small", "ore_gold", "ore_redstone", "ore_diamond", "ore_lapis", "ore_copper"]
def mc(l): return ["minecraft:" + x for x in l]
def fa(l): return ["fanscape:" + x for x in l]

def spawn(t, wt, mn_, mx): return {"type": "minecraft:" + t, "weight": wt, "minCount": mn_, "maxCount": mx}
MONSTERS = [spawn("spider", 100, 4, 4), spawn("zombie", 95, 4, 4), spawn("skeleton", 100, 4, 4),
            spawn("creeper", 100, 4, 4), spawn("slime", 100, 4, 4), spawn("enderman", 10, 1, 4), spawn("witch", 5, 1, 1)]
FARM = [spawn("sheep", 12, 4, 4), spawn("pig", 10, 4, 4), spawn("chicken", 10, 4, 4), spawn("cow", 8, 4, 4)]

def biome(name, temp, down, sky, fog, water, wfog, grass, foliage, feats, creature=None, extra=None):
    f = [[] for _ in range(11)]
    for step, lst in feats.items(): f[step] = lst
    spawners = {k: [] for k in ["monster", "creature", "ambient", "axolotls", "underground_water_creature",
                                "water_creature", "water_ambient", "misc"]}
    spawners["monster"] = MONSTERS
    spawners["creature"] = creature if creature is not None else FARM
    if extra: spawners.update(extra)
    eff = {"fog_color": fog, "sky_color": sky, "water_color": water, "water_fog_color": wfog}
    if grass is not None: eff["grass_color"] = grass
    if foliage is not None: eff["foliage_color"] = foliage
    w(f'{W}/biome/{name}.json', {
        "temperature": temp, "downfall": down, "has_precipitation": True, "effects": eff,
        "spawners": spawners, "spawn_costs": {},
        "carvers": {"air": ["minecraft:cave", "minecraft:cave_extra_underground", "minecraft:canyon"]},
        "features": f})

UND = {6: mc(ORES), 8: mc(["spring_water", "spring_lava"])}
def feats(veg, extra=None):
    d = dict(UND); d[9] = veg; d[10] = fa(["canopy_light"]) + (extra or []); return d

biome('verdant_plains', 0.8, 0.4, 0x9EC8FF, 0xD8E4FF, 0x3FA9F5, 0x1B5FA8, 0x8FD65B, 0x6CCB4F,
      feats(fa(["pink_umbrella", "pink_bonsai", "teal_tiered_rare", "ember_banyan_rare", "small_pink", "small_azure", "boulders", "flowers", "grass"])),
      creature=FARM + [spawn("horse", 5, 2, 6)])
biome('azure_forest', 0.7, 0.8, 0x7FA8FF, 0xBFD0FF, 0x2E7DFF, 0x143A8A, 0x5FD08A, 0x4BC27A,
      feats(fa(["azure_bonsai", "azure_gnarled", "teal_tiered", "pink_umbrella_rare", "small_azure", "boulders_few", "flowers", "grass"])))
biome('skyreach_plateau', 0.6, 0.5, 0xA8B8FF, 0xE0D8FF, 0x4AB8F0, 0x1D5F9E, 0x9BD86A, 0x7ACB58,
      feats(fa(["pink_umbrella", "azure_bonsai", "ember_banyan", "teal_tiered", "small_pink", "boulders", "flowers", "grass"])))
biome('red_forest', 0.9, 0.7, 0xD8789A, 0xF0B0C4, 0x6C7BE0, 0x3A3F9A, 0xEB5472, 0xEB5472,
      feats(fa(["scarlet_tall", "scarlet_weeping", "small_scarlet", "boulders_few", "flowers", "grass"])))
CRY = {"grass": 0xB9C8F0, "foliage": 0xA9B8E8}
biome('crystal_wastes', 0.0, 0.5, 0x9B7BFF, 0xC9B3FF, 0x7A6BFF, 0x3B2A8F, CRY["grass"], CRY["foliage"],
      feats(fa(["spires", "surface_clusters", "boulders_few"]), mc(["freeze_top_layer"])),
      creature=[spawn("rabbit", 10, 2, 3), spawn("polar_bear", 1, 1, 2)])
biome('crystal_peaks', 0.0, 0.5, 0x8A5CFF, 0xBFA0FF, 0x7A6BFF, 0x3B2A8F, CRY["grass"], CRY["foliage"],
      feats(fa(["spires_dense", "surface_clusters", "boulders_few"]), mc(["freeze_top_layer"])),
      creature=[spawn("goat", 5, 1, 3)])
biome('crystal_waters', 0.5, 0.5, 0x8FC8FF, 0xD8E4FF, 0x3DD9E8, 0x1A7F99, None, None,
      {6: mc(ORES), 8: mc(["spring_water"])}, creature=[],
      extra={"water_creature": [spawn("squid", 2, 1, 4)],
             "water_ambient": [spawn("cod", 15, 3, 6), spawn("salmon", 15, 1, 5)]})
biome('crystal_caverns', 0.5, 0.5, 0x000000, 0x1A0B3A, 0x7C4DFF, 0x2B1B6B, None, None,
      {2: mc(["amethyst_geode"]), 6: mc(ORES), 8: mc(["spring_water", "spring_lava"]), 9: fa(["cave_clusters"])},
      creature=[], extra={"ambient": [spawn("bat", 10, 8, 8)]})

# ---------------- world preset ----------------
def P(t, h, c, e, d): return {"temperature": t, "humidity": h, "continentalness": c, "erosion": e,
                              "depth": d, "weirdness": [-1, 1], "offset": 0.0}
LAND_D = [-2.0, 0.15]
biomes = [
    ("verdant_plains", P([-0.3, 0.3], [-1, 0.15], [-0.1, 1], [-1, 0.22], LAND_D)),
    ("azure_forest", P([-0.3, 0.3],
 [0.15, 1], [-0.1, 1], [-1, 0.22], LAND_D)),
    ("red_forest", P([0.3, 1], [-1, 1], [-0.1, 1], [-1, 0.22], LAND_D)),
    ("crystal_wastes", P([-1, -0.3], [-1, 1], [-0.1, 1], [-1, 0.22], LAND_D)),
    ("skyreach_plateau", P([-0.3, 1], [-1, 1], [-0.1, 1], [0.22, 1], LAND_D)),
    ("crystal_peaks", P([-1, -0.3], [-1, 1], [-0.1, 1], [0.22, 1], LAND_D)),
    ("crystal_waters", P([-1, 1], [-1, 1], [-1, -0.1], [-1, 1], [-2.0, 0.1])),
    ("crystal_caverns", P([-1, 1], [-1, 1], [-1, 1], [-1, 1], [0.2, 2.0])),
]
w(W + '/world_preset/fanscape.json', {"dimensions": {
    "minecraft:overworld": {"type": "minecraft:overworld", "generator": {
        "type": "minecraft:noise", "settings": "fanscape:fanscape",
        "biome_source": {"type": "minecraft:multi_noise",
                         "biomes": [{"biome": "fanscape:" + n, "parameters": p} for n, p in biomes]}}},
    "minecraft:the_nether": {"type": "minecraft:the_nether", "generator": {
        "type": "minecraft:noise", "settings": "minecraft:nether",
        "biome_source": {"type": "minecraft:multi_noise", "preset": "minecraft:nether"}}},
    "minecraft:the_end": {"type": "minecraft:the_end", "generator": {
        "type": "minecraft:noise", "settings": "minecraft:end", "biome_source": {"type": "minecraft:the_end"}}}}})
w(R + '/data/minecraft/tags/worldgen/world_preset/normal.json', {"replace": False, "values": ["fanscape:fanscape"]})

# ---------------- tags, loot, recipes ----------------
w(R + '/data/minecraft/tags/block/mineable/pickaxe.json', {"replace": False, "values": ["fanscape:crystal_block", "fanscape:luminous_crystal"]})
w(R + '/data/minecraft/tags/block/mineable/hoe.json', {"replace": False, "values": ["fanscape:azure_leaves"]})
w(R + '/data/minecraft/tags/block/leaves.json', {"replace": False, "values": ["fanscape:azure_leaves"]})
w(R + '/data/minecraft/tags/item/leaves.json', {"replace": False, "values": ["fanscape:azure_leaves"]})
def loot(n, drop, cond_=None):
    entry = {"type": "minecraft:item", "name": drop}
    w(f'{D}/loot_table/blocks/{n}.json', {"type": "minecraft:block", "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
        "entries": [entry], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
loot('crystal_block', 'fanscape:crystal_block')
loot('luminous_crystal', 'fanscape:luminous_crystal')
# листва: дроп только с ножниц/шёлка -> упрощённо: с ножниц
w(f'{D}/loot_table/blocks/azure_leaves.json', {"type": "minecraft:block", "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
    "entries": [{"type": "minecraft:item", "name": "fanscape:azure_leaves"}],
    "conditions": [{"condition": "minecraft:match_tool", "predicate": {"items": ["minecraft:shears"]}}]}]})
w(f'{D}/recipe/crystal_block.json', {"type": "minecraft:crafting_shaped", "pattern": ["##", "##"],
    "key": {"#": {"item": "fanscape:luminous_crystal"}}, "result": {"id": "fanscape:crystal_block", "count": 1}})
w(f'{D}/recipe/luminous_crystal.json', {"type": "minecraft:crafting_shapeless",
    "ingredients": [{"item": "fanscape:crystal_block"}], "result": {"id": "fanscape:luminous_crystal", "count": 4}})

# ---------------- assets ----------------
FACE = {"facing=up": {}, "facing=down": {"x": 180}, "facing=north": {"x": 90}, "facing=east": {"x": 90, "y": 90},
        "facing=south": {"x": 90, "y": 180}, "facing=west": {"x": 90, "y": 270}}
w(f'{A}/blockstates/luminous_crystal.json', {"variants": {k: dict({"model": "fanscape:block/luminous_crystal"}, **v) for k, v in FACE.items()}})
w(f'{A}/blockstates/crystal_block.json', {"variants": {"": {"model": "fanscape:block/crystal_block"}}})
w(f'{A}/blockstates/azure_leaves.json', {"variants": {"": {"model": "fanscape:block/azure_leaves"}}})
w(f'{A}/models/block/luminous_crystal.json', {"parent": "minecraft:block/cross", "render_type": "minecraft:cutout",
    "textures": {"cross": "fanscape:block/luminous_crystal"}})
w(f'{A}/models/block/crystal_block.json', {"parent": "minecraft:block/cube_all", "textures": {"all": "fanscape:block/crystal_block"}})
w(f'{A}/models/block/azure_leaves.json', {"parent": "minecraft:block/leaves", "textures": {"all": "fanscape:block/azure_leaves"}})
w(f'{A}/models/item/luminous_crystal.json', {"parent": "minecraft:item/generated", "textures": {"layer0": "fanscape:block/luminous_crystal"}})
w(f'{A}/models/item/crystal_block.json', {"parent": "fanscape:block/crystal_block"})
w(f'{A}/models/item/azure_leaves.json', {"parent": "fanscape:block/azure_leaves"})

names = {"verdant_plains": ("Verdant Plains", "Цветущие равнины"), "azure_forest": ("Azure Forest", "Лазурный лес"),
         "skyreach_plateau": ("Skyreach Plateau", "Плато Небесного предела"), "crystal_wastes": ("Crystal Wastes", "Кристальные пустоши"),
         "crystal_peaks": ("Crystal Peaks", "Кристальные пики"), "crystal_waters": ("Crystal Waters", "Кристальные воды"),
         "crystal_caverns": ("Crystal Caverns", "Кристальные пещеры"),
         "red_forest": ("Red Forest", "Красный лес")}
en = {"block.fanscape.luminous_crystal": "Luminous Crystal", "block.fanscape.crystal_block": "Crystal Block",
      "block.fanscape.azure_leaves": "Azure Leaves", "itemGroup.fanscape": "FanScape", "generator.fanscape.fanscape": "FanScape"}
ru = {"block.fanscape.luminous_crystal": "Светящийся кристалл", "block.fanscape.crystal_block": "Блок кристалла",
      "block.fanscape.azure_leaves": "Лазурная листва", "itemGroup.fanscape": "FanScape", "generator.fanscape.fanscape": "FanScape"}
for k, (e, r) in names.items():
    en[f"biome.fanscape.{k}"] = e; ru[f"biome.fanscape.{k}"] = r
w(f'{A}/lang/en_us.json', en); w(f'{A}/lang/ru_ru.json', ru)

# ---------------- textures ----------------
def png(path, px):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = b''.join(b'\x00' + bytes(c for p in row for c in p) for row in px)
    def ch(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', 16, 16, 8, 6, 0, 0, 0))
                           + ch(b'IDAT', zlib.compress(raw, 9)) + ch(b'IEND', b''))
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

rng = random.Random(7)
pal = [(120, 70, 230), (150, 110, 255), (90, 200, 255), (190, 150, 255), (110, 90, 240), (140, 220, 255)]
seeds = [(rng.uniform(0, 16), rng.uniform(0, 16), i % len(pal)) for i in range(7)]
px = []
for y in range(16):
    row = []
    for x in range(16):
        ds = sorted((min((x - sx + dx) ** 2 + (y - sy + dy) ** 2 for dx in (-16, 0, 16) for dy in (-16, 0, 16)), c) for sx, sy, c in seeds)
        d1, c1 = ds[0]; d2 = ds[1][0]
        col = pal[c1]
        if math.sqrt(d2) - math.sqrt(d1) < 0.9: col = (235, 230, 255)
        elif rng.random() < 0.06: col = (255, 255, 255)
        row.append(col + (255,))
    px.append(row)
png(f'{A}/textures/block/crystal_block.png', px)

grid = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
for cx, hgt, hw in [(4, 9, 2.0), (12, 10, 2.5), (8, 14, 3.0)]:
    for y in range(16):
        rel = 15 - y
        if rel >= hgt: continue
        half = hw * (1 - rel / hgt) + 0.3
        for x in range(16):
            dx = x + 0.5 - cx
            if abs(dx) <= half:
                t = (dx + half) / (2 * half)
                col = lerp((90, 50, 200), (190, 160, 255), t)
                if abs(dx) > half - 0.7 and rel > 1: col = lerp(col, (240, 235, 255), 0.6)
                if abs(dx) < 0.6 and rel > 3: col = (230, 240, 255)
                grid[y][x] = col + (255,)
png(f'{A}/textures/block/luminous_crystal.png', grid)

rng = random.Random(11)
blues = [(30, 60, 220), (50, 90, 255), (20, 40, 170), (110, 150, 255), (40, 120, 255)]
px = []
for y in range(16):
    row = []
    for x in range(16):
        row.append((0, 0, 0, 0) if rng.random() < 0.12 else rng.choice(blues) + (255,))
    px.append(row)
png(f'{A}/textures/block/azure_leaves.png', px)
print("done")

# ---------------- extra leaf blocks ----------------
LEAVES = {"azure_leaves": ((30, 60, 220), "Azure Leaves", "Лазурная листва"),
          "ember_leaves": ((232, 110, 30), "Ember Leaves", "Янтарная листва"),
          "teal_leaves": ((30, 150, 150), "Teal Leaves", "Бирюзовая листва"),
          "scarlet_leaves": ((235, 84, 114), "Scarlet Leaves", "Алая листва")}
def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)
for n, (base, e, r) in LEAVES.items():
    rr = random.Random(sum(map(ord, n)))
    shades = [shade(base, k) for k in (0.7, 0.85, 1.0, 1.15, 1.3)]
    px = [[(0, 0, 0, 0) if rr.random() < 0.12 else rr.choice(shades) + (255,) for _ in range(16)] for _ in range(16)]
    png(f'{A}/textures/block/{n}.png', px)
    w(f'{A}/blockstates/{n}.json', {"variants": {"": {"model": f"fanscape:block/{n}"}}})
    w(f'{A}/models/block/{n}.json', {"parent": "minecraft:block/leaves", "textures": {"all": f"fanscape:block/{n}"}})
    w(f'{A}/models/item/{n}.json', {"parent": f"fanscape:block/{n}"})
    w(f'{D}/loot_table/blocks/{n}.json', {"type": "minecraft:block", "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
        "entries": [{"type": "minecraft:item", "name": f"fanscape:{n}"}],
        "conditions": [{"condition": "minecraft:match_tool", "predicate": {"items": ["minecraft:shears"]}}]}]})
    en[f"block.fanscape.{n}"] = e; ru[f"block.fanscape.{n}"] = r
ids = [f"fanscape:{n}" for n in LEAVES]
w(R + '/data/minecraft/tags/block/leaves.json', {"replace": False, "values": ids})
w(R + '/data/minecraft/tags/item/leaves.json', {"replace": False, "values": ids})
w(R + '/data/minecraft/tags/block/mineable/hoe.json', {"replace": False, "values": ids})
w(f'{A}/lang/en_us.json', en); w(f'{A}/lang/ru_ru.json', ru)
