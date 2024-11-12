error_messages = {'clan_edit': 'Клан с таким названием или префиксом уже существует'}


class UniqueError(Exception):
    def __init__(self, error_type):
        self.error_message = error_messages[error_type]
