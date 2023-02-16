from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post, User

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Author')
        cls.group = Group.objects.create(
            title ='No',
            slug = 'No',
            description = 'No'
        )
        cls.post = Post.objects.create(
            id = 1,
            text = 'Тестовый текст',
            author = cls.author,
            group = cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_template(self):
        template_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html'
        }

        if self.guest_client:
            for address, template in template_url_names.items():
                with self.subTest(address=address):
                    if self.guest_client:
                        response = self.guest_client.get(address)
                        self.assertTemplateUsed(response, template)

        elif self.authorized_client:
            address = '/create/'
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, 'posts/create_post.html')

                
        elif response.user == self.post.author:
            address = '/posts/<post_id>/edit/'
            with self.subTest(address=address):
                response = self.user.get(address)
                self.assertTemplateUsed(response, 'posts/create_post.html')



