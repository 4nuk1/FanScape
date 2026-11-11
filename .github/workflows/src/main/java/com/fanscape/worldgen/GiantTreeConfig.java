package com.fanscape.worldgen;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;

public record GiantTreeConfig(BlockState trunk, BlockState leaves, BlockState lantern,
                              int minHeight, int maxHeight, int canopyRadius, int canopyHeight)
        implements FeatureConfiguration {
    public static final Codec<GiantTreeConfig> CODEC = RecordCodecBuilder.create(i -> i.group(
            BlockState.CODEC.fieldOf("trunk").forGetter(GiantTreeConfig::trunk),
            BlockState.CODEC.fieldOf("leaves").forGetter(GiantTreeConfig::leaves),
            BlockState.CODEC.fieldOf("lantern").forGetter(GiantTreeConfig::lantern),
            Codec.intRange(8, 90).fieldOf("min_height").forGetter(GiantTreeConfig::minHeight),
            Codec.intRange(8, 90).fieldOf("max_height").forGetter(GiantTreeConfig::maxHeight),
            Codec.intRange(4, 14).fieldOf("canopy_radius").forGetter(GiantTreeConfig::canopyRadius),
            Codec.intRange(2, 14).fieldOf("canopy_height").forGetter(GiantTreeConfig::canopyHeight)
    ).apply(i, GiantTreeConfig::new));
}
