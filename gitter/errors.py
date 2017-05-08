class GitterTokenError(Exception):
    def __str__(self): return 'Please provide your token'


class GitterMessageErorr(Exception):
    def __init__(self, room_name):
        self.room_name = room_name

    def __str__(self):
        return 'You don\'t have messages in {} room'.format(self.room_name)


class GitterApiError(Exception):
    pass
