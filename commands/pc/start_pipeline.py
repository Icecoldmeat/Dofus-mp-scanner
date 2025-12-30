from pipelines.pipeline import NuggetPipeline, ImportPricesFromExternalServer, ItemCostPipeline, RuneCrushPipeline

nugget_pipeline = NuggetPipeline

pipelines = [
  #  ImportPricesFromExternalServer(),
    ItemCostPipeline(),
#    RuneCrushPipeline(),
]

print('starting import')
for pipeline in pipelines:
    print(pipeline.description)
    pipeline.start()
