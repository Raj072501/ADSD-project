from pymongo import MongoClient

# Replace with your MongoDB connection string
mongo_uri = "mongodb+srv://Rajesh:Raj123@cluster0.vh5yz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(mongo_uri)
    # Test the connection by listing the database names
    client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    print("MongoDB connection failed:", e)
