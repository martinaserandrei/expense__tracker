from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Transaction,Category
from .forms import TransactionForm,CustomUserCreationForm, FeedbackForm
from django.http import JsonResponse
from django_filters.views import FilterView
from expenses.filters import TransactionFilter
from django.contrib import messages
from django.http import HttpResponse
import expenses.charting as ch 
from django_htmx.http import retarget
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
import time
from expenses.resources import TransactionResource
from tablib import Dataset
from django.views.decorators.http import require_http_methods
from .utils import clean_file
import os
import webbrowser
import pandas


def welcome(request):
    return render(request, 'expenses/welcome.html')

def signup(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if request.headers.get('HX-Request'):  # HTMX request
            return JsonResponse({'message': 'Account created successfully!'})
        return redirect('login')  # Redirect to login page

    if request.htmx:  # HTMX request
        return render(request, 'expenses/partials/signup_form.html', {'form': form})
    
    return render(request, 'expenses/signup.html', {'form': form})


@login_required
def home(request):
    # Calculate total income, expenses, and net income
    transactions = Transaction.objects.filter(user=request.user)
    total_income = transactions.get_total_income()
    total_expenses = transactions.get_total_expenses()
    net_income = total_income - total_expenses
    transaction_filter = TransactionFilter(request.GET, queryset=Transaction.objects.filter(user=request.user).order_by('-date'))
    paginator=Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    transaction_page = paginator.page(1)
    # Pass the calculated values to the template
    context = {
        'latest_transactions':transaction_page,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
    }
    return render(request, "expenses/home.html", context)

@login_required
def new_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            if request.htmx:
                context = {'transaction': transaction}
                response = render(request, 'expenses/partials/transaction_add_success.html', context)
                return retarget(response, '#transaction-block')

            return redirect('transactions')

        if request.htmx:
            response = render(request, 'expenses/partials/new_transaction_p.html', {'form': form})
            return retarget(response, '#transaction-block')

        return render(request, 'expenses/new_transaction.html', {'form': form})

    form = TransactionForm()
    if request.htmx:
        response = render(request, 'expenses/partials/new_transaction_p.html', {'form': form})
        return retarget(response, '#transaction-block')
    return render(request, 'expenses/new_transaction.html', {'form': form})


@login_required
def transactions_list(request):
    transaction_filter = TransactionFilter(request.GET, queryset=Transaction.objects.filter(user=request.user).order_by('-date'))
    transactions = transaction_filter.qs
    paginator=Paginator(transactions,settings.PAGE_SIZE)
    transaction_page = paginator.page(1)

    # Use methods from TransactionQuerySet
    total_income = transactions.get_total_income()
    total_expenses = transactions.get_total_expenses()

    context = {
        'transactions': transaction_page,
        'filter': transaction_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': total_income-total_expenses,
    }
    if request.htmx:  # HTMX request
        return render(request, 'expenses/partials/transaction_filtered.html', context)
    return render(request, 'expenses/transaction_list.html', context)

@login_required
def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    is_htmx = request.htmx  # Determine if the request is HTMX-based

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context = {'transaction': transaction}
            return render(request, 'expenses/partials/transaction_success.html', context)

        # Render the appropriate template based on request type
        template = 'expenses/partials/update_transaction.html' if is_htmx else 'expenses/full_page_template.html'
        context = {'form': form, 'transaction': transaction, 'content': 'expenses/partials/update_transaction.html'}
        return render(request, template, context)

    # Handle GET requests
    form = TransactionForm(instance=transaction)
    template = 'expenses/partials/update_transaction.html' if is_htmx else 'expenses/full_page_template.html'
    context = {'form': form, 'transaction': transaction, 'content': 'expenses/partials/update_transaction.html'}
    return render(request, template, context)


@login_required
def transaction_add_success(request):
    context = {
        'message': "Transaction has been successfully added to the list!"
    }
    return render(request, 'expenses/partials/transaction_add_success.html', context)
@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user= request.user)
    transaction.delete()
    context= {
        'message': f"Transaction of {transaction.amount} on {transaction.date} was deleted."
    }
    return render(request, 'expenses/partials/transaction_delete_success.html',context)

