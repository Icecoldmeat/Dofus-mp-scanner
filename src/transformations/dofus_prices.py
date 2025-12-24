import difflib

import pandas as pd
from pandas import Series

from repository.mongodb import DofusItemRepository


class PriceTransformation:
    def __init__(self):
        self.item_repository = DofusItemRepository()

    def find_closest_match(self, row: Series):
        if pd.isna(row.item_id) is False:
            return row
        name = row['name'].split(' ', 1)[0]
        if "'" in name:
            name = row['name'].split("'", 1)[0]
        potential_matches = self.item_repository.find_by_name_part(name)
        if len(potential_matches) == 0:
            potential_matches = self.item_repository.find_all_items()

        names_of_potential_matches = [potential_match["name"] for potential_match in potential_matches]

        matches = difflib.get_close_matches(row['name'], names_of_potential_matches)
        matched_item_id = [potential_match for potential_match in potential_matches if potential_match['name'] == matches[0]]

        row['item_id'] = matched_item_id[0]['item_id']
        row['corrupt_name'] = row['name']
        row['name'] = matched_item_id[0]['name']

        return row
