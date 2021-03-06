import datetime
from django.urls import reverse_lazy
from django.views import generic  # for bookslist view
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin # to be used to control users who can access the list of all borrowed books
from django.contrib.auth.decorators import login_required, permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

# form imports
from catalog.forms import RenewBookForm

# for updating views
from django.views.generic.edit import CreateView, UpdateView, DeleteView


# Create your views here.

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'available')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # Available books (status = 'on loan')
    num_instances_loaned = BookInstance.objects.filter(status__exact='o').count()
    # Available books (status = 'reserved')
    num_instances_reserved = BookInstance.objects.filter(status__exact='r').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # books with term hits
    num_books_humans = Book.objects.filter(title__contains='Humans').count()

    # politics genre
    num_books_genre_politics = Book.objects.filter(genre__exact='1').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_books_humans': num_books_humans,
        'num_books_genre_politics': num_books_genre_politics,
        'num_instances_available': num_instances_available,
        'num_instances_loaned': num_instances_loaned,
        'num_instances_reserved': num_instances_reserved,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author


# custom view for genres
class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 10


# custom detailedview for genres
# Note yet implemented correctly
class GenreDetailView(LoginRequiredMixin, generic.DetailView):
    model = Genre


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user. library user permissions required."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to all users."""
    # check permissions by printing {{perms.applabel}} to the html page
    permission_required = 'catalog.change_bookinstance'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


# for renewing book loans
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# views for edits author related stuff
class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.change_author'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_author'
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_author'
    model = Author
    success_url = reverse_lazy('authors')


# views for editing book related stuff
class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.change_book'
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_book'
    model = Book
    fields = ['title', 'summary', 'genre', 'language'] # Not recommended (potential security issue if more fields added)


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_book'
    model = Book
    success_url = reverse_lazy('books')


