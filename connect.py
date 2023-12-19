import psycopg2
from datetime import datetime, timedelta
import sys

"""
Note: It's essential never to include database credentials in code pushed to GitHub. 
Instead, sensitive information should be stored securely and accessed through environment variables or similar. 
However, in this particular exercise, we are allowing it for simplicity, as the focus is on a different aspect.
Remember to follow best practices for secure coding in production environments.
"""

# Acquire a connection to the database by specifying the credentials.
conn = psycopg2.connect(
    host="psql-dd1368-ht23.sys.kth.se", 
    database="oscjonss",
    user="oscjonss",
    password="g3MBYp2i")
print(conn)

# Create a cursor. The cursor allows you to execute database queries.
cur = conn.cursor()

# Simple function to get all books with a specific genre.
def get_book_title_by_genre():
    genre = input("Please enter a genre: ")
    query = """ SELECT books.title
                FROM books
                LEFT JOIN genre ON books.bookid = genre.bookid
                WHERE genre.genre = %s"""
    cur.execute(query, (genre,))
    result = cur.fetchall()
    titles = [row[0] for row in result]

    print(titles)

# Show all physical books with a given title.
def get_physical_books_by_title():
    title = input("Please enter a title: ")
    query = """ SELECT Resources.physicalID,
                    Books.title
                FROM Resources
                JOIN Books ON Resources.bookID = Books.bookID
                WHERE Books.title = %s"""
    cur.execute(query, (title,))
    result = cur.fetchall()
    print(result)

# Show a list of titles and how many physical copies are available (i.e. all copiesthat are not borrowed).
def get_available_physical_books():
    query = """ SELECT b.title,
                COUNT(DISTINCT r.physicalid) - COUNT(DISTINCT CASE
                                                                WHEN br.dor IS NULL
                                                                    AND br.dob IS NOT NULL THEN r.physicalid
                                                            END) AS available_copies
                FROM books b
                LEFT JOIN resources r ON b.bookID = r.bookID
                LEFT JOIN
                    (SELECT physicalid,
                        MAX(dob) AS latest_borrowing
                    FROM borrowing
                    GROUP BY physicalid) AS recent ON r.physicalid = recent.physicalid
                LEFT JOIN borrowing br ON recent.physicalid = br.physicalid
                AND recent.latest_borrowing = br.dob
                GROUP BY b.title
                ORDER BY b.title"""
    cur.execute(query)
    result = cur.fetchall()
    print(result)

# Checks if a user is a student, return true if so.
def is_student(user_id):
    query = """ SELECT userID
                FROM students
                WHERE userID = %s"""
    cur.execute(query, (user_id,))
    if cur.fetchall() == 0:
        return False
    else:
        return True
    
# Checks if a user has outstanding fines, return true if so.
def has_fines(user_id):
    query = """ SELECT f.borrowingID
                FROM Fines f
                JOIN Borrowing br On f.borrowingID = br.borrowingID
                WHERE f.Amount > 0
                    AND br.userID = %s"""
    cur.execute(query, (user_id,))
    if len(cur.fetchall()) > 0:
        print("You have unpid fines.")
        return True
    else: 
        return False

# Checks if a user has borrowed more than 4 book, return True if so.
def borrowed_books(user_id):
    query = """ SELECT borrowingID
                FROM borrowing
                WHERE userID = %s
                    AND dor IS NULL"""
    cur.execute(query, (user_id,))
    if len(cur.fetchall()) >= 4:
        print("You can only borrow 4 books at a time.")
        return True
    else:
        return False

