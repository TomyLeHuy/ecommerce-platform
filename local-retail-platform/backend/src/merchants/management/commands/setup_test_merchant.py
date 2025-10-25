"""Management command to create a test merchant account with all required data."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from merchants.models import MerchantProfile, Subscription, Shop


class Command(BaseCommand):
    help = "Creates a test merchant account with profile, subscription, and shop"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="testmerchant",
            help="Username for the merchant account (default: testmerchant)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="Test1234!",
            help="Password for the merchant account (default: Test1234!)",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="merchant@test.com",
            help="Email for the merchant account (default: merchant@test.com)",
        )
        parser.add_argument(
            "--company",
            type=str,
            default="Test Company GmbH",
            help="Company name (default: Test Company GmbH)",
        )
        parser.add_argument(
            "--shop-name",
            type=str,
            default="Test Shop",
            help="Shop name (default: Test Shop)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]
        company_name = options["company"]
        shop_name = options["shop_name"]

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"User '{username}' already exists. Deleting...")
            )
            User.objects.filter(username=username).delete()

        # Create user
        self.stdout.write(f"Creating user '{username}'...")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name="Test",
            last_name="Merchant",
        )
        self.stdout.write(self.style.SUCCESS(f"✓ User created: {username}"))

        # Create merchant profile
        self.stdout.write(f"Creating merchant profile for '{company_name}'...")
        merchant_profile = MerchantProfile.objects.create(
            user=user,
            company_name=company_name,
            tax_id=f"DE{username.upper()}123456789",
            phone="+49 123 456789",
            street_address="Teststraße 123",
            city="Berlin",
            postal_code="10115",
            country="DE",
            latitude=52.5200,
            longitude=13.4050,
            is_verified=True,  # Auto-verify for testing
        )
        self.stdout.write(
            self.style.SUCCESS(f"✓ Merchant profile created: {company_name}")
        )

        # Create subscription
        self.stdout.write("Creating subscription...")
        subscription = Subscription.objects.create(
            merchant=merchant_profile,
            tier="free",
            status="active",
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Subscription created: {subscription.get_tier_display()}"
            )
        )

        # Create shop
        shop_slug = slugify(shop_name)
        # Make slug unique if it already exists
        if Shop.objects.filter(slug=shop_slug).exists():
            shop_slug = f"{shop_slug}-{user.id}"

        self.stdout.write(f"Creating shop '{shop_name}'...")
        shop = Shop.objects.create(
            merchant=merchant_profile,
            name=shop_name,
            slug=shop_slug,
            description=f"This is a test shop for {company_name}. We sell quality products!",
            email=email,
            phone="+49 123 456789",
            delivery_radius_km=150,
            is_active=True,
            accepts_online_orders=True,
            accepts_in_store_pickup=True,
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Shop created: {shop_name}"))

        # Print summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("✓ Test merchant setup complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write(f"Username:     {username}")
        self.stdout.write(f"Password:     {password}")
        self.stdout.write(f"Email:        {email}")
        self.stdout.write(f"Company:      {company_name}")
        self.stdout.write(f"Shop:         {shop_name} (slug: {shop_slug})")
        self.stdout.write(f"Tax ID:       {merchant_profile.tax_id}")
        self.stdout.write(f"Verified:     Yes")
        self.stdout.write(f"Subscription: {subscription.get_tier_display()}")
        self.stdout.write("")
        self.stdout.write("You can now log in at: /merchant/login")
        self.stdout.write("")
