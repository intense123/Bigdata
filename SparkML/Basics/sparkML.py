pip install pyspark

import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('crew_requirement').getOrCreate()

df = spark.read.csv('/content/cruise_ship_info.csv', inferSchema = True, header = True)

df.show(5)

df.printSchema()

from pyspark.ml.feature import StringIndexer

indexer = StringIndexer(inputCol = 'Cruise_line', outputCol = "Cruise_line_index")

df_indexed = indexer.fit(df).transform(df)

df_indexed.show(10)

df_indexed.select('Cruise_line', 'Cruise_line_index').distinct().show()

df_indexed.groupby("Cruise_line").count().show()

df_indexed.columns

from pyspark.ml.feature import VectorAssembler

assembler = VectorAssembler(inputCols = ['Age',
 'Tonnage',
 'passengers',
 'length',
 'cabins',
 'passenger_density',
 'Cruise_line_index'], outputCol = 'features')

output = assembler.transform(df_indexed)

output.show()

train_data , test_data = output.randomSplit([.8,.2])
train_data.describe().show()

from pyspark.ml.regression import LinearRegression
crew_req = LinearRegression(featuresCol= 'features', labelCol = 'crew')

model = crew_req.fit(train_data)

result = model.evaluate(train_data)

result.r2

pred = model.transform(test_data)

result_test = model.evaluate(test_data)

result_test.r2

pred.show()

pip install ucimlrepo

from ucimlrepo import fetch_ucirepo

# fetch dataset
adult = fetch_ucirepo(id=2)

# data (as pandas dataframes)
X = adult.data.features
y = adult.data.targets

# metadata
print(adult.metadata)

# variable information
print(adult.variables)

X.head()

data = spark.read.csv('/content/adult.data')
data.show()

labels = ['age', 'workclass', 'fnlwgt', 'education', 'numbers', 'marital', 'occupation', 'relation', 'race', 'gender', 'gain', 'loss', 'hourlypay', 'country', 'income']

df = data.toDF(*labels)

df.show(5)

df.printSchema()

from pyspark.sql.functions import col
new_df = df.withColumn('age' , col('age').cast('integer'))

new_df.printSchema()

for i in [ 'fnlwgt' , 'numbers', 'gain', 'loss', 'hourlypay']:
  new_df = new_df.withColumn(i , col(i).cast('integer'))

from pyspark.sql.functions import *

new_df.select([count(when(col(c).isNull(), c )).alias(c) for c in new_df.columns]).show()

df.select('workclass').distinct().show()

df = new_df.replace(" ?" , None)

from pyspark.sql.functions import *

df.select([count(when(col(c).isNull(), c )).alias(c) for c in df.columns]).show()

df.groupby('occupation').count().show()

df = df.fillna(" United-States", subset = ['country'])

df = df.fillna(" Private", subset = ['workclass'])

df = df.fillna(" Prof-specialty", subset = ['occupation'])

df.select([count(when(col(c).isNull(), c )).alias(c) for c in df.columns]).show()

from pyspark.ml.classification import LogisticRegression
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer , VectorAssembler

df.columns

categorical_cols = [ 'workclass',
 'education',
 'marital',
 'occupation',
 'relation',
 'race',
 'gender',
 'country']
numeric_cols = [ 'age' ,'fnlwgt' , 'numbers', 'gain', 'loss', 'hourlypay']
label = 'income'

indexer = [StringIndexer(inputCol = c , outputCol = f"{c}_index", handleInvalid = 'keep') for c in categorical_cols]

label_indexer = StringIndexer(inputCol = 'income', outputCol = 'label', handleInvalid = 'keep')

assembler = VectorAssembler(inputCols = [f'{c}_index' for c in categorical_cols] + numeric_cols, outputCol = 'features')

lr = LogisticRegression(featuresCol = 'features', labelCol = 'label')

pipeline = Pipeline(stages = indexer + [assembler , label_indexer , lr] )

train_data , test_data = df.randomSplit([.8, .2])

model = pipeline.fit(train_data)

prediction = model.transform(test_data)

prediction.select('label', 'prediction').show()

prediction.groupby('label', 'prediction').count().show()

from pyspark.ml.evaluation import MulticlassClassificationEvaluator

evaluator = MulticlassClassificationEvaluator(predictionCol = 'prediction', labelCol = 'label', metricName = 'accuracy')

evaluator.evaluate(prediction)
