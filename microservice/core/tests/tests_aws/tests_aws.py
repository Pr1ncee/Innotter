import sys
sys.path.append('/app/microservice/')

import pytest

from fastapi.testclient import TestClient
import moto

from core.aws.dynamodb_client import DynamoDBClient
from core.main import app
from core.settings import settings


client = TestClient(app)
db = DynamoDBClient


class TestDynamoDBClient:
    _table_name = settings.USERS_NAME_TABLE
    _params = {
                 'TableName': _table_name,
                 'KeySchema': [
                     {'AttributeName': 'id', 'KeyType': 'HASH'},
                 ],
                 'AttributeDefinitions': [
                     {'AttributeName': 'id', 'AttributeType': 'N'},
                 ],
                 'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                 }
    }
    _item = {'id': {'N': '1'}, 'is_blocked': {'BOOL': False}, 'username': {'S': 'test'}}

    @moto.mock_dynamodb
    def test_dynamodb_methods(self):
        table = db.create_table(self._params)
        assert table['TableDescription']['TableName'] == self._table_name

        response = db.scan(self._table_name)
        assert not response

        response = db.put_item(self._table_name, self._item)
        assert response == 200

    @pytest.mark.parametrize(
        'target_pk, expected',
        [
            (False, ('BOOL', False)),
            (1, ('N', '1')),
            ('foo', ('S', 'foo')),
            (b'foo', ('B', str(b'foo'))),
            (None, ('NULL', True))
        ]
    )
    def test_type_converter(self, target_pk, expected):
        assert db.target_pk_type(target_pk) == expected
