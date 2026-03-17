import os
import random
from decimal import Decimal

import requests
from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from hotels.models import Hotel, RoomType, HotelImage, RoomTypeImage, HotelReview


fake = Faker()


CITIES = [
    "Kyiv",
    "Lviv",
    "Odesa",
    "Kharkiv",
    "Dnipro",
    "Zaporizhzhia",
    "Ivano-Frankivsk",
    "Uzhhorod",
    "Chernivtsi",
    "Ternopil",
    "Vinnytsia",
    "Poltava",
    "Cherkasy",
    "Zhytomyr",
    "Rivne",
    "Lutsk",
    "Khmelnytskyi",
    "Sumy",
    "Kropyvnytskyi",
    "Mykolaiv",
]

STREET_NAMES = [
    "Shevchenko",
    "Hrushevskoho",
    "Franka",
    "Lesi Ukrainky",
    "Khmelnytskoho",
    "Mazepy",
    "Bandery",
    "Soborna",
    "Tsentralna",
    "Myru",
    "Svobody",
    "Heroiv Ukrainy",
    "Nezalezhnosti",
    "Sadova",
    "Zelena",
]

ROOM_TYPE_CONFIG = [
    {
        "name": "Single Room",
        "capacity": 1,
        "price_min": 55,
        "price_max": 95,
        "qty_min": 4,
        "qty_max": 8,
        "queries": ["single bedroom", "hotel room", "bedroom interior"],
    },
    {
        "name": "Double Room",
        "capacity": 2,
        "price_min": 85,
        "price_max": 140,
        "qty_min": 2,
        "qty_max": 6,
        "queries": ["double bedroom", "hotel room", "bedroom interior"],
    },
    {
        "name": "King Size Room",
        "capacity": 2,
        "price_min": 140,
        "price_max": 220,
        "qty_min": 1,
        "qty_max": 3,
        "queries": ["king bed hotel room", "hotel suite", "bedroom interior"],
    },
    {
        "name": "Luxury Room",
        "capacity": 4,
        "price_min": 250,
        "price_max": 420,
        "qty_min": 1,
        "qty_max": 2,
        "queries": ["luxury suite", "hotel suite", "luxury hotel room"],
    },
]

REVIEW_COMMENTS = [
    "Wonderful stay, very clean rooms and friendly staff.",
    "Great location and delicious breakfast.",
    "Comfortable beds and nice atmosphere.",
    "The room was clean and spacious, we enjoyed our stay.",
    "Very good service and smooth check-in.",
    "Excellent hotel for a weekend trip.",
    "Beautiful interior and helpful reception staff.",
    "Nice hotel, good value for money.",
    "Everything was good, especially the location.",
    "Cozy room and pleasant service.",
    "Amazing experience, would definitely come back.",
    "The hotel looked even better than in the photos.",
]


def random_hotel_name() -> str:
    prefixes = [
        "Grand",
        "Royal",
        "Golden",
        "Emerald",
        "Imperial",
        "Central",
        "Heritage",
        "Sunrise",
        "Blue",
        "Crystal",
        "Sky",
        "Riverside",
        "Premium",
        "Elite",
        "Palace",
    ]
    suffixes = [
        "Hotel",
        "Palace",
        "Residence",
        "Suites",
        "Resort",
        "Boutique Hotel",
        "Inn",
        "Grand Hotel",
    ]
    return f"{random.choice(prefixes)} {fake.company().split()[0]} {random.choice(suffixes)}"


def random_ukrainian_address(city: str) -> str:
    street = random.choice(STREET_NAMES)
    building = random.randint(1, 120)
    return f"vul. {street}, {building}, {city}"


