from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """Base view set for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        # we are using this function to to modify the queryset instead of the \
        # class variable because if we want to change the model in the future \
        # we just have to set the model in the queryset class variable.
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
            # here 'r' of recipe is small letter because of reverse relation

        return queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manager recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of IDs from string to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for the authenticated user only and
        filter them (by ingredients or tags) if the query params are
        provided"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        queryset = self.queryset

        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(
                tags__id__in=tags_ids
            )

        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(
                ingredients__id__in=ingredients_ids
            )

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        return serializer.save(user=self.request.user)

    @action(methods=['POST', 'GET'], detail=True, url_path='image')
    def image(self, request, pk=None):
        """Upload an image to the recipe"""
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = self.get_serializer(
                recipe,
                data=request.data
            )  # Passing recipe and the request data (image) to the serializer

            if serializer.is_valid():
                """Checking if the data passed in serializer is valid and then
                saving it"""
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'GET':
            serializer = self.get_serializer(
                recipe
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
