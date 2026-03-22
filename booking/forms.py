from django import forms
from .models import Booking
from .services import is_room_type_available


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
            ),
        }

    def __init__(self, *args, room_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_type = room_type
        if room_type is not None:
            self.instance.room_type = room_type

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        guests = cleaned_data.get("guests")

        if not check_in or not check_out or not self.room_type:
            return cleaned_data
        
        if guests and guests > self.room_type.capacity:
            self.add_error("guests", "Too many guests for this room type")

        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("Дата виїзду має бути пізніше за дату заїзду.")
            
        if not is_room_type_available(self.room_type, check_in, check_out):
            raise forms.ValidationError("No rooms available for the selected dates")

        return cleaned_data
