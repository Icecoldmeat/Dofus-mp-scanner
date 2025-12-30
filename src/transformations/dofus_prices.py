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

        print(row)
        potential_matches = self.item_repository.find_by_name_part(name)
        matches = self.get_matches(potential_matches, row)
        if len(matches) == 0:
            potential_matches = self.item_repository.find_all_items_as_list(self.item_repository.PROJECTION_DEFAULT)
            matches = self.get_matches(potential_matches, row)

        matched_item_id = [{'item_id': None, 'name': 'Item Not Found'}]
        if len(matches) > 0:
            matched_item_id = [potential_match for potential_match in potential_matches if potential_match['name'] == matches[0]]

        try:
            row['item_id'] = matched_item_id[0]['item_id']
        except Exception as e:
            raise e

        row['corrupt_name'] = row['name']
        row['name'] = matched_item_id[0]['name']

        return row

    def get_matches(self, potential_matches, row):
        names_of_potential_matches = [potential_match["name"] for potential_match in potential_matches]
        matches = difflib.get_close_matches(row['name'], names_of_potential_matches)

        return matches
