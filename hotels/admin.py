from django.contrib import admin
from .models import Hotel, RoomType, HotelImage, RoomTypeImage, HotelReview


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 0


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 0


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "stars", "slug")
    search_fields = ("name", "city", "address")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [HotelImageInline, RoomTypeInline]


class RoomTypeImageInline(admin.TabularInline):
    model = RoomTypeImage
    extra = 0


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "hotel", "capacity", "price", "total_quantity", "slug")
    search_fields = ("name", "hotel__name")
    list_filter = ("hotel",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [RoomTypeImageInline]
    autocomplete_fields = ("hotel",)


@admin.register(HotelReview)
class HotelReviewAdmin(admin.ModelAdmin):
    list_display = ("hotel", "author_name", "rating", "created_at")
    search_fields = ("hotel__name", "author_name", "comment")
    list_filter = ("rating", "created_at")