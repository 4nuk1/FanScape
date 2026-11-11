package com.fanscape;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(FanScape.MOD_ID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(FanScape.MOD_ID);

    /** Кристалл-светильник: яркость 14, как у факела. Ставится на любую грань, как аметистовый кластер. */
    public static final DeferredBlock<Block> LUMINOUS_CRYSTAL = BLOCKS.registerBlock("luminous_crystal",
            p -> new AmethystClusterBlock(7.0F, 3.0F, p),
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).forceSolidOn().noOcclusion()
                    .sound(SoundType.AMETHYST_CLUSTER).strength(1.5F).lightLevel(s -> 14)
                    .pushReaction(PushReaction.DESTROY));

    /** Полный блок кристалла, яркость 14. */
    public static final DeferredBlock<Block> CRYSTAL_BLOCK = BLOCKS.registerBlock("crystal_block", Block::new,
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).strength(1.5F, 6.0F)
                    .sound(SoundType.AMETHYST).lightLevel(s -> 14).requiresCorrectToolForDrops());

    /** Синяя листва для «лазурных» деревьев. */
    public static final DeferredBlock<Block> AZURE_LEAVES = BLOCKS.registerBlock("azure_leaves", LeavesBlock::new,
            BlockBehaviour.Properties.ofFullCopy(Blocks.OAK_LEAVES).mapColor(MapColor.COLOR_BLUE));

    public static final DeferredItem<BlockItem> LUMINOUS_CRYSTAL_ITEM = ITEMS.register("luminous_crystal",
            () -> new BlockItem(LUMINOUS_CRYSTAL.get(), new Item.Properties()));
    public static final DeferredItem<BlockItem> CRYSTAL_BLOCK_ITEM = ITEMS.register("crystal_block",
            () -> new BlockItem(CRYSTAL_BLOCK.get(), new Item.Properties()));
    public static final DeferredItem<BlockItem> AZURE_LEAVES_ITEM = ITEMS.register("azure_leaves",
            () -> new BlockItem(AZURE_LEAVES.get(), new Item.Properties()));
}
