from typing import Type


class InconsistentStateChangeError(Exception):
    def __init__(self, entity_class: Type, current_status: str, updated_status: str):
        self.entity_class = entity_class
        self.current_status = current_status
        self.updated_status = updated_status

    def __str__(self):
        return "Inconsistent state change error: '{0}' from '{1}' to '{2}' status.".format(
            self.entity_class.__name__,
            self.current_status,
            self.updated_status,
        )
