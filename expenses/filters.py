import django_filters
from django import forms

from expenses.models import Transaction,Category

class TransactionFilter(django_filters.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        choices=Transaction.TRANSACTION_TYPE_CHOICES,
        field_name='type',
        lookup_expr='iexact',
        label='Transaction Type',
        empty_label='Any',
    )
    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    min_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Minimum Amount',
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Maximum Amount',
    )

    start_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        label='Start Date',
        widget=forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'})
    )
    end_date = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        label='End Date',
        widget=forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'})
    )

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'min_amount', 'max_amount', 'start_date', 'end_date']