from django.contrib import admin
from django.urls import path
from app_server import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Gerenciamento
    path('', views.lista_produtos, name='lista_produtos'),
    path('novo/', views.criar_produto, name='criar_produto'),
    path('editar/<int:id>/', views.editar_produto, name='editar_produto'),
    path('excluir/<int:id>/', views.excluir_produto, name='excluir_produto'),

    # Catálogo do cliente
    path("catalogo/", views.catalogo_cliente, name="catalogo_cliente"),

    # Carrinho
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),

    # Adicionar 1 unidade
    path("add/<int:produto_id>/", views.add_carrinho, name="add_carrinho"),

    # Adicionar com quantidade escolhida
    path("add/<int:produto_id>/<int:qtd>/", views.add_carrinho, name="add_carrinho_qtd"),

    # Menos 1
    path("menos/<int:produto_id>/", views.remove_carrinho, name="remove_carrinho"),

    # Remover item completo
    path("remover/<int:produto_id>/", views.remover_item, name="remover_item"),

    # Finalizar compra (desconta estoque + vai pro WhatsApp)
    path("finalizar_venda/", views.finalizar_compra, name="finalizar_venda"),
]
