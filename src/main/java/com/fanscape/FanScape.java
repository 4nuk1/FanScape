package com.fanscape;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(FanScape.MOD_ID)
public class FanScape {
    public static final String MOD_ID = "fanscape";

    public FanScape(IEventBus modBus) {
        ModBlocks.BLOCKS.register(modBus);
        ModBlocks.ITEMS.register(modBus);
        ModFeatures.FEATURES.register(modBus);
        ModTabs.TABS.register(modBus);
    }
}
