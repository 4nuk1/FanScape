package com.fanscape.worldgen;

import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

public final class FeatureUtil {
    private FeatureUtil() {}

    /** Во время генерации можно писать только в 3x3 чанка вокруг origin. */
    public static boolean inRange(BlockPos origin, BlockPos p) {
        int dx = (p.getX() >> 4) - (origin.getX() >> 4);
        int dz = (p.getZ() >> 4) - (origin.getZ() >> 4);
        return Math.abs(dx) <= 1 && Math.abs(dz) <= 1;
    }

    public static boolean replaceable(WorldGenLevel level, BlockPos p) {
        BlockState s = level.getBlockState(p);
        return s.isAir() || s.is(BlockTags.REPLACEABLE_BY_TREES) || s.is(BlockTags.LEAVES) || s.is(Blocks.SNOW);
    }

    public static boolean place(WorldGenLevel level, BlockPos origin, BlockPos p, BlockState state) {
        if (level.isOutsideBuildHeight(p) || !inRange(origin, p) || !replaceable(level, p)) return false;
        level.setBlock(p, state, 2);
        return true;
    }
}
