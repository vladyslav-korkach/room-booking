from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "full_name",
            "email",
            "phone",
            "check_in",
            "check_out",
            "guests",
        ]
        labels = {
            "full_name": "Повне ім'я",
            "email": "Електронна пошта",
            "phone": "Телефон",
            "check_in": "Дата заїзду",
            "check_out": "Дата виїзду",
            "guests": "Кількість гостей",
        }

        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Повне імʼя",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ел. пошта",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "type": "tel",
                    "placeholder": "+380...",
                    "class": "form-control",
                }
            ),
            "check_in": forms.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "Дата заїзду",
                    "class": "form-control",
                }
            ),
            "check_out": forms.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "Дата виїзду",
                    "class": "form-control",
                }
            ),
            "guests": forms.NumberInput(
                attrs={
                    "placeholder": "Всього гостей",
                    "class": "form-control",
                    "min": 1,
                }
            )

        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("Дата виїзду має бути пізніше за дату заїзду.")

        return cleaned_data
