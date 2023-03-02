# from django import forms
# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase
# from users.forms import CreationForm


# from .const import ANOTHERUSER, REVERSE_SIGNUP, USER_DATA

# User = get_user_model()


# class SignUpTest(TestCase):
#     def setUp(self):
#         self.guest_client = Client()
#         # self.user = User.objects.create_user(username=ANOTHERUSER)
#         # self.authorized_client = Client()
#         # self.authorized_client.force_login(self.user)
#         self.user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password1': 'testpassword', 'password2': 'testpassword'}
#         self.form_data = CreationForm(data=USER_DATA)

#     def test_signup_page_show_correct_context(self):
#         responce = self.guest_client.get(REVERSE_SIGNUP)
#         form_fields = {
#             "first_name": forms.fields.CharField,
#             "last_name": forms.fields.CharField,
#             "username": forms.fields.CharField,
#             "email": forms.fields.EmailField,
#         }
#         for field, expected_type in form_fields.items():
#             with self.subTest(field=field):
#                 form_field = responce.context["form"].fields[field]
#                 self.assertIsInstance(form_field, expected_type)


#     def test_signup_view(self):
#         response = self.guest_client.post(REVERSE_SIGNUP, data=USER_DATA)
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())


#     def test_signup_form(self):
#         self.assertTrue(self.form_data.is_valid())

