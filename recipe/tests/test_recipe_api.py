'''Test for the recipe API'''
import os   
import tempfile
from PIL import Image

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse('recipe:recipe-list')




# def create_user(**params):
#     """Create a sample user"""  
#     return get_user_model().objects.create_user(**params)

def create_user(email='user@example.com', password='testpass123'):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample description',
        'link': 'http://example.com/sample-recipe.pdf',
    }
    defaults.update(params)

    recipe=Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user=create_user(email='user@example.com', password='testpass')
        self.client.force_authenticate(self.user)
    

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)


        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 =create_user(email='other@example.com',password='testpass')
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res=self.client.get(RECIPE_URL)

        recipe=Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.00'),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)


    def test_partial_upadte(self):
        """Test updating a recipe with patch"""
        original_link='http://example.com/original-recipe.pdf'
        recipe=create_recipe(
                user=self.user, 
                title='Original title',
                link=original_link
            )

        payload={'title':'New title'}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
        

    def test_full_update(self):
        """Test updating a recipe with put"""
        recipe=create_recipe(
            user=self.user,
            title='Original title',
            link='http://example.com/original-recipe.pdf',
            description='Original description',
        )
        payload={
            'title':'Updated title',
            'time_minutes':25,
            'price':Decimal('5.00'),
            'link':'http://example.com/updated-recipe.pdf',
            'description':'Updated description',
        }
        url=detail_url(recipe.id)
        res=self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    
    def test_update_user_return_error(self):
        """Test updating a recipe with put"""
        new_user=create_user(email='user2@example.com', password='testpass')
        recipe=create_recipe(user=self.user)

        payload={'user':new_user.id}
        url=detail_url(recipe.id)
        res=self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)


    def test_delete_recipe(self):
        """Test deleting a recipe"""
        recipe=create_recipe(user=self.user)

        url=detail_url(recipe.id)
        res=self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
    

    def test_recipe_other_user_recipe_error(self):
        """Test deleting a recipe"""
        new_user=create_user(email='user2@example.com', password='testpass')
        recipe=create_recipe(user=new_user)

        url=detail_url(recipe.id)
        res=self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())


    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with tags"""
        payload={
            'title':'Avocado lime cheesecake',
            'tags':[{ 'name':'Vegan'}, {'name':'Dessert'}],
            'time_minutes':60,
            'price':Decimal('20.00'),
        }
        res=self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)

        recipe=recipe[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists=recipe.tags.filter(
                name=tag['name'],  
                user=self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with tags"""
        tag_bd=Tag.objects.create(user=self.user, name='Vegan')

        payload={
            'title':'Avocado lime cheesecake',
            'tags':[{'name':'Vegan'}, {'name':'Dessert'}],
            'time_minutes':60,
            'price':Decimal('20.00'),
        }   
        res=self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recipe=recipe[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_bd, recipe.tags.all())
        for tag in payload['tags']:
            exists=recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_tag_on_update(self):
        """Test creating a tag on update"""
        recipe=create_recipe(user=self.user)

        payload={'tags':[{'name':'Vegan'}]}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag=Tag.objects.get(user=self.user, name='Vegan')
        self.assertIn(new_tag, recipe.tags.all())


    def test_update_recipe_assign_tag(self):
        """Test updating a recipe with tags"""
        tag_breakfast=Tag.objects.create(user=self.user, name='Breakfast')
        recipe=create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch=Tag.objects.create(user=self.user, name='Lunch')
        payload={'tags':[{'name':'Lunch'}]}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())
    
    def test_clear_recipe_tags(self):
        """Test clearing all tags from a recipe"""
        tag=Tag.objects.create(user=self.user, name='Breakfast')
        recipe=create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload={'tags':[]}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
        
    
    def test_create_recipe_with_new_ingredient(self):
        """Test creating a recipe with ingredients"""
        payload={
            'title':'Avocado lime cheesecake',
            'ingredients':[{'name':'Avocado'}, {'name':'Lime'}],
            'time_minutes':60,
            'price':Decimal('20.00'),
        }
        res=self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recipe=recipe[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists=recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_create_with_existing_ingredient(self):
        """Test creating a recipe with ingredients"""
        ingredient=Ingredient.objects.create(user=self.user, name='Avocado')
        payload={
            'title':'Avocado lime cheesecake',
            'ingredients':[{'name':'Avocado'}, {'name':'Lime'}],
            'time_minutes':60,
            'price':Decimal('20.00'),
        }
        res=self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recipe=recipe[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists=recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_create_ingredient_on_update(self):
        """Test creating an ingredient on update"""
        recipe=create_recipe(user=self.user)

        payload={'ingredients':[{'name':'Avocado'}]}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient=Ingredient.objects.get(user=self.user, name='Avocado')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """Test updating a recipe with ingredients"""
        ingredient1=Ingredient.objects.create(user=self.user, name='Bread')
        recipe=create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2=Ingredient.objects.create(user=self.user, name='Butter')
        payload={'ingredients':[{'name':'Butter'}]}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing all ingredients from a recipe"""
        ingredient=Ingredient.objects.create(user=self.user, name='Bread')
        recipe=create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload={'ingredients':[]}
        url=detail_url(recipe.id)
        res=self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test returning recipes with specific text"""
        recipe1=create_recipe(user=self.user, title='Chicken Curry')
        recipe2=create_recipe(user=self.user, title='Vegetable Curry')
        tag1=Tag.objects.create(user=self.user, name='Chicken')
        tag2=Tag.objects.create(user=self.user, name='Vegetable')

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3=create_recipe(user=self.user, title='Fish and Chips')

        params={'tags':f'{tag1.id},{tag2.id}'}
        res=self.client.get(RECIPE_URL, params)

        serializer1=RecipeSerializer(recipe1)
        serializer2=RecipeSerializer(recipe2)
        serializer3=RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        recipe1=create_recipe(user=self.user, title='Posh beans on toast')
        recipe2=create_recipe(user=self.user, title='Chicken Curry')
        ingredient1=Ingredient.objects.create(user=self.user, name='Feta cheese')
        ingredient2=Ingredient.objects.create(user=self.user, name='Chicken')

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3=create_recipe(user=self.user, title='Steak and mushrooms')

        params={'ingredients':f'{ingredient1.id},{ingredient2.id}'}
        res=self.client.get(RECIPE_URL, params)

        serializer1=RecipeSerializer(recipe1)
        serializer2=RecipeSerializer(recipe2)
        serializer3=RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)



# # Test for the image upload
# class RecipeImageUploadTests(TestCase):
#     """Test image upload for recipe"""

#     def setUp(self):
#         self.client=APIClient()
#         self.user=create_user(
#             'user@example.com',
#             'testpass123',
#         )
#         self.client.force_authenticate(self.user)
#         self.recipe=create_recipe(user=self.user)
    
#     def tearDown(self):
#         self.recipe.image.delete()
    
#     def test_upload_image(self):
#         """Test uploading an image to recipe"""
#         url=image_upload_url(self.recipe.id)
#         with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
#             img=Image.new('RGB', (10,10))
#             img.save(image_file, format='JPEG')
#             image_file.seek(0)
#             res=self.client.post(url, {'image':image_file}, format='multipart')

#         self.recipe.refresh_from_db()
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn('image', res.data)
#         self.assertTrue(os.path.exists(self.recipe.image.path))

#     def test_upload_image_bad_request(self):
#         """Test uploading an invalid image"""
#         url=image_upload_url(self.recipe.id)
#         payload={'image':'notimage'}
#         res=self.client.post(url, payload, format='multipart')

#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class RecipeImageUploadTests(TestCase):
    """Test uploading images to recipes"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass123')
        self.client.force_authenticate(self.user)
        self.recipe = Recipe.objects.create(
            user=self.user,
            title='Sample recipe',
            time_minutes=10,
            price=5.00
        )

    def test_upload_image(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            res = self.client.post(url, {'image': image_file}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)