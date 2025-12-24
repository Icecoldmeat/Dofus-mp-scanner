from time import sleep

import requests

from repository.mongodb import DofusRepository


class DofusDBClient:
    RECIPE_URL = "https://api.dofusdb.fr/recipes"
    ITEM_URL = "https://api.dofusdb.fr/items"
    RECIPE_TOTAL = 4745
    ITEM_TOTAL = 20494
    PAGE_SIZE = 50

    def __init__(self, dofus_repo: DofusRepository):
        self.dofus_repo = dofus_repo

    def fetch_all(self, url: str, total_count: int, skip_start: int = 0):
        """
        Fetches all recipes from the API.
        Returns a list of all recipe objects.
        """

        for skip in range(skip_start, total_count, self.PAGE_SIZE):
            params = {
                "$skip": skip,
                "$limit": self.PAGE_SIZE
            }

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json().get("data", [])

                if not data:
                    break  # stop early if API returns no data

                #  all_recipes.extend(data)
                self.dofus_repo.add_multiple(data)
                sleep(20)
                print(f"Fetched {len(data)} recipes and saved to db...")

            except requests.RequestException as e:
                print(f"Error at skip={skip}: {e}")
                break

