from django.db import models

# Create your models here.
from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)

    imagem_url = models.TextField(blank=True)

    estoque = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.imagem_url = self._formatar_imagem(self.imagem_url)
        super().save(*args, **kwargs)

    def _formatar_imagem(self, valor):
        if not valor:
            return valor

        valor = valor.strip()

        # Se já tiver prefixo base64 → beleza
        if valor.startswith("data:image"):
            return valor

        # Se for apenas o código base64 → adicionar prefixo PNG
        if len(valor) > 50 and all(c.isalnum() or c in "+/=" for c in valor):
            return "data:image/png;base64," + valor

        # Caso seja URL normal → só retorna
        return valor

    def __str__(self):
        return self.nome
