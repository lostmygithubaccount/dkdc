-- This shows using the AutoMLTrain stored procedure to create a model for the nyctaxi dataset.
-- There is a backup for this dataset described at: 
--    https://docs.microsoft.com/en-us/sql/advanced-analytics/tutorials/demo-data-nyctaxi-in-sql?view=sql-server-2017
--
-- Note that the query casts datetime columns as nvarchar because datetime columns are currently
-- not supported by the sp_execute_external_script stored procedure.
--
-- This call uses @whitelist_models to give a list of models to use for training.

INSERT INTO dbo.aml_model(RunId, ExperimentName, Model, LogFileText, WorkspaceName)
EXEC dbo.AutoMLTrain @input_query='
SELECT TOP 100000
       CAST([pickup_datetime] AS NVARCHAR(30)) AS pickup_datetime
      ,CAST([dropoff_datetime] AS NVARCHAR(30)) AS dropoff_datetime
      ,[passenger_count]
      ,[trip_time_in_secs]
      ,[trip_distance]
      ,[payment_type]
      ,[tip_class]
  FROM [dbo].[nyctaxi_sample] ORDER BY [hack_license] ',
  @label_column = 'tip_class',
  @iterations = 10,
  @iteration_timeout_minutes = 3,
  @whitelist_models='ExtremeRandomTrees, DecisionTree'
  



