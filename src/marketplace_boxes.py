from dataclasses import dataclass


@dataclass
class MarketPlaceScannerBoxes:
    mp_item_box_width: int # from kamas icon
    mp_item_box_height_from_middle: int
    mp_items_kamas_region: tuple[int, int, int, int]
    mp_item_sale_box_region: tuple[int, int, int, int] # use a item without a set for measurements
    mp_validate_new_items_region: tuple[int, int, int, int]

    # This is not used on screen but, the actual image. u can use https://pixspy.com/
    mp_item_sale_box_pack_image_end_x: int
    mp_item_sale_box_pack_image_pack_x_end: int
    mp_item_sale_box_pack_image_end_star_x: int


average_text_box = MarketPlaceScannerBoxes(
    mp_item_box_width=390,
    mp_item_box_height_from_middle=18,
    mp_items_kamas_region=(688, 24, 731, 1017),
    mp_item_sale_box_region=(154, 156, 421+154, 348+156),
    mp_validate_new_items_region=(895, 287, 281+895, 575+287),
    mp_item_sale_box_pack_image_end_x=70,
    mp_item_sale_box_pack_image_pack_x_end=120,
    mp_item_sale_box_pack_image_end_star_x=160,

)
# Large textboxes makes it so that 5 offers are also visible in none set items.
large_text_box = MarketPlaceScannerBoxes(
    mp_item_box_width=464-25,
    mp_item_box_height_from_middle=20,
    mp_items_kamas_region=(1163, 163, 181, 797),
    mp_item_sale_box_region=(159, 166, 418+159, 352+166),
    mp_validate_new_items_region=(847, 294, 297+847, 569+294),
    mp_item_sale_box_pack_image_end_x=70,
    mp_item_sale_box_pack_image_pack_x_end=120,
    mp_item_sale_box_pack_image_end_star_x=160,

)
