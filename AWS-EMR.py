# -*- coding: utf-8 -*-
"""AES EMR.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1x6C96agZTBEC3WtE8kY-BF_sP7mMA0Vl
"""

from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("AmazonReviewsAnalysis").getOrCreate()

# Load dataset (assuming stored in HDFS or S3)
df = spark.read.csv("s3://your-bucket/amazon-reviews.csv", header=True, inferSchema=True)

# Display schema
df.printSchema()

# Perform Data Cleaning
df = df.dropna()  # Drop missing values
df = df.filter(df["reviewText"] != "")  # Remove empty reviews

# Perform Basic Analysis (e.g., Count the number of reviews per product)
review_counts = df.groupBy("productId").count()

# Show results
review_counts.show()

# Save the processed data
review_counts.write.csv("s3://your-bucket/processed_reviews.csv", header=True)

# Stop Spark session
spark.stop()

from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, HashingTF, IDF
from pyspark.ml.classification import LogisticRegression

# Initialize Spark
spark = SparkSession.builder.appName("SentimentAnalysis").getOrCreate()

# Load dataset
df = spark.read.csv("s3://your-bucket/amazon-reviews.csv", header=True, inferSchema=True)

# Select relevant columns
df = df.select("reviewText", "overall")

# Convert text reviews into features
tokenizer = Tokenizer(inputCol="reviewText", outputCol="words")
words_data = tokenizer.transform(df)

hashing_tf = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=10000)
featurized_data = hashing_tf.transform(words_data)

idf = IDF(inputCol="rawFeatures", outputCol="features")
idf_model = idf.fit(featurized_data)
rescaled_data = idf_model.transform(featurized_data)

# Convert star ratings into binary sentiment (positive = 1 if rating >= 4)
df = df.withColumn("label", (df["overall"] >= 4).cast("integer"))

# Train-test split
(train, test) = df.randomSplit([0.8, 0.2])

# Train logistic regression model
lr = LogisticRegression(featuresCol="features", labelCol="label")
lr_model = lr.fit(train)

# Make predictions
predictions = lr_model.transform(test)

# Evaluate model
predictions.select("reviewText", "prediction").show()

# Stop Spark session
spark.stop()