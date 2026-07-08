from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Kilometer(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponível"
        PENDING = "pending", "Aguardando conferência do PIX"
        CONFIRMED = "confirmed", "Confirmado"

    number = models.PositiveSmallIntegerField(
        "KM",
        unique=True,
        validators=(MinValueValidator(1), MaxValueValidator(160)),
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    sponsor_name = models.CharField("Nome do apoiador", max_length=120, blank=True)
    donor_email = models.EmailField("E-mail", blank=True)
    donor_phone = models.CharField("WhatsApp", max_length=40, blank=True)
    amount = models.DecimalField("Valor", max_digits=8, decimal_places=2, blank=True, null=True)
    pix_receipt = models.FileField("Comprovante PIX", upload_to="receipts/", blank=True)
    donor_message = models.TextField("Mensagem", max_length=280, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("number",)

    def __str__(self):
        return f"KM {self.number:03d}"
