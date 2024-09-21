Overview
This API allows users to create and manage recipes, as well as categorize them with tags and ingredients. The API supports user authentication and provides CRUD operations for managing recipes, tags, and ingredients.

API Base URL
/api/
Authentication
The API uses token-based authentication.
Users need to be authenticated to access and modify recipes, tags, and ingredients.
Endpoints

1. Health Check
URL: /api/health-check/
Method: GET
Description: Check if the API is running.
Response:
json

{
  "healthy": true
}

2. User Management
Register New User
URL: /api/user/create/
Method: POST
Description: Create a new user account.
Request Body:
json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
Response:
json

{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}


Token Authentication
URL: /api/user/token/
Method: POST
Description: Obtain authentication token for the user.
Request Body:
json

{
  "email": "user@example.com",
  "password": "password123"
}
Response:
json

{
  "token": "your-jwt-token"
}


Manage User Profile
URL: /api/user/me/
Method: GET (Retrieve) / PUT (Update)
Description: Retrieve or update the authenticated user's profile.
Request:
json

{
  "name": "John Doe",
  "email": "user@example.com"
}
Response (for GET):
json

{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}


3. Recipe Management
List Recipes
URL: /api/recipe/recipes/
Method: GET
Description: Retrieve a list of recipes for the authenticated user. Supports filtering by tags and ingredients.
Response:
json

[
  {
    "id": 1,
    "title": "Chicken Curry",
    "time_minutes": 30,
    "price": "12.50",
    "tags": ["Dinner", "Spicy"],
    "ingredients": ["Chicken", "Curry powder"]
  },
  ...
]


Create a Recipe
URL: /api/recipe/recipes/
Method: POST
Description: Create a new recipe.
Request Body:
json


{
  "title": "Chicken Curry",
  "description": "Delicious spicy chicken curry",
  "time_minutes": 30,
  "price": "12.50",
  "tags": [1, 2],
  "ingredients": [1, 2]
}
Response:
json


{
  "id": 1,
  "title": "Chicken Curry",
  "time_minutes": 30,
  "price": "12.50",
  "tags": ["Dinner", "Spicy"],
  "ingredients": ["Chicken", "Curry powder"]
}
Retrieve a Recipe
URL: /api/recipe/recipes/{id}/
Method: GET
Description: Retrieve a specific recipe by its ID.
Response:
json


{
  "id": 1,
  "title": "Chicken Curry",
  "description": "Delicious spicy chicken curry",
  "time_minutes": 30,
  "price": "12.50",
  "tags": ["Dinner", "Spicy"],
  "ingredients": ["Chicken", "Curry powder"]
}


Update a Recipe
URL: /api/recipe/recipes/{id}/
Method: PUT / PATCH
Description: Update an existing recipe.
Request Body:
json

{
  "title": "Chicken Biryani",
  "time_minutes": 40,
  "price": "15.00"
}
Response:
json

{
  "id": 1,
  "title": "Chicken Biryani",
  "time_minutes": 40,
  "price": "15.00",
  "tags": ["Dinner", "Spicy"],
  "ingredients": ["Chicken", "Rice"]
}


Delete a Recipe
URL: /api/recipe/recipes/{id}/
Method: DELETE
Description: Delete a specific recipe by its ID.
Response: 204 No Content


4. Tag Management
List Tags
URL: /api/recipe/tags/
Method: GET
Description: Retrieve a list of tags created by the authenticated user.
Response:
json

[
  {
    "id": 1,
    "name": "Dinner"
  },
  {
    "id": 2,
    "name": "Spicy"
  }
]


Create a Tag
URL: /api/recipe/tags/
Method: POST
Description: Create a new tag.
Request Body:
json

{
  "name": "Vegetarian"
}
Response:
json

{
  "id": 3,
  "name": "Vegetarian"
}


5. Ingredient Management
List Ingredients
URL: /api/recipe/ingredients/
Method: GET
Description: Retrieve a list of ingredients created by the authenticated user.
Response:
json

[
  {
    "id": 1,
    "name": "Chicken"
  },
  {
    "id": 2,
    "name": "Curry powder"
  }
]


Create an Ingredient
URL: /api/recipe/ingredients/
Method: POST
Description: Create a new ingredient.
Request Body:
json

{
  "name": "Garlic"
}
Response:
json

{
  "id": 3,
  "name": "Garlic"
}


OpenAPI Documentation
With drf-spectacular, you can generate the schema and use Swagger or Redoc for documentation.

Schema URL: /api/schema/
Swagger Docs: /api/docs/
Make sure that in your settings.py, you have drf-spectacular properly configured, and this code is set up to render the documentation in Swagger UI.

Swagger View Example:

python
Copy code
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
]



## This Documentation is Generated by AI