package com.fanscape;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.function.Supplier;

public class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, FanScape.MOD_ID);

    public static final Supplier<CreativeModeTab> MAIN = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.fanscape"))
            .icon(() -> new ItemStack(ModBlocks.LUMINOUS_CRYSTAL_ITEM.get()))
            .displayItems((params, out) -> {
                out.accept(ModBlocks.LUMINOUS_CRYSTAL_ITEM.get());
                out.accept(ModBlocks.CRYSTAL_BLOCK_ITEM.get());
                out.accept(ModBlocks.AZURE_LEAVES_ITEM.get());
            }).build());
}
