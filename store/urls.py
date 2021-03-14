from django.urls import path, re_path

from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='index'),
    path('basket/', views.BasketView.as_view(), name='basket'),
    path('store/today/', views.today_view, name='store-today'),
    path('category/<slug:slug>/', views.CategoriesView.as_view(), name='category-detail'),
    re_path(r'^month/(?P<pk>[0-9]{2})/$', views.month_view, name='store-month'),
    path('p/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('send_mail/', views.MailingView.as_view(), name='mailing-app'),
    path('register/', views.FormView.as_view(), name='test_form'),
    path('validator/', views.ValidateView.as_view(), name='validator'),
    path('basket/add/', views.FillBasket.as_view(), name='add_to_basket'),
    path('basket/clear/', views.UpdateBasket.as_view(), name='clear_cart'),
    path('basket/update/', views.UpdateBasket.as_view(), name='update_cart'),
    path('api/', views.ApiView.as_view(), name='API'),
]
