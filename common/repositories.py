from typing import List

from .api import BrickInstanceMessagesApi
from scaladecore.entities import BrickInstanceMessageEntity


class BrickInstanceMessagesRepository:
    def __init__(self):
        self.api = BrickInstanceMessagesApi()

    def get_all(self, bi_uuid) -> List[BrickInstanceMessageEntity]:
        resp, ok, err = self.api.select_all_by_bi_uuid(bi_uuid)
        if not ok:
            raise Exception(
                'An error occurred while retrieving brick instance messages: "%s"' % err)
        messages = []
        for item in resp['Items']:
            item_d = {**item}
            item_d['created'] = float(item_d['created'])
            messages.append(
                BrickInstanceMessageEntity.create_from_dict(item_d))
        return messages