@login_required
def get_transactions(request):
    time.sleep(2)
    page = request.GET.get('page',1)
    transaction_filter = TransactionFilter(request.GET, queryset=Transaction.objects.filter(user=request.user).order_by('-date'))
    transactions = transaction_filter.qs
    paginator=Paginator(transactions,settings.PAGE_SIZE)
    context={
        'transactions': paginator.page(page)
    }
    return render( request, 'expenses/partials/transaction_container.html#transaction_list',context)
@login_required
def feedback_view(request):
    if request.method == 'POST':
        # Handle feedback submission
        bio = request.POST.get('bio')
        # Save the feedback (replace with your actual save logic)
        if bio:
            # Simulate saving feedback
            messages.success(request, "Thank you for your feedback!")
            if request.headers.get('HX-Request'):
                # Return a success message for HTMX
                return HttpResponse("<p class='text-success'>Thank you for your feedback!</p>")
    
    if request.headers.get('HX-Request'):
        # If the request is an HTMX request, return only the form partial
        return render(request, 'expenses/_feedback_form.html')
    
    # Otherwise, render the full feedback page
    return render(request, 'expenses/feedback.html')

@login_required
def transaction_charts(request):
    # Debugging: Ensure the user is passed correctly
    print("User:", request.user)

    # Apply the filter to user's transactions
    transaction_filter = TransactionFilter(
        request.GET, 
        queryset=Transaction.objects.filter(user=request.user))

    # Generate the chart using the filtered transactions
    income_expense_bar = ch.plot_expenses(transaction_filter.qs)
    category_income_pie = ch.plot_category_pie_chart(
        transaction_filter.qs.filter(type='income'))
    category_expense_pie = ch.plot_category_pie_chart(
        transaction_filter.qs.filter(type='expense'))
    plot_line_chart = ch.plot_line_chart(transaction_filter.qs)

    context = {
        'filter': transaction_filter,
        'income_expense_bar': income_expense_bar.to_html(),
        'category_income_pie': category_income_pie.to_html(),
        'category_expense_pie': category_expense_pie.to_html(),
        'plot_line_chart': plot_line_chart.to_html(),
    }
    if request.htmx:
        return render(request, 'expenses/partials/charts_filtered.html', context)
    return render(request, 'expenses/charts.html', context)

@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect':request.get_full_path()})
    transaction_filter = TransactionFilter(request.GET, queryset=Transaction.objects.filter(user=request.user).order_by('-date'))
    data= TransactionResource().export(transaction_filter.qs)
    response= HttpResponse(data.csv)
    #pip install "tablib[all]" to install also pandas file yaml files and all files
    response['Content-Disposition']='attachment;filename=transactions.csv'
    return response

@login_required
def import_transactions(request):
    if request.method == 'POST':
        resource = TransactionResource(user=request.user)
        file = request.FILES.get('file')
        dataset = Dataset()
        dataset.load(file.read().decode(), format='csv')

        duplicate_count = 0
        imported_count = 0

        for row in dataset.dict:
            # Check if the transaction already exists
            existing_transaction = Transaction.objects.filter(
                user=request.user,
                date=row.get('date'),
                description=row.get('description'),
                amount=row.get('amount'),
                type=row.get('type'),
                category__name=row.get('category')
            ).exists()

            if existing_transaction:
                duplicate_count += 1
                continue  # Skip duplicates

            # Create a new transaction
            Transaction.objects.create(
                user=request.user,
                date=row.get('date'),
                description=row.get('description'),
                amount=row.get('amount'),
                type=row.get('type'),
                category=Category.objects.get(name=row.get('category'))
            )
            imported_count += 1

        context = {
            'message': f'{imported_count} transactions were uploaded successfully and {duplicate_count} duplicates were found and skipped.',
            'duplicate_count': duplicate_count,
        }

        if request.headers.get('HX-Request'):
            return render(request, 'expenses/partials/transaction_import_success.html', context)

        return redirect('transactions')

    if request.headers.get('HX-Request'):
        return render(request, 'expenses/partials/import_transaction.html')
    else:
        return render(request, 'expenses/import_main.html')


@login_required
def choose_banking_service(request):
    if request.method == 'POST':
        banking_service = request.POST.get('banking_service')

        # Open the banking service in a new tab
        if banking_service == 'intesa':
            webbrowser.open_new_tab('https://www.intesasanpaolo.com/it/persone-e-famiglie/login-page.html')
        # Redirect to the file preparation page
        return redirect('prepare_file_page')

    # Render the appropriate template
    if request.htmx:
        return render(request, 'expenses/partials/choose_banking_service.html')
    else:
        return render(request, 'expenses/full_page_template.html', {
            'content': 'expenses/partials/choose_banking_service.html',
        })


