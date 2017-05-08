import requests as r

from gitter.const import GITTER_BASE_URL
from gitter.errors import GitterTokenError, GitterApiError


class BaseApi:
    def __init__(self, token):
        if not token:
            raise GitterTokenError
        self.token = token

    def request_process(self, method, api, **kwargs):
        headers = {
            'Authorization': 'Bearer ' + self.token,
        }
        return method(GITTER_BASE_URL + api, headers=headers, **kwargs).json()

    def get(self, api, **kwargs):
        return self.request_process(r.get, api, **kwargs)

    def post(self, api, **kwargs):
        return self.request_process(r.post, api, **kwargs)

    def put(self, api, **kwargs):
        return self.request_process(r.put, api, **kwargs)

    def delete(self, api, **kwargs):
        return self.request_process(r.delete, api, **kwargs)

    def check_auth(self):
        return self.get('user')

    @property
    def get_user_id(self):
        return self.check_auth()[0]['id']

    @property
    def rooms_list(self):
        return self.get('rooms')

    @property
    def groups_list(self):
        return self.get('groups')

    def find_by_room_name(self, name):
        room_id = ''
        for x in self.rooms_list:
            if x['name'] == name:
                room_id = x['id']

        return room_id


class Auth(BaseApi):
    @property
    def get_my_id(self):
        user_id = self.check_auth()[0]['id']
        name = self.check_auth()[0]['username']
        return {'Name': name, 'user_id': user_id}


class Groups(BaseApi):
    @property
    def list(self):
        return self.groups_list


class Rooms(BaseApi):
    def grab_room(self, uri_name):
        return self.post('rooms', data={'uri': uri_name})

    def join(self, room_name):
        user_id = self.get_user_id
        api_meth = 'user/{}/rooms'.format(user_id)
        return self.post(
            api_meth,
            data={'id': self.find_by_room_name(room_name)}
        )

    def leave(self, room_name, _user_id=None):
        user_id = self.get_user_id
        api_meth = 'rooms/{}/users/{}'.format(
            self.find_by_room_name(room_name),
            user_id if user_id else _user_id
        )

        return self.delete(api_meth)

    def update(self, room_name, topic, no_index=None, tags=None):
        api_meth = 'rooms/{}'.format(self.find_by_room_name(room_name))
        return self.put(
            api_meth,
            data={'topic': topic, 'noindex': no_index, 'tags': tags}
        )

    def delete_room(self, room_name):
        api_meth = 'rooms/{}'.format(self.find_by_room_name(room_name))
        return self.delete(api_meth)

    def sub_resource(self, room_name):
        api_meth = 'rooms/{}/users'.format(self.find_by_room_name(room_name))
        return self.get(api_meth)


class Messages(BaseApi):
    def list(self, room_name):
        room_id = self.find_by_room_name(room_name)
        api_meth = 'rooms/{}/chatMessages'.format(room_id)
        return self.get(api_meth)

    def send(self, room_name, text='GitterHQPy test message'):
        room_id = self.find_by_room_name(room_name)
        api_meth = 'rooms/{}/chatMessages'.format(room_id)
        return self.post(api_meth, data={'text': text})


class User(BaseApi):
    def current_user(self):
        return self.check_auth()

    def sub_resource(self):
        api_meth = 'user/{}/rooms'.format(self.get_user_id)
        return self.get(api_meth)

    def unread_items(self, room_name):
        api_met = 'user/{}/rooms/{}/unreadItems'.format(
            self.get_user_id,
            self.find_by_room_name(room_name)
        )
        return self.get(api_met)

    @property
    def orgs(self):
        api_meth = 'user/{}/orgs'.format(self.get_user_id)
        return self.get(api_meth)

    @property
    def repos(self):
        api_meth = 'user/{}/repos'.format(self.get_user_id)
        return self.get(api_meth)

    @property
    def channels(self):
        api_meth = 'user/{}/channels'.format(self.get_user_id)
        return self.get(api_meth)

    # Method will be refactor
    # def mark_as_read(self, room_name, chat):
    #     if chat and isinstance(chat, list):
    #         chat = [self.find_by_room_name(name) for name in chat]
    #     else:
    #         raise GitterApiError('Chat argument must be a list.')
    #     api_meth = 'user/{}/rooms/{}/unreadItems'.format(
    #         self.get_user_id,
    #         self.find_by_room_name(room_name),
    #     )
    #     return self.post(api_meth, data={'chat': chat})


class GitterClient(BaseApi):
    def __init__(self, token=None):
        super().__init__(token)
        self.auth = Auth(token)
        self.groups = Groups(token)
        self.rooms = Rooms(token)
        self.message = Messages(token)
        self.user = User(token)

gitter = GitterClient('29ee4e6f41fb6835196996dbd682c5e47e503bb7')
print(gitter.user.channels)