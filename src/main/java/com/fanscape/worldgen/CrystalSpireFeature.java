package com.fanscape.worldgen;

import com.fanscape.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/** Высокие наклонные шестигранные кристальные шпили. */
public class CrystalSpireFeature extends Feature<NoneFeatureConfiguration> {
    public CrystalSpireFeature() { super(NoneFeatureConfiguration.CODEC); }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos o = ctx.origin();
        BlockState below = level.getBlockState(o.below());
        if (below.isAir() || !below.getFluidState().isEmpty()) return false;

        int h = 14 + rnd.nextInt(30);
        double ang = rnd.nextDouble() * Math.PI * 2;
        spire(level, o, o, rnd, h, 2.5 + rnd.nextDouble() * 2.0, ang, h * 0.25);
        int n = 2 + rnd.nextInt(3);
        for (int i = 0; i < n; i++) {
            double a = rnd.nextDouble() * Math.PI * 2;
            double dist = 3 + rnd.nextInt(5);
            BlockPos q = o.offset((int) (Math.cos(a) * dist), 0, (int) (Math.sin(a) * dist));
            int gy = findGround(level, q, o.getY());
            if (gy == Integer.MIN_VALUE) continue;
            double ratio = 0.3 + rnd.nextDouble() * 0.3;
            spire(level, o, new BlockPos(q.getX(), gy, q.getZ()), rnd, (int) (h * ratio),
                    1.5 + rnd.nextDouble(), ang + (rnd.nextDouble() - 0.5), h * ratio * 0.3);
        }
        return true;
    }

    private static int findGround(WorldGenLevel level, BlockPos p, int refY) {
        for (int y = refY + 6; y >= refY - 6; y--) {
            BlockPos c = new BlockPos(p.getX(), y, p.getZ());
            if (!FeatureUtil.inRange(c, c)) return Integer.MIN_VALUE;
            if (!level.getBlockState(c).isAir() && level.getBlockState(c.above()).isAir()) return y + 1;
        }
        return Integer.MIN_VALUE;
    }

    private static void spire(WorldGenLevel level, BlockPos origin, BlockPos base, RandomSource rnd,
                              int h, double r0, double ang, double lean) {
        BlockState crystal = ModBlocks.CRYSTAL_BLOCK.get().defaultBlockState();
        for (int y = -2; y <= h; y++) {
            double t = Math.max(0, y) / (double) h;
            double r = y < 0 ? r0 : r0 * (1 - t) + 0.4;
            double cx = base.getX() + 0.5 + Math.cos(ang) * lean * t;
            double cz = base.getZ() + 0.5 + Math.sin(ang) * lean * t;
            int ir = (int) Math.ceil(r);
            for (int ix = -ir; ix <= ir; ix++)
                for (int iz = -ir; iz <= ir; iz++) {
                    double hex = Math.max(Math.abs(ix) * 0.866 + Math.abs(iz) * 0.5, Math.abs(iz));
                    if (hex > r) continue;
                    BlockPos p = new BlockPos((int) Math.floor(cx) + ix, base.getY() + y, (int) Math.floor(cz) + iz);
                    if (level.isOutsideBuildHeight(p) || !FeatureUtil.inRange(origin, p)) continue;
                    BlockState cur = level.getBlockState(p);
                    if (y < 0) {
                        if (!cur.is(Blocks.BEDROCK) && cur.getFluidState().isEmpty()) level.setBlock(p, crystal, 2);
                    } else if (FeatureUtil.replaceable(level, p)) {
                        level.setBlock(p, crystal, 2);
                    }
                }
        }
    }
}
