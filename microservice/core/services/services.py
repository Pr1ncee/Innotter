from core.aws.dynamodb_client import DynamoDBClient


db = DynamoDBClient
hashable = int | float | str | tuple | None


def get_objects(table_name: str, pks: list[int], target_pk: str) -> dict:
    """
    Scan the given table and extract all the object's fields from it
    :param table_name: table to be scanned
    :param pks: list of primary keys which will be compared with
           (e.g. user has several pages which have several posts)
    :param target_pk: primary key to be scanned with
    :return: dict with the appropriate objects.
    """
    data = {}
    target_table = db.scan(table_name)
    for page in target_table:
        if int(*page[target_pk].values()) in pks:
            object_fields = {}
            for k, v in page.items():
                object_fields.update(
                    {k: str(*v.values())}
                )
            page_id = object_fields.pop('id')
            data.update({page_id: object_fields})
            
    return data


def total_objects_count(objects_list: dict[hashable, [hashable, int]], pk: hashable) -> int:
    """
    Figure out sum of field in nested dict
    :param objects_list: nested dict to be iterated
    :param pk: primary key to sum its value
    :return: int
    """
    return sum([int(fields[pk]) for _, fields in objects_list.items()])
