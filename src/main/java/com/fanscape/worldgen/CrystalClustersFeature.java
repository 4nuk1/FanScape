package com.fanscape.worldgen;

import com.fanscape.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Россыпь кристаллов на полу, стенах и потолках (поверхность и пещеры). */
public class CrystalClustersFeature extends Feature<NoneFeatureConfiguration> {
    public CrystalClustersFeature() { super(NoneFeatureConfiguration.CODEC); }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos o = ctx.origin();
        BlockState base = ModBlocks.LUMINOUS_CRYSTAL.get().defaultBlockState();
        int placed = 0;
        for (int i = 0; i < 28; i++) {
            BlockPos p = o.offset(rnd.nextInt(9) - 4, rnd.nextInt(7) - 3, rnd.nextInt(9) - 4);
            if (level.isOutsideBuildHeight(p) || !FeatureUtil.inRange(o, p) || !level.isEmptyBlock(p)) continue;
            Direction d = Direction.getRandom(rnd);
            BlockPos s = p.relative(d);
            if (level.getBlockState(s).isFaceSturdy(level, s, d.getOpposite())) {
                level.setBlock(p, base.setValue(AmethystClusterBlock.FACING, d.getOpposite()), 2);
                placed++;
            }
        }
        return placed > 0;
    }
}