# Checks if a user can borrow a specific book by its ISBN, returns True if so.
# Checks both if a user has borrowed it more than 6 times, and if it is avaliable for borrowing.
def ISBN_availability(user_id, ISBN):
    query = """ SELECT e.ISBN
                FROM Books b
                JOIN Edition e ON b.bookID = e.bookID
                JOIN Resources r ON b.bookID = r.bookID
                JOIN Borrowing br ON r.physicalID = br.physicalID
                WHERE br.userID = %s
                    AND e.isbn = %s"""
    cur.execute(query, (user_id, ISBN,))
    if len(cur.fetchall()) >= 6:
        print("You cannot borrow this book again.")
        return False
    
    query = """ SELECT r.physicalID
                FROM Books b
                LEFT JOIN Resources r ON b.bookID = r.bookID
                LEFT JOIN Edition e ON b.bookID = e.bookID 
                LEFT JOIN
                    (SELECT physicalID,
                        MAX(DoB) AS latest_borrowing
                    FROM Borrowing
                    GROUP BY physicalID) AS recent ON r.physicalID = recent.physicalID
                LEFT JOIN Borrowing br ON recent.physicalID = br.physicalID
                AND recent.latest_borrowing = br.DoB
                WHERE e.isbn = %s
                    AND (br.DoR IS NOT NULL
                        OR recent.physicalID IS NULL)
                    AND r.physicalID IS NOT NULL"""
    cur.execute(query, (ISBN,))
    if len(cur.fetchall()) < 1:
        print("This book is not available for borrowing.")
        return False
    
    return True

# Adds a book to the borrowing table.
def insert_borrowing(user_id, ISBN):
    query = """ SELECT r.physicalID
                FROM Books b
                LEFT JOIN Resources r ON b.bookID = r.bookID
                LEFT JOIN Edition e ON b.bookID = e.bookID 
                LEFT JOIN
                    (SELECT physicalID,
                        MAX(DoB) AS latest_borrowing
                    FROM Borrowing
                    GROUP BY physicalID) AS recent ON r.physicalID = recent.physicalID
                LEFT JOIN Borrowing br ON recent.physicalID = br.physicalID
                AND recent.latest_borrowing = br.DoB
                WHERE e.isbn = %s
                    AND (br.DoR IS NOT NULL
                        OR recent.physicalID IS NULL)
                    AND r.physicalID IS NOT NULL"""
    cur.execute(query, (ISBN,))
    physical_copies = cur.fetchall()
    physical_id = physical_copies[0]

    query = """ SELECT borrowingID
                FROM borrowing"""
    cur.execute(query)
    ID_list = cur.fetchall()
    borrowing_id = max(ID_list, key=lambda x: x[0])[0] + 1

    current_date_time = datetime.now()

    dob = current_date_time.date()
    doe = dob + timedelta(days=7)

    query = """ INSERT INTO Borrowing(BorrowingID,physicalID,userID,DoB,DoR,DoE)
                VALUES(%s, %s, %s, %s, %s, %s)"""
    cur.execute(query, (borrowing_id, physical_id, user_id, dob, None, doe,))

    print("Return the book by:", doe)
    conn.commit()


# Lets a user borrow a book.
def borrow_book():
    email = input("Email: ")
    query = """ SELECT userID
                FROM users
                WHERE email = %s"""
    cur.execute(query, (email,))
    user_id = cur.fetchone()

    if user_id:
        if (is_student(user_id)):
            if ((has_fines(user_id) == False) and (borrowed_books(user_id) == False)):
                ISBN = input("Enter the ISBN of the book you want to borrow: ")
                if ISBN_availability(user_id, ISBN):
                    insert_borrowing(user_id, ISBN)
        else:
            ISBN = input("Enter the ISBN of the book you want to borrow: ")
            if ISBN_availability(ISBN):
                insert_borrowing(user_id)
    else:
        print("Invalid email.")

# Main function.
if __name__ == "__main__":
    while True:
        print("Select an option: ")
        print("0: Quit")
        print("1. Show books by genre")
        print("2. Show books by title")
        print("3. Show all books")
        print("4. Borrow book")

        option = input("-> ")

        if option == "0":
            sys.exit()
        elif option == "1":
            get_book_title_by_genre()
        elif option == "2":
            get_physical_books_by_title()
        elif option == "3":
            get_available_physical_books()
        elif option == "4":
            borrow_book()
        
        #match option:
        #    case 0:
        #        sys.exit()
        #    case 1:
        #        get_book_title_by_genre()
        #    case 2:
        #        get_physical_books_by_title()
        #    case 3:
        #        get_available_physical_books()
        #    case 4:
        #        borrow_book()