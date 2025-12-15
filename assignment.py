import streamlit as st
import pandas as pd
import uuid
class Book:

    """Represents a book in the library."""
    def __init__(self, title, author, total_copies):
        self.book_id = str(uuid.uuid4())[:8] 
        self._title = title.title()
        self._author = author.title()
        self._total_copies = max(1, int(total_copies))
        self._available_copies = self._total_copies
    
    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def total_copies(self):
        return self._total_copies

    @property
    def available_copies(self):
        return self._available_copies

    def borrow_copy(self):
        if self._available_copies > 0:
            self._available_copies -= 1
            return True
        return False

    def return_copy(self):
        if self._available_copies < self._total_copies:
            self._available_copies += 1
            return True
        return False

    def to_dict(self):
        return {
            "Book ID": self.book_id,
            "Title": self._title,
            "Author": self._author,
            "Total Copies": self._total_copies,
            "Available Copies": self._available_copies
        }
class User:
    """Represents a user of the library system."""
    def __init__(self, name):
        self.user_id = str(uuid.uuid4())[:6]
        self._name = name.title()
        self.borrowed_books = {}  

    @property
    def name(self):
        return self._name

    def to_dict(self):
        return {
            "User ID": self.user_id,
            "Name": self._name,
            "Borrowed Count": len(self.borrowed_books)
        }
    
class Library:
    """Manages all book records, users, and operations."""
    def __init__(self):
        self.books = {}
        self.users = {}
        self._initialize_data()

    def _initialize_data(self):
        initial_books = [
            ("karachi chal ", "Maaz Amir", 5),
            ("How to survive in Karachi ", "Maaz Amir ", 3),
            ("pet story", "Maaz Amir", 4),
            ("jungle book", "Maaz Amir", 2),
        ]
        for title, author, copies in initial_books:
            book = Book(title, author, copies)
            self.books[book.book_id] = book

        initial_users = ["muhammad", "Maaz"]
        for name in initial_users:
            user = User(name)
            self.users[user.user_id] = user

    def add_book(self, title, author, total_copies):
        book = Book(title, author, total_copies)
        self.books[book.book_id] = book
        return book

    def add_user(self, name):
        user = User(name)
        self.users[user.user_id] = user
        return user

    def search_book(self, query, search_by='title'):
        query = query.lower()
        results = []
        for book in self.books.values():
            if search_by == 'title' and query in book.title.lower():
                results.append(book)
            elif search_by == 'author' and query in book.author.lower():
                results.append(book)
        return results

    def get_book_by_id(self, book_id):
        return self.books.get(book_id)

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def borrow_book(self, book_id, user_id):
        book = self.get_book_by_id(book_id)
        user = self.get_user_by_id(user_id)

        if not book: return "Error: Book not found."
        if not user: return "Error: User not found."
        if book_id in user.borrowed_books:
            return f"Error: User {user.name} has already borrowed '{book.title}'."
        if book.borrow_copy():
            user.borrowed_books[book_id] = book.title
            return f"Success: '{book.title}' borrowed by {user.name}."
        else:
            return f"Error: '{book.title}' has no available copies."

    def return_book(self, book_id, user_id):
        book = self.get_book_by_id(book_id)
        user = self.get_user_by_id(user_id)

        if not book: return "Error: Book not found."
        if not user: return "Error: User not found."
        if book_id not in user.borrowed_books:
            return f"Error: '{book.title}' was not borrowed by {user.name}."
        
        if book.return_copy():
            del user.borrowed_books[book_id]
            return f"Success: '{book.title}' returned by {user.name}."
        else:
            return "Error: Could not process book return."
    
    def get_all_books_data(self):
        return [book.to_dict() for book in self.books.values()]

    def get_all_users_data(self):
        return [user.to_dict() for user in self.users.values()]
    
    def get_borrowed_records(self):
        records = []
        for user_id, user in self.users.items():
            for book_id, book_title in user.borrowed_books.items():
                records.append({
                    "User Name": user.name,
                    "User ID": user_id,
                    "Book Title": book_title,
                    "Book ID": book_id
                })
        return records

if 'library' not in st.session_state:
    st.session_state.library = Library()

library = st.session_state.library

st.set_page_config(layout="wide", page_title="Digital Library System")
st.title("📚 Digital Library Management System")
st.markdown("---")

menu = st.sidebar.selectbox("Navigation Menu", [
    "View All Books",
    "Search Book",
    "Add New Book",
    "Borrow/Return Book",
    "View Users & Records"
])

