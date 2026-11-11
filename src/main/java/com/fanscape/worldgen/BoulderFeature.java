package com.fanscape.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Крупные валуны. */
public class BoulderFeature extends Feature<NoneFeatureConfiguration> {
    public BoulderFeature() { super(NoneFeatureConfiguration.CODEC); }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos o = ctx.origin();
        BlockState below = level.getBlockState(o.below());
        if (below.isAir() || !below.getFluidState().isEmpty()) return false;

        int r = 2 + rnd.nextInt(5);
        double rx = r + rnd.nextDouble(), ry = r * 0.7 + 0.5, rz = r + rnd.nextDouble();
        BlockPos c = o.above((int) (ry * 0.4));
        int ix = (int) Math.ceil(rx), iy = (int) Math.ceil(ry), iz = (int) Math.ceil(rz);
        for (int dx = -ix; dx <= ix; dx++)
            for (int dy = -iy; dy <= iy; dy++)
                for (int dz = -iz; dz <= iz; dz++) {
                    double d = dx * dx / (rx * rx) + dy * dy / (ry * ry) + dz * dz / (rz * rz);
                    if (d > 1.0 - rnd.nextFloat() * 0.25) continue;
                    BlockPos p = c.offset(dx, dy, dz);
                    if (level.isOutsideBuildHeight(p) || !FeatureUtil.inRange(o, p)) continue;
                    if (FeatureUtil.replaceable(level, p) || level.getBlockState(p).is(BlockTags.DIRT)) {
                        int k = rnd.nextInt(10);
                        BlockState s = k < 6 ? Blocks.STONE.defaultBlockState()
                                : k < 8 ? Blocks.ANDESITE.defaultBlockState()
                                : Blocks.MOSSY_COBBLESTONE.defaultBlockState();
                        level.setBlock(p, s, 2);
                    }
                }
        return true;
    }
}
