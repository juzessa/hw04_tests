from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from posts.constants import FIRST_TEN
from posts.models import Group, Post, User

User = get_user_model()


class PostViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='Test',
                                         slug='test',
                                         description='test',)
        cls.group2 = Group.objects.create(title='Test2',
                                          slug='test2',
                                          description='test2',)
        cls.author = User.objects.create(username='Author')
        for i in range(1, FIRST_TEN + 2):

            Post.objects.create(
                id=i,
                text='Тест' + str(i),
                author=cls.author,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        template_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'test'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'Author'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': '1'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }

        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_redirect(self):
        template_pages_names = {
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
            'posts/create_post.html'}

        for reverse_name, template in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                if not self.assertRedirects:
                    post = response.context['post']
                    if response.user == post.author:
                        self.assertTemplateUsed(response, template)
                    else:
                        self.assertRedirects(response,
                                             reverse
                                             ('posts:post_detail',
                                              kwargs={'post_id': '1'}))

    def test_index_page_shows_correct_context(self):
        test_list = Post.objects.select_related('author', 'group')
        response = self.authorized_client.get(reverse('posts:index'))
        post_list = response.context['post_list']
        self.assertQuerysetEqual(post_list, test_list, lambda x: x)

    def test_group_posts_page_shows_correct_context(self):
        group = get_object_or_404(Group, slug='test')
        test_post = group.posts.select_related('author')
        response = self.authorized_client.get(reverse('posts:group_list',
                                                      kwargs={'slug': 'test'}))
        posts = response.context['posts']
        self.assertQuerysetEqual(test_post, posts, transform=lambda x: x)

    def test_profile_page_shows_correct_context(self):
        author = get_object_or_404(User, username='Author')
        test_post = Post.objects.filter(author=author)
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'Author'}))
        posts = response.context['post_list']
        self.assertQuerysetEqual(test_post, posts, transform=lambda x: x)

    def test_post_detail_page_shows_correct_context(self):
        one_post = get_object_or_404(Post, id='1')
        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      kwargs={'post_id': 1}))
        test_post = response.context['one_post']
        self.assertEqual(one_post, test_post)

    def test_post_create_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_one_record(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 1)

    def test2_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': 'test'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test2_second_page_contains_one_record(self):
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': 'test'})
                                   + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 1)

    def test3_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:profile',
                                           kwargs={'username': 'Author'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test3_second_page_contains_one_record(self):
        response = self.client.get(reverse('posts:profile',
                                           kwargs={'username':
                                                   'Author'})
                                   + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_added(self):
        one_post = get_object_or_404(Post, id='1')
        response_dict = {reverse('posts:index'): 'post_list',
                         reverse('posts:group_list',
                         kwargs={'slug': 'test'}): 'posts',
                         reverse('posts:profile',
                         kwargs={'username': 'Author'}): 'post_list', }
        for page, context_variable in response_dict.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                if one_post.group:
                    self.assertIn(one_post, response.context[context_variable])

    def test_group_not_added(self):
        one_post = get_object_or_404(Post, id='1')
        response = self.client.get(reverse('posts:group_list',
                                           kwargs={'slug': 'test2'}))
        self.assertNotIn(one_post, response.context['posts'])
