import datetime as dt

from django.conf import settings
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей"""

    def validate_username(self, value):
        if str(value).lower() in settings.INVALID_USERNAMES:
            raise serializers.ValidationError(
                'Нельзя такое имя'
            )
        return value

    class Meta:
        fields = fields = (
            "username",
            "email"
        )
        model = User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""
    class Meta:
        fields = fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role"
        )
        model = User


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов на произведения."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
            'title'
        )
        read_only_fields = ('title',)

    def validate(self, data):
        request = self.context['request']

        if request.method == 'POST':
            parser = self.context['request'].parser_context
            title_id = parser.get('kwargs', {}).get('title_id')
            if Review.objects.filter(
                title__id=title_id,
                author=request.user,
            ).exists():
                raise serializers.ValidationError(
                    'Можно оставить только один отзыв к произведению'
                )

        return data

    def validate_score(self, value):
        """Валидация поля score:
            оценка должна быть от 1 до 10.
        """
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка должна быть от 1 до 10')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )
        read_only_fields = ('review',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений искусств"""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений искусств"""
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleBaseSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'rating',
            'genre',
            'category',
        )

    def get_rating(self, obj):
        if hasattr(obj, 'rating') and obj.rating:
            return int(obj.rating)
        return None


class TitleReadSerializer(TitleBaseSerializer):
    """Сериализатор для чтения произведений искусства"""
    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)


class TitleSerializer(TitleBaseSerializer):
    """Сериализатор для работы с произведениями искусства."""
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=False,
        slug_field='slug',
    )

    def validate_year(self, value):
        current_year = dt.datetime.today().year

        if value > current_year:
            raise serializers.ValidationError(
                'Год создания произведения не может быть из будущего!',
            )
        return value
