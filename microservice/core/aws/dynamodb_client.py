from warnings import warn

from .base_client import ClientMeta


class DynamoDBClient(metaclass=ClientMeta):
    _service_name = 'dynamodb'
    _client = None

    @classmethod
    def scan_db(cls, table_name: str) -> list:
        """
        Scan the database based on table_name
        :param table_name: target table
        :return: fetched items.
        """
        response = cls.client.scan(TableName=table_name)
        return response.get('Items', tuple())

    @classmethod
    def get_item(cls, table_name: str, pk: str, target_pk: int) -> dict:
        """
        Fetch target item if it exists
        :param table_name: a target table
        :param pk: a primary key of the table
        :param target_pk: a primary key of the target item
        :return: fetched item.
        """
        pk_type, converted_pk = cls.target_pk_type(target_pk)
        response = cls.client.get_item(TableName=table_name, Key={pk: {pk_type: converted_pk}})
        return response.get('Item', dict())

    @classmethod
    def put_item(cls, table_name: str, item: dict) -> int:
        """
        Put the given item to the database
        :param table_name: a target table
        :param item: an item to be added
        :return: request status code (int).
        """
        response = cls.client.put_item(TableName=table_name, Item=item)
        return response['ResponseMetadata']['HTTPStatusCode']

    @classmethod
    def update_item(cls, table_name: str, pk: str, target_pk: str | int | bytes, fields_to_update: dict) -> int:
        """
        Update the given item
        :param table_name: a target table
        :param pk: a primary key of the table
        :param target_pk: a primary key of the target item
        :param fields_to_update: fields to update
        :return: request status code (int).
        """
        pk_type, converted_pk = cls.target_pk_type(target_pk)
        response = cls.client.update_item(
            TableName=table_name,
            Key={pk: {pk_type: converted_pk}},
            AttributeUpdates=fields_to_update
        )
        return response['ResponseMetadata']['HTTPStatusCode']

    @classmethod
    def delete_item(cls, table_name: str, pk: int, target_pk: str | int | bytes) -> int:
        """
        Delete the given item
        :param table_name: a target table
        :param pk: a primary key of the table
        :param target_pk: a primary key of the target item
        :return: request status code (int).
        """
        pk_type, converted_pk = cls.target_pk_type(target_pk)
        response = cls.client.delete_item(
            TableName=table_name,
            Key={pk: {pk_type: converted_pk}}
        )
        return response['ResponseMetadata']['HTTPStatusCode']

    @staticmethod
    def target_pk_type(target_pk: int | str | bytes) -> tuple[str, str] | str:
        """
        Define primary key type
        :param target_pk: primary key to define its type
        :return: type string representation.
        """
        match target_pk:
            case bool():  # 'case bool' should be before 'case int', 'cause bool type is a subclass of int class
                pk_type, pk = 'BOOL', target_pk
            case int():
                pk_type, pk = 'N', str(target_pk)
            case str():
                pk_type, pk = 'S', target_pk
            case bytes():
                pk_type, pk = 'B', str(target_pk)
            case None:
                pk_type, pk = 'NULL', True
            case _:
                warn("The given primary key's type is invalid")
                raise KeyError("Define the right primary return_value key's type")
        return pk_type, pk
