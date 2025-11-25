from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto
from .forms import ProdutoForm


# ------------------------------
# GERENCIAMENTO
# ------------------------------

def lista_produtos(request):
    busca = request.GET.get("q", "")
    produtos = Produto.objects.filter(nome__icontains=busca)
    return render(request, "lista_produtos.html", {"produtos": produtos, "busca": busca})


def criar_produto(request):
    if request.method == "POST":
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_produtos")

    form = ProdutoForm()
    return render(request, "form_produto.html", {"form": form})


def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    form = ProdutoForm(request.POST or None, instance=produto)

    if form.is_valid():
        form.save()
        return redirect("lista_produtos")

    return render(request, "form_produto.html", {"form": form})


def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    return redirect("lista_produtos")


# ------------------------------
# CATÁLOGO CLIENTE
# ------------------------------

def catalogo_cliente(request):
    busca = request.GET.get("q", "")
    produtos = Produto.objects.filter(nome__icontains=busca)

    # força não usar cache
    return render(request, "catalogo_cliente.html", {
        "produtos": produtos,
        "busca": busca
    })

# ------------------------------
# CARRINHO
# ------------------------------

def get_carrinho(request):
    return request.session.get("carrinho", {})


def salvar_carrinho(request, carrinho):
    request.session["carrinho"] = carrinho
    request.session.modified = True


# ADD com quantidade
def add_carrinho(request, produto_id, qtd=1):
    produto = get_object_or_404(Produto, id=produto_id)

    # 🚫 BLOQUEIA preço zero
    if produto.preco <= 0:
        return redirect("catalogo_cliente")

    # 🚫 BLOQUEIA estoque zero
    if produto.estoque <= 0:
        return redirect("catalogo_cliente")

    qtd = int(qtd)
    carrinho = request.session.get("carrinho", {})
    atual = carrinho.get(str(produto_id), 0)

    # 🔒 NÃO DEIXA ULTRAPASSAR O ESTOQUE
    if atual + qtd > produto.estoque:
        carrinho[str(produto_id)] = produto.estoque
    else:
        carrinho[str(produto_id)] = atual + qtd

    request.session["carrinho"] = carrinho
    request.session.modified = True

    return redirect("catalogo_cliente")



def remove_carrinho(request, produto_id):
    produto_id = str(produto_id)
    carrinho = get_carrinho(request)

    if produto_id in carrinho:
        carrinho[produto_id] -= 1
        if carrinho[produto_id] <= 0:
            del carrinho[produto_id]

    salvar_carrinho(request, carrinho)
    return redirect("ver_carrinho")


def remover_item(request, produto_id):
    produto_id = str(produto_id)
    carrinho = get_carrinho(request)

    if produto_id in carrinho:
        del carrinho[produto_id]

    salvar_carrinho(request, carrinho)
    return redirect("ver_carrinho")


# Página do carrinho
def ver_carrinho(request):
    carrinho = get_carrinho(request)
    produtos = []
    total = 0

    for item_id, qtd in carrinho.items():
        produto = Produto.objects.get(id=item_id)
        subtotal = produto.preco * qtd
        total += subtotal
        produtos.append({
            "produto": produto,
            "quantidade": qtd,
            "subtotal": subtotal
        })

    return render(request, "carrinho.html", {"produtos": produtos, "total": total})


# ------------------------------
# FINALIZAR COMPRA (estoque + Zap)
# ------------------------------

def finalizar_compra(request):
    carrinho = request.session.get("carrinho", {})

    if not carrinho:
        return redirect("ver_carrinho")

    texto = "Olá! Tenho interesse nestes produtos:%0A%0A"

    for produto_id, quantidade in carrinho.items():
        if produto.preco <= 0:
            continue  # ignora itens com preço zero

        produto = Produto.objects.get(id=produto_id)
        quantidade = int(quantidade)
        subtotal = produto.preco * quantidade

        # 🔥 DESCONTA DO ESTOQUE
        if produto.estoque >= quantidade:
            produto.estoque -= quantidade
            produto.save()

        texto += f"- {quantidade}x {produto.nome} (R$ {subtotal})%0A"

    total = sum(
        Produto.objects.get(id=i).preco * q for i, q in carrinho.items()
    )
    texto += f"%0ATotal: R$ {total}"

    # Limpa carrinho
    request.session["carrinho"] = {}

    # Número do cliente
    numero = "5585991857797"

    # Redireciona automaticamente pro WhatsApp
    return redirect(f"https://wa.me/{numero}?text={texto}")
