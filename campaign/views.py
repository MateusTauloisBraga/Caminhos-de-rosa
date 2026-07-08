from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urllib.parse import quote

from .forms import KilometerSponsorForm
from .models import Kilometer


def home(request):
    kilometers = Kilometer.objects.all()
    confirmed_count = kilometers.filter(status=Kilometer.Status.CONFIRMED).count()
    pending_count = kilometers.filter(status=Kilometer.Status.PENDING).count()
    available_count = kilometers.filter(status=Kilometer.Status.AVAILABLE).count()
    confirmed_total = kilometers.filter(status=Kilometer.Status.CONFIRMED).aggregate(total=Sum("amount"))["total"] or 0
    pending_total = kilometers.filter(status=Kilometer.Status.PENDING).aggregate(total=Sum("amount"))["total"] or 0
    reserved_total = confirmed_total + pending_total

    context = {
        "kilometers": kilometers,
        "confirmed_count": confirmed_count,
        "pending_count": pending_count,
        "available_count": available_count,
        "confirmed_total": confirmed_total,
        "pending_total": pending_total,
        "reserved_total": reserved_total,
        "confirmed_food_units": int(confirmed_total // settings.FOOD_UNIT_VALUE),
        "pending_food_units": int(pending_total // settings.FOOD_UNIT_VALUE),
        "reserved_food_units": int(reserved_total // settings.FOOD_UNIT_VALUE),
        "food_unit_value": settings.FOOD_UNIT_VALUE,
        "pix_key": settings.PIX_KEY,
        "suggested_km_value": settings.SUGGESTED_KM_VALUE,
    }
    return render(request, "campaign/home.html", context)


def _selected_numbers(request):
    raw_numbers = request.POST.getlist("km_numbers") or request.GET.getlist("km")
    numbers = []
    for raw_number in raw_numbers:
        try:
            number = int(raw_number)
        except (TypeError, ValueError):
            continue
        if 1 <= number <= 160 and number not in numbers:
            numbers.append(number)
    return numbers


@transaction.atomic
def reserve_kilometers(request):
    numbers = _selected_numbers(request)
    if not numbers:
        messages.warning(request, "Escolha ao menos um KM livre da estrada.")
        return redirect("campaign:home")

    selected = list(Kilometer.objects.select_for_update().filter(number__in=numbers).order_by("number"))
    unavailable = [km.number for km in selected if km.status != Kilometer.Status.AVAILABLE]
    if len(selected) != len(numbers) or unavailable:
        messages.warning(request, "Algum KM escolhido já tomou rumo. Veja os livres e tente de novo.")
        return redirect("campaign:home")

    if request.method == "POST":
        form = KilometerSponsorForm(
            request.POST,
            request.FILES,
            minimum_amount=settings.SUGGESTED_KM_VALUE * len(selected),
        )
        if form.is_valid():
            data = form.cleaned_data
            amount_per_km = data["amount"] / len(selected)
            for kilometer in selected:
                kilometer.sponsor_name = data["sponsor_name"]
                kilometer.amount = amount_per_km
                kilometer.donor_message = data["donor_message"]
                kilometer.status = Kilometer.Status.PENDING
                kilometer.save()
            km_query = ",".join(str(km.number) for km in selected)
            return redirect(f"{reverse('campaign:thank_you')}?kms={km_query}")
    else:
        form = KilometerSponsorForm(
            initial={"amount": settings.SUGGESTED_KM_VALUE * len(selected)},
            minimum_amount=settings.SUGGESTED_KM_VALUE * len(selected),
        )

    return render(
        request,
        "campaign/reserve.html",
        {
            "form": form,
            "selected": selected,
            "pix_key": settings.PIX_KEY,
            "suggested_km_value": settings.SUGGESTED_KM_VALUE,
            "total_suggested": settings.SUGGESTED_KM_VALUE * len(selected),
        },
    )


@transaction.atomic
def sponsor_kilometer(request, number):
    kilometer = get_object_or_404(Kilometer.objects.select_for_update(), number=number)
    if kilometer.status != Kilometer.Status.AVAILABLE:
        messages.warning(request, f"O KM {number} já tomou rumo: reservado ou confirmado.")
        return redirect("campaign:home")

    if request.method == "POST":
        form = KilometerSponsorForm(
            request.POST,
            request.FILES,
            instance=kilometer,
            minimum_amount=settings.SUGGESTED_KM_VALUE,
        )
        if form.is_valid():
            sponsorship = form.save(commit=False)
            sponsorship.status = Kilometer.Status.PENDING
            sponsorship.save()
            return redirect(f"{reverse('campaign:thank_you')}?kms={number}")
    else:
        form = KilometerSponsorForm(
            instance=kilometer,
            initial={"amount": settings.SUGGESTED_KM_VALUE},
            minimum_amount=settings.SUGGESTED_KM_VALUE,
        )

    return render(
        request,
        "campaign/sponsor.html",
        {
            "form": form,
            "kilometer": kilometer,
            "pix_key": settings.PIX_KEY,
            "suggested_km_value": settings.SUGGESTED_KM_VALUE,
        },
    )


def thank_you(request):
    km_text = request.GET.get("kms", "")
    numbers = [int(number) for number in km_text.split(",") if number.isdigit()]
    kilometers = Kilometer.objects.filter(number__in=numbers).order_by("number")
    km_label = ", ".join(f"KM {number}" for number in numbers)
    message = quote(f"Oi, Mateus! Acabei de fazer o PIX da campanha Caminhos de Rosa para: {km_label}. Segue o comprovante.")
    whatsapp_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={message}"
    total = sum((km.amount or 0) for km in kilometers)
    return render(
        request,
        "campaign/thank_you.html",
        {
            "kilometers": kilometers,
            "pix_key": settings.PIX_KEY,
            "pix_copy_paste": settings.PIX_COPY_PASTE,
            "whatsapp_url": whatsapp_url,
            "total": total,
        },
    )


def kilometer_detail(request, number):
    kilometer = get_object_or_404(Kilometer, number=number)
    if kilometer.status == Kilometer.Status.AVAILABLE:
        messages.warning(request, f"O KM {number} ainda está livre.")
        return redirect("campaign:home")

    return render(request, "campaign/kilometer_detail.html", {"kilometer": kilometer})


def panel_login(request):
    if request.session.get("panel_authenticated"):
        return redirect("campaign:panel")

    if request.method == "POST":
        password = request.POST.get("password", "")
        if password == settings.ADMIN_PASSWORD:
            request.session["panel_authenticated"] = True
            return redirect("campaign:panel")
        messages.warning(request, "Senha não abriu a porteira.")

    return render(request, "campaign/panel_login.html")


def panel_logout(request):
    request.session.pop("panel_authenticated", None)
    return redirect("campaign:home")


@transaction.atomic
def panel(request):
    if not request.session.get("panel_authenticated"):
        return redirect("campaign:panel_login")

    if request.method == "POST":
        action = request.POST.get("action")
        ids = request.POST.getlist("kilometers")
        kilometers = Kilometer.objects.select_for_update().filter(id__in=ids)

        if not ids:
            messages.warning(request, "Marque ao menos um KM na caderneta.")
        elif action == "confirm":
            kilometers.update(status=Kilometer.Status.CONFIRMED, confirmed_at=timezone.now())
            messages.success(request, "KM dado como certo.")
        elif action == "release":
            kilometers.update(
                status=Kilometer.Status.AVAILABLE,
                sponsor_name="",
                donor_email="",
                donor_phone="",
                amount=None,
                pix_receipt="",
                donor_message="",
                confirmed_at=None,
            )
            messages.success(request, "KM solto de novo.")
        return redirect("campaign:panel")

    pending = Kilometer.objects.filter(status=Kilometer.Status.PENDING)
    confirmed = Kilometer.objects.filter(status=Kilometer.Status.CONFIRMED)
    pending_total = pending.aggregate(total=Sum("amount"))["total"] or 0
    confirmed_total = confirmed.aggregate(total=Sum("amount"))["total"] or 0
    reserved_total = pending_total + confirmed_total
    return render(
        request,
        "campaign/panel.html",
        {
            "pending": pending,
            "confirmed": confirmed,
            "pending_count": pending.count(),
            "confirmed_count": confirmed.count(),
            "pending_total": pending_total,
            "confirmed_total": confirmed_total,
            "reserved_total": reserved_total,
            "reserved_food_units": int(reserved_total // settings.FOOD_UNIT_VALUE),
            "food_unit_value": settings.FOOD_UNIT_VALUE,
        },
    )
