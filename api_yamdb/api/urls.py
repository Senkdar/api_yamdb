from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupViewSet,
    TitleViewSet,
    UserViewSet,
    get_token,
)

router_v1 = routers.DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet)
router_v1.register('categories', CategoryViewSet)

router_v1.register(
    prefix='auth/signup',
    viewset=SignupViewSet
)
router_v1.register(
    prefix='users',
    viewset=UserViewSet
)
router_v1.register(
    prefix=r'^titles/(?P<title_id>\d+)/reviews',
    viewset=ReviewViewSet,
    basename='reviews',
)
router_v1.register(
    prefix=r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    viewset=CommentViewSet,
    basename='comments',
)

urlpatterns = [
    path('v1/auth/token/', get_token, name='get_token'),
    path('v1/', include(router_v1.urls))
]
