from booking.models import Booking

def get_overlapping_bookings(room_type, check_in, check_out):
    return Booking.objects.filter(
        room_type=room_type,
        status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        check_in__lt=check_out,
        check_out__gt=check_in,
    )


def get_available_quantity(room_type, check_in, check_out):
    overlapping_count = get_overlapping_bookings(room_type, check_in, check_out).count()
    return max(room_type.total_quantity - overlapping_count, 0)


def is_room_type_available(room_type, check_in, check_out):
    return get_available_quantity(room_type, check_in, check_out) > 0
