import redis
import msgpack

class UserCache(object):

    _instance = None
    SEEN_USERS_SET_KEY = 'seen_users'
    BLACK_LIST_KEY = 'black_list'

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
    def get_black_list(cls):
        blacklist = set()
        try:
            blacklist = cls.get_instance().smembers(cls.BLACK_LIST_KEY)
        except:
            print 'Error retrieving black list from redis!'

        return blacklist

    @classmethod
    def set_following(cls, user, followers_list):
        cls.get_instance().set(user, msgpack.packb(followers_list))

    @classmethod
    def get_following(cls, user):
        following = None
        try:
            following = msgpack.unpackb(cls.get_instance().get(user))
        except:
            print "could not unpack! user:{}".format(user)
        return following

    @classmethod
    def remove_user(cls, user):
        return cls.get_instance().delete(user)

    @classmethod
    def get_all_parsed_user_following(cls):
        all_following = set()
        all_users = cls.get_instance().keys()
        for user in all_users:
            if user != cls.SEEN_USERS_SET_KEY:
                user_following = cls.get_following(user)
                if user_following is not None:
                    for followee in user_following:
                        all_following.add(followee)
        return all_following