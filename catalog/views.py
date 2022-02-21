from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language

from django.views import generic #for bookslist view



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

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_books_humans': num_books_humans,
        'num_books_genre_politics': num_books_genre_politics,
        'num_instances_available': num_instances_available,
        'num_instances_loaned': num_instances_loaned,
        'num_instances_reserved': num_instances_reserved,
        'num_authors': num_authors,
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