@login_required
def prepare_file_page(request):
    if request.method == 'POST' and 'transaction_file' in request.FILES:
        transaction_file = request.FILES['transaction_file']

        # Save the uploaded file temporarily
        temp_file_path = os.path.join(settings.TEMP_DIR, transaction_file.name)

        with open(temp_file_path, 'wb') as f:
            for chunk in transaction_file.chunks():
                f.write(chunk)

        try:
            cleaned_temp_file_path = clean_file.clean_excel(temp_file_path)
        except Exception as e:
            return render(request, 'expenses/partials/prepare_file.html', {
                'error': f"Error cleaning file: {e}"
            })

        # Step 2: Transform the cleaned file into the correct format
        try:
            cleaned_file_path = clean_file.transform_file_to_prova(
                cleaned_temp_file_path,
                cleaned_temp_file_path.replace('.csv', '_cleaned.csv')
            )
        except Exception as e:
            return render(request, 'expenses/partials/prepare_file.html', {
                'error': f"Error transforming file: {e}"
            })

        # Load cleaned transactions into a DataFrame for category assignment
        print(f"Cleaned file path: {cleaned_file_path}")

        cleaned_data = pandas.read_csv(cleaned_file_path)
        request.session['cleaned_file_path'] = cleaned_file_path  # Store for later use

        # Redirect to finalize transactions
        return redirect('finalize_transactions')

    # Check if the request is an HTMX request
    if request.htmx:
        return render(request, 'expenses/partials/prepare_file.html')
    else:
        # Render the full page template if it's not an HTMX request
        return render(request, 'expenses/full_page_template.html', {
            'content': 'expenses/partials/prepare_file.html'
        })


@login_required
def finalize_transactions(request):
    # Check if the cleaned file path exists
    cleaned_file_path = request.session.get('cleaned_file_path')

    if not cleaned_file_path or not os.path.exists(cleaned_file_path):
        return redirect('prepare_file_page')

    # Load the cleaned data
    cleaned_data = pandas.read_csv(cleaned_file_path)

    # Fetch all available categories
    categories = Category.objects.all()

    # Determine if the user has completed the process
    step = request.session.get('finalize_transactions_step', 'assign_categories')

    if request.method == 'POST':
        category_assignments = request.POST.getlist('categories[]')

        # Assign categories to transactions
        for index, category_id in enumerate(category_assignments):
            cleaned_data.loc[index, 'category'] = category_id

        # Save transactions to the database
        for _, row in cleaned_data.iterrows():
            Transaction.objects.create(
                user=request.user,
                date=row['date'],
                description=row['description'],
                amount=row['amount'],
                type=row['type'],
                category_id=row['category']
            )

        # Update the session to indicate the success step
        request.session['finalize_transactions_step'] = 'success'



        # Render the correct template based on the step
        if step == 'success':
            if request.htmx:
                return render(request, 'expenses/partials/transaction_import_success.html', {
                    'message': 'Transactions successfully saved and imported!'
                })
            else:
                return render(request, 'expenses/full_page_template.html', {
                    'content': 'expenses/partials/transaction_import_success.html',
                    'message': 'Transactions successfully saved and imported!',
                })

    if request.htmx:
        return render(request, 'expenses/partials/assign_categories.html', {
            'transactions': cleaned_data.to_dict('records'),
            'categories': categories,
        })
    else:
        return render(request, 'expenses/full_page_template.html', {
            'content': 'expenses/partials/assign_categories.html',
            'transactions': cleaned_data.to_dict('records'),
            'categories': categories,
        })


@login_required
def import_choice(request):
    if request.method == 'POST':
        choice = request.POST.get('source')
        if choice == 'file':
            # Redirect to the file import page
            return redirect('import')
        elif choice == 'banking':
            # Redirect to the banking service choice page
            return redirect('choose_banking_service')

    # Check if the request is an HTMX request
    if request.htmx:
        return render(request, 'expenses/partials/import_choice.html')
    else:
        # Render the full page template with the partial content
        return render(request, 'expenses/full_page_template.html', {
            'content': 'expenses/partials/import_choice.html'
        })
