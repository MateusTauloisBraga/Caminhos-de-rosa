from django import forms

from .models import Kilometer


class KilometerSponsorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.minimum_amount = kwargs.pop("minimum_amount", 30)
        super().__init__(*args, **kwargs)
        for field_name in ("sponsor_name", "donor_phone", "amount"):
            if field_name in self.fields:
                self.fields[field_name].required = True
        self.fields["amount"].widget.attrs["min"] = str(self.minimum_amount)
        self.fields["amount"].initial = self.minimum_amount

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount < self.minimum_amount:
            raise forms.ValidationError(f"O valor mínimo para esta reserva é R$ {self.minimum_amount}.")
        return amount

    class Meta:
        model = Kilometer
        fields = ("sponsor_name", "amount", "donor_message")
        labels = {
            "sponsor_name": "Nome",
            "amount": "Valor do auxílio",
            "donor_message": "Mensagem",
        }
        help_texts = {
            "sponsor_name": "É esse nome que vai pousar no quilômetro depois da conferência.",
            "amount": "Mínimo de R$ 30 por quilômetro escolhido.",
            "donor_message": "Opcional. Deixe uma palavra para seguir junto na travessia.",
        }
        widgets = {
            "amount": forms.NumberInput(attrs={"min": "1", "step": "0.01"}),
            "donor_message": forms.Textarea(attrs={"rows": 4}),
        }
