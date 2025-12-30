from api.dofusdb import DofusDBClient
from repository.mongodb import DofusRepository, DofusEffectsRepository, DofusCharacteristicRepository

dbClient = DofusDBClient(DofusRepository(DofusRepository.TABLE_RECIPE))
dbClient.fetch_all(dbClient.RECIPE_URL, dbClient.RECIPE_TOTAL, 1000)

dbClient = DofusDBClient(DofusRepository(DofusRepository.TABLE_ITEM))
dbClient.fetch_all(dbClient.ITEM_URL, dbClient.ITEM_TOTAL, 0)

dbClient = DofusDBClient(DofusEffectsRepository())
dbClient.fetch_all(dbClient.EFFECTS_URL, 867, 0)


dbClient = DofusDBClient(DofusCharacteristicRepository())
dbClient.fetch_all(dbClient.CHARACTERISTICS_URL, 999, 0)