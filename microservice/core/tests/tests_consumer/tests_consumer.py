import sys
sys.path.append('/app/microservice/')

from core.rabbitmq.consumer import PikaClient


class TestConsumer:
    _item = {'id': 1, 'is_blocked': False, 'username': 'admin'}

    def test_preprocessing_data_no_update(self):
        expected_item = {'id': {'N': '1'}, 'is_blocked': {'BOOL': False}, 'username': {'S': 'admin'}}
        response = PikaClient.preprocessing_data(self._item, update=False)
        assert response == expected_item

    def test_preprocessing_data_update(self):
        expected_item = {
            'id': {'Value': {'N': '1'}},
            'is_blocked': {'Value': {'BOOL': False}},
            'username': {'Value': {'S': 'admin'}}
        }
        response = PikaClient.preprocessing_data(self._item, update=True)
        assert response == expected_item