if menu == "View All Books":
    st.header("📖 All Library Books")
    books_data = library.get_all_books_data()
    
    if books_data:
        df = pd.DataFrame(books_data)
        st.dataframe(df.set_index('Book ID'), use_container_width=True)

        st.subheader("Check Book Availability")
        book_titles = [book['Title'] for book in books_data]
        selected_title = st.selectbox("Select a book to check availability:", book_titles)
        
        if selected_title:
            book_found = next((book for book in library.books.values() if book.title == selected_title), None)
            if book_found:
                availability_status = f"**{book_found.available_copies}** out of **{book_found.total_copies}** copies available."
                st.info(availability_status)
    else:
        st.warning("No books in the library.")

elif menu == "Search Book":
    st.header("🔍 Search for Books")
    search_by = st.radio("Search By:", ("Title", "Author"), horizontal=True)
    search_query = st.text_input(f"Enter {search_by} to search:")

    if search_query:
        results = library.search_book(search_query, search_by.lower())
        if results:
            st.success(f"Found {len(results)} book(s) matching your query.")
            results_data = [book.to_dict() for book in results]
            df = pd.DataFrame(results_data)
            st.dataframe(df.set_index('Book ID'), use_container_width=True)
        else:
            st.warning(f"No books found with the {search_by} containing '{search_query}'.")

elif menu == "Add New Book":
    st.header("➕ Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title", key="new_title")
        author = st.text_input("Author", key="new_author")
        total_copies = st.number_input("Total Copies", min_value=1, value=1, step=1, key="new_copies")
        submitted = st.form_submit_button("Add Book to Library")
        
        if submitted:
            if title and author and total_copies:
                new_book = library.add_book(title, author, total_copies)
                st.success(f"Book added! '{new_book.title}' by {new_book.author} (ID: {new_book.book_id})")
                st.balloons()
            else:
                st.error("Please fill in all the details.")

elif menu == "Borrow/Return Book":
    st.header("🤝 Book Transactions")
    col1, col2 = st.columns(2)

    with col1.expander("Borrow a Book"):
        st.subheader("Borrow Book")
        book_options = {book.title: book.book_id for book in library.books.values() if book.available_copies > 0}
        user_options = {user.name: user.user_id for user in library.users.values()}

        if not book_options or not user_options:
            st.warning("Cannot proceed. Ensure books are available and users exist.")
        else:
            with st.form("borrow_form"):
                selected_title = st.selectbox("Select Book Title:", list(book_options.keys()))
                selected_user_name = st.selectbox("Select User Name:", list(user_options.keys()))
                borrow_submitted = st.form_submit_button("Confirm Borrow")

                if borrow_submitted:
                    book_id = book_options[selected_title]
                    user_id = user_options[selected_user_name]
                    result = library.borrow_book(book_id, user_id)
                    if "Success" in result:
                        st.success(result)
                    else:
                        st.error(result)

    with col2.expander("Return a Book"):
        st.subheader("Return Book")
        borrowed_records = library.get_borrowed_records()
        
        if not borrowed_records:
            st.warning("No books are currently borrowed.")
        else:
            return_options = {}
            for record in borrowed_records:
                key = f"{record['Book Title']} (Borrowed by {record['User Name']})"
                return_options[key] = (record['Book ID'], record['User ID'])
            
            with st.form("return_form"):
                selected_return = st.selectbox("Select Book to Return:", list(return_options.keys()))
                return_submitted = st.form_submit_button("Confirm Return")

                if return_submitted:
                    book_id, user_id = return_options[selected_return]
                    result = library.return_book(book_id, user_id)
                    if "Success" in result:
                        st.success(result)
                    else:
                        st.error(result)

elif menu == "View Users & Records":
    st.header("👥 User Management & Records")
    
    st.subheader("Add New User")
    user_name = st.text_input("New User Name:")
    if st.button("Add User"):
        if user_name:
            new_user = library.add_user(user_name)
            st.success(f"User added: {new_user.name} (ID: {new_user.user_id})")
        else:
            st.error("Please enter a user name.")
    
    st.markdown("---")
    st.subheader("All Registered Users")
    users_data = library.get_all_users_data()
    if users_data:
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users.set_index('User ID'), use_container_width=True)
    else:
        st.info("No users registered.")
        
    st.markdown("---")
    st.subheader("Current Borrowed Records")
    borrowed_records = library.get_borrowed_records()
    if borrowed_records:
        df_records = pd.DataFrame(borrowed_records)
        st.dataframe(df_records, use_container_width=True)
    else:
        st.info("No books are currently borrowed by any user.")