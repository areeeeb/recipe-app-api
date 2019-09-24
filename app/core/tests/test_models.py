from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@example.com', password='testpass'):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Test creating a new user with email"""
        email = 'test@example.com'
        password = 'password123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_is_normalized(self):
        """Test if the email is saved as lower case into the database"""
        email = 'upper@EMAIL.COM'

        user = get_user_model().objects.create_user(email=email)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test if creating new user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123 ')

    def test_create_new_super_user(self):
        """Test if a new superuser is created"""
        email = 'test@example.com'
        password = 'pass1234'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the string representation of the tag model"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the string representation of the ingredient model"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Chocolate'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe object is created and its string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
