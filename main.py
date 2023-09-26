import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
                    BookID TEXT PRIMARY KEY,
                    Title TEXT,
                    Author TEXT,
                    ISBN TEXT,
                    Status INTEGER DEFAULT 0
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                    UserID TEXT PRIMARY KEY,
                    Name TEXT,
                    Email TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Reservations (
                    ReservationID INTEGER PRIMARY KEY AUTOINCREMENT,
                    BookID TEXT,
                    UserID TEXT,
                    ReservationDate TEXT,
                    FOREIGN KEY (BookID) REFERENCES Books (BookID),
                    FOREIGN KEY (UserID) REFERENCES Users (UserID)
                )''')


def add_book():
    # Add a new book to the Books table
    book_id = input("Enter BookID: ")
    title = input("Enter Title: ")
    author = input("Enter Author: ")
    isbn = input("Enter ISBN: ")

    cursor.execute("INSERT INTO Books (BookID, Title, Author, ISBN) VALUES (?, ?, ?, ?)",
                   (book_id, title, author, isbn))
    conn.commit()
    print("Book added successfully!")


def find_book_details():
    # Find book details based on BookID
    # Include reservation status and user details if reserved
    book_id = input("Enter BookID: ")
    cursor.execute('''SELECT Books.*, Reservations.ReservationDate, Users.UserID, Users.Name, Users.Email
                          FROM Books
                          LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                          LEFT JOIN Users ON Reservations.UserID = Users.UserID
                          WHERE Books.BookID = ?''', (book_id,))
    book_details = cursor.fetchone()

    if book_details is None:
        print("Book not found.")
    else:
        print("Book Details:")
        print("BookID:", book_details[0])
        print("Title:", book_details[1])
        print("Author:", book_details[2])
        print("ISBN:", book_details[3])
        if book_details[4] == 0:
            print("Status: Available")
        else:
            print("Status: Reserved")
            print("Reservation Date:", book_details[5])
            print("Reserved by:")
            print("UserID:", book_details[6])
            print("Name:", book_details[7])
            print("Email:", book_details[8])


def find_reservation_status():
    # Find book reservation status based on BookID, Title, UserID, or ReservationID
    search_term = input("Enter BookID, Title, UserID, or ReservationID: ")
    cursor.execute('''SELECT Books.BookID, Books.Title, Reservations.ReservationDate, Users.Name, Users.Email
                          FROM Books
                          LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                          LEFT JOIN Users ON Reservations.UserID = Users.UserID
                          WHERE Books.BookID = ?
                             OR Books.Title LIKE ?
                             OR Users.UserID = ?
                             OR Reservations.ReservationID = ?''',
                   (search_term, f'%{search_term}%', search_term, search_term))
    reservation_status = cursor.fetchall()

    if len(reservation_status) == 0:
        print("No reservations found.")
    else:
        print("Reservation Status:")
        for reservation in reservation_status:
            print("BookID:", reservation[0])
            print("Title:", reservation[1])
            print("Reservation Date:", reservation[2])
            print("Reserved by:")
            print("Name:", reservation[3])
            print("Email:", reservation[4])
            print("-----------------------")


def find_all_books():
    # Find all books and include details from all three tables
    cursor.execute('''SELECT Books.*, Reservations.ReservationDate, Users.UserID, Users.Name, Users.Email
                          FROM Books
                          LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
                          LEFT JOIN Users ON Reservations.UserID = Users.UserID''')
    all_books = cursor.fetchall()

    if len(all_books) == 0:
        print("No books found in the library.")
    else:
        print("All Books:")
        for book in all_books:
            print("BookID:", book[0])
            print("Title:", book[1])
            print("Author:", book[2])
            print("ISBN:", book[3])
            if book[4] == 0:
                print("Status: Available")
            else:
                print("Status: Reserved")
                print("Reservation Date:", book[5])
                print("Reserved by:")
                print("UserID:", book[6])
                print("Name:", book[7])
                print("Email:", book[8])
            print("-----------------------")


def update_book_details():
    # Modify/update book details based on BookID
    book_id = input("Enter BookID: ")
    new_title = input("Enter new title (leave empty to keep existing): ")
    new_author = input("Enter new author (leave empty to keep existing): ")
    new_isbn = input("Enter new ISBN (leave empty to keep existing): ")

    update_query = "UPDATE Books SET"
    update_fields = []
    update_values = []

    if new_title:
        update_fields.append("Title = ?")
        update_values.append(new_title)

    if new_author:
        update_fields.append("Author = ?")
        update_values.append(new_author)

    if new_isbn:
        update_fields.append("ISBN = ?")
        update_values.append(new_isbn)

    if not update_fields:
        print("No changes provided. Book details remain unchanged.")
        return

    update_query += " " + ", ".join(update_fields) + " WHERE BookID = ?"
    update_values.append(book_id)

    cursor.execute(update_query, tuple(update_values))
    conn.commit()
    print("Book details updated successfully!")


def delete_book():
    # Delete a book based on BookID
    # Handle deletion from both Books and Reservations tables if reserved
    book_id = input("Enter BookID: ")

    cursor.execute("SELECT * FROM Books WHERE BookID = ?", (book_id,))
    book = cursor.fetchone()

    if book is None:
        print("Book not found.")
        return

    if book[4] == 1:
        cursor.execute("DELETE FROM Reservations WHERE BookID = ?", (book_id,))
        conn.commit()

    cursor.execute("DELETE FROM Books WHERE BookID = ?", (book_id,))
    conn.commit()
    print("Book deleted successfully!")


while True:
    print("Library Management System Menu:")
    print("1. Add a new book")
    print("2. Find a book's details")
    print("3. Find reservation status")
    print("4. Find all books")
    print("5. Update book details")
    print("6. Delete a book")
    print("7. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_book()
    elif choice == "2":
        find_book_details()
    elif choice == "3":
        find_reservation_status()
    elif choice == "4":
        find_all_books()
    elif choice == "5":
        update_book_details()
    elif choice == "6":
        delete_book()
    elif choice == "7":
        break
    else:
        print("Invalid choice. Please try again.")

# Close the database connection
conn.close()