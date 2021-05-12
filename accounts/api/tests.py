from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = "/api/accounts/login/"
LOGOUT_URL = "/api/accounts/logout/"
SIGNUP_URL = "/api/accounts/signup/"
LOGIN_STATUS_URL = "/api/accounts/login_status/"

class AccountApiTests(TestCase):

    def setUp(self):
        # 这个函数会在每个 test function 执行的时候被执行
        self.client = APIClient()
        self.user = self.createUser(
            username="admin",
            password="correct password",
            email="admin@jiuzhang.com",
        )

    def createUser(self, username, password, email):
        # 不能使用User.objects.create()
        # 因为password需要被加密，username和email需要进行一些normalize的处理。
        return User.objects.create_user(username, email, password)

    # 每个测试函数必须以 test_ 开头，才会被自动调用进行测试
    # 测试必须用 post 而不是 get
    def test_login(self):
        response = self.client.get(LOGIN_URL, {
            "username": self.user.username,
            "password": 'correct password',
        })

        # 登陆失败，http status code 返回 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # 用了post，但是密码错误
        response = self.client.post(LOGIN_URL, {
            "username": self.user.username,
            "password": 'wrong password'
        })
        self.assertEqual(response.status_code, 400)

        # 验证还没有登陆
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # 用正确的密码
        response = self.client.post(LOGIN_URL, {
            "username": self.user.username,
            "password": 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], "admin@jiuzhang.com")

        # 验证已经登录了
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # 先登录
        self.client.post(LOGIN_URL, {
            "username": self.user.username,
            "password": "correct password",
        })

        # 验证用户已经登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # 测试必须用post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # 改用post，成功logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # 验证用户已经登出
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'password': 'any password',
            'email': 'someone@twitter.com',
        }

        # 测试get请求失败
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # 测试错误的邮箱
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'password': 'any password',
            'email': 'not a correct email address',
        })
        self.assertEqual(response.status_code, 400)

        # 测试密码太短
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'password': '123',
            'email': 'someone@twitter.com',
        })
        self.assertEqual(response.status_code, 400)

        # 测试用户名太长
        response = self.client.post(SIGNUP_URL, {
            'username': 'asfjkadfjlakdfjlaoir oqiwuer023',
            'password': 'any password',
            'email': 'someone@twitter.com',
        })
        self.assertEqual(response.status_code, 400)

        # 成功注册
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # 验证用户已经成功登入
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


