package com.fanscape.worldgen;

import com.fanscape.ModBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Огромное дерево: толстый изогнутый ствол, корни, ветви и зонтичная крона с кристальными «фонарями». */
public class GiantTreeFeature extends Feature<GiantTreeConfig> {
    public GiantTreeFeature(Codec<GiantTreeConfig> codec) { super(codec); }

    private static BlockState axis(BlockState s, Direction.Axis a) {
        return s.hasProperty(RotatedPillarBlock.AXIS) ? s.setValue(RotatedPillarBlock.AXIS, a) : s;
    }

    @Override
    public boolean place(FeaturePlaceContext<GiantTreeConfig> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos o = ctx.origin();
        GiantTreeConfig cfg = ctx.config();

        if (!level.getBlockState(o.below()).is(BlockTags.DIRT)) return false;
        for (int dx = -3; dx <= 3; dx += 3)
            for (int dz = -3; dz <= 3; dz += 3) {
                BlockState b = level.getBlockState(o.offset(dx, -1, dz));
                if (b.isAir() || !b.getFluidState().isEmpty()) return false;
            }

        int h = cfg.minHeight() + rnd.nextInt(Math.max(1, cfg.maxHeight() - cfg.minHeight() + 1));
        double angle = rnd.nextDouble() * Math.PI * 2;
        double lean = 1 + rnd.nextInt(3);
        double ox = o.getX() + 0.5, oz = o.getZ() + 0.5;
        BlockState logY = axis(cfg.trunk(), Direction.Axis.Y);

        // --- ствол
        for (int y = 0; y <= h; y++) {
            double t = (double) y / h;
            double off = t * t;
            double cx = ox + Math.cos(angle) * lean * off;
            double cz = oz + Math.sin(angle) * lean * off;
            double r = 3.3 - 1.8 * t + (y < 4 ? (4 - y) * 0.35 : 0);
            int ir = (int) Math.ceil(r);
            for (int ix = -ir; ix <= ir; ix++)
                for (int iz = -ir; iz <= ir; iz++) {
                    if (ix * ix + iz * iz > r * r) continue;
                    BlockPos p = new BlockPos(Mth.floor(cx) + ix, o.getY() + y, Mth.floor(cz) + iz);
                    FeatureUtil.place(level, o, p, logY);
                    if (y == 0) {
                        for (int k = 1; k <= 8; k++) {
                            BlockPos q = p.below(k);
                            if (!FeatureUtil.place(level, o, q, logY)) break;
                        }
                    }
                }
        }

        // --- корни
        for (int i = 0; i < 6; i++) {
            double ra = i * Math.PI / 3 + rnd.nextDouble() * 0.6;
            for (int s = 2; s <= 8; s++) {
                BlockPos p = BlockPos.containing(ox + Math.cos(ra) * s, o.getY() + 1 - s / 3.0, oz + Math.sin(ra) * s);
                FeatureUtil.place(level, o, p, axis(cfg.trunk(), Math.abs(Math.cos(ra)) > Math.abs(Math.sin(ra)) ? Direction.Axis.X : Direction.Axis.Z));
            }
        }

        // --- ветви и кроны
        double R = cfg.canopyRadius();
        List<double[]> blobs = new ArrayList<>();
        int nb = 5 + rnd.nextInt(3);
        for (int i = 0; i < nb; i++) {
            double ba = i * (Math.PI * 2 / nb) + rnd.nextDouble() * 0.7;
            double st = 0.6 + rnd.nextDouble() * 0.3;
            double sx = ox + Math.cos(angle) * lean * st * st;
            double sz = oz + Math.sin(angle) * lean * st * st;
            double sy = o.getY() + h * st;
            double len = R * (0.45 + rnd.nextDouble() * 0.15);
            double rise = 0.15 + rnd.nextDouble() * 0.3;
            BlockState bl = axis(cfg.trunk(), Math.abs(Math.cos(ba)) > Math.abs(Math.sin(ba)) ? Direction.Axis.X : Direction.Axis.Z);
            double px = sx, py = sy, pz = sz;
            for (int s = 1; s <= len; s++) {
                px = sx + Math.cos(ba) * s;
                pz = sz + Math.sin(ba) * s;
                py = sy + s * rise;
                BlockPos p = BlockPos.containing(px, py, pz);
                FeatureUtil.place(level, o, p, bl);
                if (s < len * 0.5) FeatureUtil.place(level, o, p.above(), bl);
            }
            blobs.add(new double[]{px, py + 1, pz, 3.5 + rnd.nextDouble() * 1.5, cfg.canopyHeight() * 0.5 + rnd.nextDouble() * 1.5});
        }
        double tx = ox + Math.cos(angle) * lean, tz = oz + Math.sin(angle) * lean, ty = o.getY() + h;
        blobs.add(new double[]{tx, ty + 1, tz, R * 0.7, cfg.canopyHeight() * 0.6 + 1});

        // --- листва
        Set<BlockPos> leaves = new HashSet<>();
        Set<Long> columns = new HashSet<>();
        BlockState leafState = cfg.leaves();
        for (double[] b : blobs) {
            double rx = b[3], ry = b[4];
            int ix = (int) Math.ceil(rx), iy = (int) Math.ceil(ry);
            for (int dx = -ix; dx <= ix; dx++)
                for (int dy = -iy; dy <= iy; dy++)
                    for (int dz = -ix; dz <= ix; dz++) {
                        double d = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) + (dz * dz) / (rx * rx);
                        if (d > 1.0 - rnd.nextFloat() * 0.35) continue;
                        BlockPos p = BlockPos.containing(b[0] + dx, b[1] + dy, b[2] + dz);
                        if (FeatureUtil.place(level, o, p, leafState)) {
                            leaves.add(p.immutable());
                            columns.add(ChunkPos.asLong(p.getX(), p.getZ()));
                        }
                    }
        }

        // --- светящиеся кристаллы-«плоды» в нижнем слое кроны
        for (BlockPos p : leaves) {
            if (level.getBlockState(p.below()).isAir() && rnd.nextInt(7) == 0) {
                level.setBlock(p, cfg.lantern(), 2);
            }
        }

        // --- кристаллы на земле под кроной, чтобы не было тёмных пятен
        BlockState lamp = ModBlocks.LUMINOUS_CRYSTAL.get().defaultBlockState()
                .setValue(AmethystClusterBlock.FACING, Direction.UP);
        for (int gx = -16; gx <= 16; gx += 4)
            for (int gz = -16; gz <= 16; gz += 4) {
                int x = o.getX() + gx + rnd.nextInt(3) - 1;
                int z = o.getZ() + gz + rnd.nextInt(3) - 1;
                if (!columns.contains(ChunkPos.asLong(x, z))) continue;
                BlockPos ground = null;
                for (int y = o.getY() + 12; y >= o.getY() - 12; y--) {
                    BlockPos p = new BlockPos(x, y, z);
                    if (!FeatureUtil.inRange(o, p)) break;
                    BlockState s = level.getBlockState(p);
                    if (s.isAir() || s.is(BlockTags.LEAVES)) continue;
                    if (s.is(BlockTags.LOGS) || !s.getFluidState().isEmpty()) break;
                    ground = p;
                    break;
                }
                if (ground == null) continue;
                BlockPos lp = ground.above();
                if (level.isEmptyBlock(lp) && level.getBlockState(ground).isFaceSturdy(level, ground, Direction.UP)) {
                    level.setBlock(lp, lamp, 2);
                }
            }
        return true;
    }
}
