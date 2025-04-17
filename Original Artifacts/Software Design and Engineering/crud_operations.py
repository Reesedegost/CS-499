from pymongo import MongoClient
from pymongo.errors import PyMongoError

class CRUD:
    """CRUD operations for a MongoDB collection."""
    
    def __init__(self, user, password, host, port, database_name, collection_name):
        """
        Initialize the MongoDB connection.
        
        Parameters:
            user (str): MongoDB username.
            password (str): MongoDB password.
            host (str): MongoDB host address.
            port (int): MongoDB port number.
            database_name (str): Database name.
            collection_name (str): Collection name.
        """
        try:
            self.client = MongoClient(f'mongodb://aacuser:Reesedegoat21@nv-desktop-services.apporto.com:32824')
            self.database = self.client['AAC']
            self.collection = self.database['animals']
            print("Connected to MongoDB.")
        except PyMongoError as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise e

    def create(self, data):
        """
        Insert a document into the collection.
        
        Parameters:
            data (dict): The document to insert.

        Returns:
            bool: True if insertion is successful, False otherwise.
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")

        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
        except PyMongoError as e:
            print(f"Insert failed: {e}")
            return False

    def read(self, query, limit=None):
        """
        Query documents from the collection.
        
        Parameters:
            query (dict): The query filter.
            limit (int): Maximum number of documents to return
        Returns:
            list: A list of matching documents.
        """
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")

        try:
            cursor = self.collection.find(query)
            if limit is not None:
                cursor = cursor.limit(limit)
            return list(cursor)
        except PyMongoError as e:
            print(f"Query failed: {e}")
            return []

    def update(self, collection_name, filter, update_values):
        """
        Update documents in the collection.

        Parameters:
            query (dict): The filter to match documents to be updated.
            update (dict): The update operations to apply to the matching documents.

        Returns:
            int: The number of documents modified.
        """
        try:
            collection = self.database[collection_name]
            result = collection.update_many(filter, {"$set": update_values})
            return result.modified_count
        except Exception as e:
            print(f"Error in update: {e}")
            return 0

    def delete(self, collection_name, filter):
        """
        Delete documents from the collection.

        Parameters:
            query (dict): The filter to match documents to be deleted.

        Returns:
            int: The number of documents deleted.
        """
        try:
            collection = self.database[collection_name]
            result = collection.delete_many(filter)
            return result.deleted_count
        except Exception as e:
            print(f"Error in delete: {e}")
            return 0
