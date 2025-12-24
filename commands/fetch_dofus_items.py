from api.dofusdb import DofusDBClient
from repository.mongodb import DofusRepository

dbClient = DofusDBClient(DofusRepository(DofusRepository.TABLE_RECIPE))
dbClient.fetch_all(dbClient.RECIPE_URL, dbClient.RECIPE_TOTAL, 1000)

dbClient = DofusDBClient(DofusRepository(DofusRepository.TABLE_ITEM))
dbClient.fetch_all(dbClient.ITEM_URL, dbClient.ITEM_TOTAL, 0)
