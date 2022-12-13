import sys

sys.path.append('/app/microservice/')

from core.settings import settings
from core.services import services, stats_service


class TestServices:
    _objs_list = {
        '41':
            {
                'posts': '0',
                'followers': '5',
                'uuid': 'another uuidaaa',
                'unblock_date': 'None',
                'name': 'another pagea',
                'owner_id': '1'
            }
    }

    def test_get_objects_and_total_count(self, mocker):
        user_id = 1
        mocked_response = [
            {'posts': {'N': '0'},
             'followers': {'N': '5'},
             'uuid': {'S': 'another uuidaaa'},
             'unblock_date': {'S': 'None'},
             'id': {'N': '41'},
             'name': {'S': 'another pagea'},
             'owner_id': {'N': '1'}}
        ]

        mocker.patch("core.aws.dynamodb_client.DynamoDBClient.scan", return_value=mocked_response)

        response = services.get_objects(settings.PAGES_NAME_TABLE, [user_id], 'owner_id')
        item = [v for k, v in response.items()]
        assert item[0]['owner_id'] == str(user_id)

    def test_total_objects_count(self):
        count = services.total_objects_count(self._objs_list, 'followers')
        assert count == 5

    def test_stats_service(self, mocker):
        mocked_response_total_count = 10

        mocker.patch("core.services.stats_service.get_objects", return_value=self._objs_list)
        mocker.patch("core.services.stats_service.total_objects_count", return_value=mocked_response_total_count)

        response = stats_service.StatisticsService.processing_stats(1)
        assert response.pages == self._objs_list
        assert response.posts == self._objs_list
        assert response.total_likes == mocked_response_total_count
        assert response.total_followers == mocked_response_total_count
        assert response.total_pages == len(self._objs_list)
        assert response.total_posts == len(self._objs_list)
