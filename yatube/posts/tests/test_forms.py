from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User

User = get_user_model()

class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create(username='Author')
        cls.group = Group.objects.create(
        title='Test',
        slug = 'test',
        description = 'test',
        )
        cls.post = Post.objects.create(
                id = 1,
                text = 'Тест1',
                author = cls.author,
                group = cls.group
            )
        cls.form  = PostForm()
    
    def setUp(self):
        self.user = User.objects.create_user(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
    
    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Что-то такое',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data = form_data, #что сюда передать
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_edit_post(self):
        self.post.text = self.post.text + 'new'
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(10,)),
            data = form_data,
        )
        self.post.refresh_from_db()
        post_two = get_object_or_404(Post, id=1)
        self.assertNotEqual(self.post.text, 'Тест1new')
