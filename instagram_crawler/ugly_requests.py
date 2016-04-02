import requests
import json

def get_following(username, user_id):

    headers = {
        'cookie': 'mid=VnUVzAAEAAFrsUJBFRzd5lqhoQfx; datr=-l2JVh_rEOhYoXPsmZsnXe8y; _ga=GA1.2.1352834737.1451843071; sessionid=IGSC5316be210fbe6559d47f3e5689940e321d1f4f8c36181e0595779748e3682bed%3AkLh2N1cWaSE6mc3xhzgTM6ge7oGvh5Sa%3A%7B%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A2395051068%2C%22_token%22%3A%222395051068%3Az1Pag9SQIdFYdob3LGwZZAzlUyNjSkcd%3Acf3fd0ef51589ddb20adbf9d89e803167dbe60f113b333f97e43db35b5ed62c9%22%2C%22asns%22%3A%7B%2231.168.24.50%22%3A8551%2C%22time%22%3A1459500796%7D%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22last_refreshed%22%3A1459500797.5551%2C%22_platform%22%3A4%7D;csrftoken=75b8594610eb3c8e6903e22d2472e7ba;',
        'origin': 'https://www.instagram.com',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'he-IL,he;q=0.8,en-US;q=0.6,en;q=0.4',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-csrftoken': '75b8594610eb3c8e6903e22d2472e7ba',
        'x-instagram-ajax': '1',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': '*/*',
        'referer': 'https://www.instagram.com/{}/'.format(username),
        'authority': 'www.instagram.com',
    }

    data = 'q=ig_user({})+%7B%0A++follows.first(10)+%7B%0A++++count%2C%0A++++page_info+%7B%0A++++++end_cursor%2C%0A++++++has_next_page%0A++++%7D%2C%0A++++nodes+%7B%0A++++++id%2C%0A++++++is_verified%2C%0A++++++followed_by_viewer%2C%0A++++++requested_by_viewer%2C%0A++++++full_name%2C%0A++++++profile_pic_url%2C%0A++++++username%0A++++%7D%0A++%7D%0A%7D%0A&ref=relationships%3A%3Afollow_list'.format(user_id)

    response = requests.post('https://www.instagram.com/query/', headers=headers, data=data)

    if response and response.status_code == 200 and response.content:
        content_json = json.loads(response.content)
        if content_json and 'follows' in content_json and 'nodes' in content_json['follows']:
            user_follows = []
            for follower in content_json['follows']['nodes']:
                user_follows.append(follower['username'])
            return user_follows
        else:
            return None


if __name__ == '__main__':
    print get_following('_amit_paz', '19092040')