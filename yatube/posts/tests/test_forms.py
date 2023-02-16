from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create(username='Author')
        cls.post = Post.objects.create(text='Тест1',
                                       author=cls.author,)
        cls.user = User.objects.create_user(username='Test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        group = Group.objects.create(title='Test',
                                     slug='test',
                                     description='test',)
        self.authorized_client.post(
            reverse('posts:post_create'),
            data={'text': 'Что-то такое',
                  'group': group.id},
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Что-то такое',
                group=group.id).exists())

    def test_edit_post(self):
        post = Post.objects.create(text='Тест1',
                                   author=self.author,)
        group = Group.objects.create(title='Test',
                                     slug='test',
                                     description='test',)
        self.post.text = post.text + 'new'
        form_data = {
            'text': post.text,
            'group': group.id
        }

        self.authorized_client.post(
            reverse('posts:post_edit', args=(10,)),
            data=form_data,)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.text, 'Тест1new')
