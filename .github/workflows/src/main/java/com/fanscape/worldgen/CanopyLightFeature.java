package com.fanscape.worldgen;

import com.fanscape.ModBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Для любых деревьев в чанке: ставит светящиеся кристаллы на землю под листвой. */
public class CanopyLightFeature extends Feature<NoneFeatureConfiguration> {
    public CanopyLightFeature() { super(NoneFeatureConfiguration.CODEC); }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        int x0 = ctx.origin().getX() & ~15, z0 = ctx.origin().getZ() & ~15;
        BlockState lamp = ModBlocks.LUMINOUS_CRYSTAL.get().defaultBlockState()
                .setValue(AmethystClusterBlock.FACING, Direction.UP);
        boolean any = false;
        for (int gx = 1; gx < 16; gx += 4)
            for (int gz = 1; gz < 16; gz += 4) {
                int x = x0 + gx + rnd.nextInt(2), z = z0 + gz + rnd.nextInt(2);
                int ground = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
                if (top - ground < 3) continue;
                BlockPos p = new BlockPos(x, ground, z);
                BlockState below = level.getBlockState(p.below());
                if (below.is(BlockTags.LOGS) || !below.getFluidState().isEmpty()) continue;
                boolean covered = false;
                for (int dy = 1; dy <= 24 && !covered; dy++)
                    covered = level.getBlockState(p.above(dy)).is(BlockTags.LEAVES);
                if (!covered) continue;
                if (level.isEmptyBlock(p) && below.isFaceSturdy(level, p.below(), Direction.UP)) {
                    level.setBlock(p, lamp, 2);
                    any = true;
                }
            }
        return any;
    }
}
