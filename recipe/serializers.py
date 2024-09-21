'''Serializers for recipe app'''
from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient




# Create a new class IngredientSerializer that inherits from serializers.ModelSerializer
class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)



# Create a new class TagSerializer that inherits from serializers.ModelSerializer
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)



# Create a new class RecipeSerializer that inherits from serializers.ModelSerializer
class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'time_minutes', 'price', 'link', 
            'tags', 'ingredients',
        )
        read_only_fields = ('id',)

    
    def _get_or_create_tags(self,tags,recipe):
        """Get or create tags"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=recipe.user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self,ingredients,recipe):
        """Get or create ingredients"""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=recipe.user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a new recipe"""
        tags = validated_data.pop('tags',[])
        ingredients = validated_data.pop('ingredients',[])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags,recipe)
        self._get_or_create_ingredients(ingredients,recipe)
        
        return recipe
    

    def update(self,instance,validated_data):
        """Update a recipe"""
        tags = validated_data.pop('tags',None)
        ingredients=validated_data.pop('ingredients',None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags,instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients,instance)

        for attr, value in validated_data.items():
            setattr(instance,attr,value)

        instance.save()
        return instance

# Create a new class RecipeDetailSerializer that inherits from RecipeSerializer
class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description',)
        read_only_fields = ('id',)



# Create a new class RecipeImageSerializer that inherits from serializers.ModelSerializer
class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes"""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
        extra_kwargs = {'image': {'required': 'True'}}