class UnsplashClient:
    base_url = "https://api.unsplash.com"

    def __init__(self, access_key: str):
        if not access_key:
            raise ValueError("Unsplash access key is required")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept-Version": "v1",
                "Authorization": f"Client-ID {access_key}",
            }
        )

    def search_photo_urls(self, query: str, per_page: int = 20, pages: int = 1) -> list[str]:
        urls = []
        seen = set()

        for page in range(1, pages + 1):
            response = self.session.get(
                f"{self.base_url}/search/photos",
                params={
                    "query": query,
                    "page": page,
                    "per_page": per_page,
                    "orientation": "landscape",
                    "content_filter": "high",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("results", []):
                url = item.get("urls", {}).get("regular")
                if url and url not in seen:
                    seen.add(url)
                    urls.append(url)

        return urls

    def search_with_fallbacks(self, queries: list[str], per_page: int = 20, pages: int = 1) -> list[str]:
        all_urls = []
        seen = set()

        for query in queries:
            urls = self.search_photo_urls(query=query, per_page=per_page, pages=pages)
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    all_urls.append(url)

            if all_urls:
                break

        return all_urls


class Command(BaseCommand):
    help = "Seed fake hotels, room types, images, and reviews"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="How many hotels to create. Default: 50",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing hotel-related data before seeding",
        )

    def handle(self, *args, **options):
        count = options["count"]
        reset = options["reset"]

        access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not access_key:
            raise CommandError(
                "UNSPLASH_ACCESS_KEY is not set.\n"
                "Example:\n"
                "export UNSPLASH_ACCESS_KEY='your_access_key_here'"
            )

        client = UnsplashClient(access_key)

        if reset:
            self.stdout.write(self.style.WARNING("Deleting old hotel data..."))
            HotelReview.objects.all().delete()
            RoomTypeImage.objects.all().delete()
            HotelImage.objects.all().delete()
            RoomType.objects.all().delete()
            Hotel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Old data deleted."))

        self.stdout.write(self.style.WARNING("Fetching hotel images from Unsplash..."))
        hotel_image_pool = client.search_with_fallbacks(
            queries=[
                "hotel building exterior",
                "hotel exterior",
                "hotel facade",
                "resort building",
            ],
            per_page=30,
            pages=2,
        )

        if len(hotel_image_pool) < count:
            raise CommandError(
                f"Only {len(hotel_image_pool)} hotel images found, but {count} hotels requested."
            )

        room_image_pools = {}

        for config in ROOM_TYPE_CONFIG:
            self.stdout.write(
                self.style.WARNING(f"Fetching room images for: {config['name']}...")
            )

            room_urls = client.search_with_fallbacks(
                queries=config["queries"],
                per_page=20,
                pages=1,
            )

            if not room_urls:
                raise CommandError(
                    f"No images found for room type '{config['name']}'. "
                    f"Tried queries: {config['queries']}"
                )

            room_image_pools[config["name"]] = room_urls

        self.stdout.write(self.style.WARNING(f"Creating {count} hotels..."))

        random.shuffle(hotel_image_pool)
        created_hotels = 0

        for i in range(count):
            city = random.choice(CITIES)

            hotel = Hotel.objects.create(
                name=random_hotel_name(),
                city=city,
                address=random_ukrainian_address(city),
                description=fake.paragraph(nb_sentences=5),
                stars=random.randint(3, 5),
            )

            main_hotel_image = hotel_image_pool[i]

            HotelImage.objects.create(
                hotel=hotel,
                image=main_hotel_image,
                alt_text=f"{hotel.name} exterior",
                is_main=True,
            )

            extra_candidates = [img for img in hotel_image_pool if img != main_hotel_image]
            for extra_img in random.sample(extra_candidates, k=min(2, len(extra_candidates))):
                HotelImage.objects.create(
                    hotel=hotel,
                    image=extra_img,
                    alt_text=f"{hotel.name} gallery image",
                    is_main=False,
                )

            for config in ROOM_TYPE_CONFIG:
                room_type = RoomType.objects.create(
                    hotel=hotel,
                    name=config["name"],
                    capacity=config["capacity"],
                    price=Decimal(str(random.randint(config["price_min"], config["price_max"]))),
                    total_quantity=random.randint(config["qty_min"], config["qty_max"]),
                    description=fake.paragraph(nb_sentences=3),
                )

                room_pool = room_image_pools[config["name"]]
                selected_room_images = random.sample(room_pool, k=min(2, len(room_pool)))

                for idx, room_img in enumerate(selected_room_images):
                    RoomTypeImage.objects.create(
                        room_type=room_type,
                        image=room_img,
                        alt_text=f"{room_type.name} at {hotel.name}",
                        is_main=(idx == 0),
                    )

            # Fake reviews
            reviews_count = random.randint(8, 40)

            for _ in range(reviews_count):
                # weighted ratings to look more realistic for hotels
                rating = random.choices(
                    population=[6, 7, 8, 9, 10],
                    weights=[5, 10, 30, 35, 20],
                    k=1,
                )[0]

                HotelReview.objects.create(
                    hotel=hotel,
                    author_name=fake.name(),
                    rating=rating,
                    comment=random.choice(REVIEW_COMMENTS),
                )

            created_hotels += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{created_hotels}/{count}] Created: {hotel.name} "
                    f"(rating: {hotel.rating}, reviews: {hotel.reviews.count()})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully."))