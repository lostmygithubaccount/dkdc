-- This shows using the AutoMLPredictstored procedure to predict values based on a model for the nyctaxi dataset.
-- There is a backup for this dataset described at: 
--    https://docs.microsoft.com/en-us/sql/advanced-analytics/tutorials/demo-data-nyctaxi-in-sql?view=sql-server-2017
--
-- Note that the query casts datetime columns as nvarchar because datetime columns are currently
-- not supported by the sp_execute_external_script stored procedure.

DECLARE @Model NVARCHAR(MAX) = (SELECT TOP 1 Model FROM dbo.aml_model WHERE ExperimentName = 'automl-sql-test' ORDER BY CreatedDate DESC)
EXEC dbo.AutoMLPredict @input_query='
SELECT top 100
      CAST([pickup_datetime] AS NVARCHAR(30)) AS pickup_datetime
      ,CAST([dropoff_datetime] AS NVARCHAR(30)) AS dropoff_datetime
      ,[passenger_count]
      ,[trip_time_in_secs]
      ,[trip_distance]
	  ,[payment_type]
      ,[tip_class]
FROM [dbo].[nyctaxi_sample] ORDER BY [hack_license] DESC',
  @model = @model,
  @label_column = 'tip_class'
WITH RESULT SETS ((pickup_datetime NVARCHAR(30), dropoff_datetime NVARCHAR(30), passenger_count INT, trip_time_in_secs BIGINT, trip_distance FLOAT, payment_type CHAR(3), actual_tip_class INT, predicted_tip_class INT))
  



