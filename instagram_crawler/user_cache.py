import redis


class UserCache(object):

    _instance = None
    SEEN_USERS_SET_KEY = 'seen_users'

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            # TODO set passwords, logical db and such
            cls._instance = redis.StrictRedis()
        return cls._instance

    @classmethod
    def user_parsed(cls, username):
        return cls.get_instance().sismember(cls.SEEN_USERS_SET_KEY, username)

    @classmethod
    def add_to_parsed(cls, username):
        cls.get_instance().sadd(cls.SEEN_USERS_SET_KEY, username)

    @classmethod
    def set_followers(cls, user, followers_list):
        cls.get_instance().set(user, followers_list)

    @classmethod
    def get_followers(cls, user):
        cls.get_instance().get(user)

    @classmethod
    def remove_user(cls, user):
        cls.get_instance().delete(user)

    @classmethod
    def get_all_parsed_user_following(cls):
        all_following = []
        for user in cls.get_instance().keys():
            if user != cls.SEEN_USERS_SET_KEY:
                all_following.extend(cls.get_followers(user))