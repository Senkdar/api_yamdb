from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)

from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModerator
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleSerializer,
    UserSerializer,
)


@api_view(['POST'])
def get_token(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if username is None or confirmation_code is None:
        return Response(status=HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirmation_code):
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=HTTP_200_OK)

    return Response(status=HTTP_400_BAD_REQUEST)


class SignupViewSet(CreateModelMixin, GenericViewSet):
    """Вьюсет для регистрации пользователей."""
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        email = serializer.validated_data.get('email')
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Confirmation Code from Ya.MDB',
            message=f'Confirmation code: {confirmation_code}',
            from_email=settings.FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request):
        response = super().create(request)

        return (
            Response(response.data, status=HTTP_200_OK)
            if response.status_code == HTTP_201_CREATED
            else response
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User (пользователь)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, IsAdmin,)

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request,):
        if request.method == 'PATCH':
            request_data = request.data.copy()
            if request.user.is_user:
                request_data['role'] = User.USER
            serializer = UserSerializer(
                request.user,
                data=request_data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review (отзыв)."""
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrModerator,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment (комментарий)."""
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrModerator,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title (произведение)."""
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleReadSerializer
        return TitleSerializer

    def get_queryset(self):
        genre = self.request.query_params.get('genre', r'.*')
        category = self.request.query_params.get('category', r'.*')
        name = self.request.query_params.get('name', r'.*')
        year = self.request.query_params.get('year', r'.*')

        return Title.objects.filter(
            year__regex=year,
            name__regex=name,
            category__slug__regex=category,
            genre__slug__regex=genre,
        ).annotate(rating=Avg('reviews__score'))


class ArtsClassesViewSet(
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый класс для вьюсетов группировки произведений искусства."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ArtsClassesViewSet):
    """Вьюсет для модели Genre (жанр)."""
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class CategoryViewSet(ArtsClassesViewSet):
    """Вьюсет для модели Category (категория)."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
