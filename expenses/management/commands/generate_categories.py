import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from expenses.models import User, Transaction, Category

class Command(BaseCommand):
    help = "Generates transactions for testing"

    def handle(self, *args, **options):
        fake = Faker()

        # Create categories
        categories = ['Bills', 'Food', 'Clothes', 'Medical', 'Housing', 'Salary', 'Social', 'Transport', 'Vacation', 'Other']

        for category in categories:
            Category.objects.get_or_create(name=category)

        # Get the last logged-in user
        sessions = Session.objects.filter(expire_date__gte=now())
        user_id = None
        for session in sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            if user_id:
                break

        if not user_id:
            self.stdout.write(self.style.ERROR("No logged-in user found. Please ensure a user is logged in."))
            return

        user = User.objects.get(id=user_id)

        # # Create transactions
        # categories = Category.objects.all()
        # types = [x[0] for x in Transaction.TRANSACTION_TYPE_CHOICES]

        # for i in range(20):
        #     Transaction.objects.create(
        #         category=random.choice(categories),
        #         user=user,
        #         amount=random.uniform(1, 2500),
        #         date=fake.date_between(start_date='-1y', end_date='today'),
        #         type=random.choice(types),
        #         description=fake.sentence(nb_words=10)
        #     )
        # self.stdout.write(self.style.SUCCESS(f"Transactions successfully generated for user: {user.username}"))