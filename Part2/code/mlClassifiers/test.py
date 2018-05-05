from pyspark.sql import SQLContext
from pyspark import SparkConf, SparkContext

from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# Load training data
conf = SparkConf().setAppName("NeuralNetworks")
conf = conf.setMaster("local[*]")
sc   = SparkContext(conf=conf)

sqlContext = SQLContext(sc)

df = sqlContext.read.format("com.databricks.spark.csv").option("delimiter", "\t").option("header", "true").load("doc1.txt")

# Displays the content of the DataFrame to stdout
#df.select("Docid").show(2,truncate= True)
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("Python Spark Feedforward neural network example") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()
    



# Convert to float format
def string_to_float(x):
    return float(x)

#
def condition(r):
    if (0<= r <= 1):
        label = "low"
    elif(1< r <= 2):
        label = "medium"
    else:
        label = "high"
    return label
    

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, DoubleType
string_to_float_udf = udf(string_to_float, DoubleType())
quality_udf = udf(lambda x: condition(x), StringType())
df= df.withColumn("label", quality_udf("label"))

# convert the data to dense vector
def transData(data):
    return data.rdd.map(lambda r: [r[-1], Vectors.dense(r[:-1])]).\
           toDF(['label','features'])

from pyspark.sql import Row
from pyspark.ml.linalg import Vectors

data= transData(df)
data.show()

(trainingData, testData) = df.randomSplit([0.7, 0.3])


# specify layers for the neural network:
# input layer of size 11 (features), two intermediate of size 5 and 4
# and output of size 7 (classes)
layers = [7, 10 , 2]

# create the trainer and set its parameters
FNN = MultilayerPerceptronClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures",\
                                         maxIter=100, layers=layers, blockSize=128, seed=1234)
# Convert indexed labels back to original labels.
labelConverter = IndexToString(inputCol="prediction", outputCol="predictedLabel",
                               labels=labelIndexer.labels)
# Chain indexers and forest in a Pipeline
from pyspark.ml import Pipeline
pipeline = Pipeline(stages=[labelIndexer, featureIndexer, FNN, labelConverter])
# train the model
# Train model.  This also runs the indexers.
model = pipeline.fit(trainingData)

# Make predictions.
predictions = model.transform(testData)
# Select example rows to display.
predictions.select("features","label","predictedLabel").show(5)


# Select (prediction, true label) and compute test error
evaluator = MulticlassClassificationEvaluator(
    labelCol="indexedLabel", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)
print("Predictions accuracy = %g, Test Error = %g" % (accuracy,(1.0 - accuracy)))