from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language
from django.views import generic #for bookslist view
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


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
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
