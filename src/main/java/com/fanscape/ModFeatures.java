package com.fanscape;

import com.fanscape.worldgen.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES =
            DeferredRegister.create(Registries.FEATURE, FanScape.MOD_ID);

    public static final DeferredHolder<Feature<?>, GiantTreeFeature> GIANT_TREE =
            FEATURES.register("giant_tree", () -> new GiantTreeFeature(GiantTreeConfig.CODEC));
    public static final DeferredHolder<Feature<?>, CrystalSpireFeature> CRYSTAL_SPIRE =
            FEATURES.register("crystal_spire", CrystalSpireFeature::new);
    public static final DeferredHolder<Feature<?>, CrystalClustersFeature> CRYSTAL_CLUSTERS =
            FEATURES.register("crystal_clusters", CrystalClustersFeature::new);
    public static final DeferredHolder<Feature<?>, BoulderFeature> BOULDER =
            FEATURES.register("boulder", BoulderFeature::new);
    public static final DeferredHolder<Feature<?>, CanopyLightFeature> CANOPY_LIGHT =
            FEATURES.register("canopy_light", CanopyLightFeature::new);
}
