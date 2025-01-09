from import_export import resources, fields
from expenses.models import Transaction, Category
from import_export.widgets import ForeignKeyWidget

class TransactionResource(resources.ModelResource):
    duplicate_count = 0  # Initialize duplicate count

    class Meta:
        model = Transaction
        fields = ('date', 'amount', 'type', 'description', 'category')  # Include only necessary fields
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('date', 'amount', 'type', 'description', 'category')  # Use these fields to identify duplicates

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # Store the user to associate with transactions
        self.duplicate_count = 0

    def get_instance(self, instance_loader, row):
        """
        Overrides the default instance retrieval logic to include user filtering.
        Ensures that the user-specific transactions are checked for duplicates.
        """
        return self._meta.model.objects.filter(
            user=self.user,
            date=row.get('date'),
            amount=row.get('amount'),
            type=row.get('type'),
            description=row.get('description'),
            category__name=row.get('category'),
        ).first()

    
    def before_import_row(self, row, **kwargs):
        """
        Check for duplicates before importing a row.
        """
        row['user'] = self.user  # Set the user for the transaction
        if self.get_instance(None, row):
            self.duplicate_count += 1
            return False  # Skip importing this row
        return True
    def dehydrate_category(self, transaction):
        # Export the name of the category instead of its ID
        return transaction.category.name if transaction.category else 'N/A'