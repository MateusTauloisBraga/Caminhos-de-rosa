from django.db import migrations, models


def create_kilometers(apps, schema_editor):
    Kilometer = apps.get_model("campaign", "Kilometer")
    Kilometer.objects.bulk_create(
        [Kilometer(number=number) for number in range(1, 161)],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Kilometer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveSmallIntegerField(unique=True, verbose_name="KM")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("available", "Disponível"),
                            ("pending", "Aguardando conferência do PIX"),
                            ("confirmed", "Confirmado"),
                        ],
                        default="available",
                        max_length=20,
                    ),
                ),
                ("sponsor_name", models.CharField(blank=True, max_length=120, verbose_name="Nome do apoiador")),
                ("donor_email", models.EmailField(blank=True, max_length=254, verbose_name="E-mail")),
                ("donor_phone", models.CharField(blank=True, max_length=40, verbose_name="WhatsApp")),
                ("amount", models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name="Valor")),
                ("pix_receipt", models.FileField(blank=True, upload_to="receipts/", verbose_name="Comprovante PIX")),
                ("donor_message", models.TextField(blank=True, max_length=280, verbose_name="Mensagem")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("number",)},
        ),
        migrations.RunPython(create_kilometers, migrations.RunPython.noop),
    ]
