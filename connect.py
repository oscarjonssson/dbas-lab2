import psycopg2
from datetime import datetime, timedelta

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
                WHERE genre.genre = %s""", (genre)
    cur.execute(query)
    result = cur.fetchall()
    titles = [row[0] for row in result]

    print(titles)

# function to Show all physical books with a given title.
def get_physical_books_by_title():
    title = input("Please enter a title: ")
    query = """ SELECT Resources.physicalID,
                    Books.title
                FROM Resources
                JOIN Books ON Resources.bookID = Books.bookID
                WHERE Books.title = %s""", (title)
    cur.execute(query)
    result = cur.fetchall()
    print(result)

# function to Show a list of titles and how many physical copies are available (i.e. all copiesthat are not borrowed).
def get_available_physical_books():
    query = """ SELECT b.title,
                COUNT(DISTINCT r.physicalid) - COUNT(DISTINCT CASE
                                                                WHEN bor.dor IS NULL
                                                                    AND bor.dob IS NOT NULL THEN r.physicalid
                                                            END) AS available_copies
                FROM books b
                LEFT JOIN resources r ON b.bookID = r.bookid
                LEFT JOIN
                    (SELECT physicalid,
                        MAX(dob) AS max_borrow_date
                    FROM borrowing
                    GROUP BY physicalid) AS latest_borrowings ON r.physicalid = latest_borrowings.physicalid
                LEFT JOIN borrowing bor ON latest_borrowings.physicalid = bor.physicalid
                AND latest_borrowings.max_borrow_date = bor.dob
                GROUP BY b.title
                ORDER BY b.title"""
    cur.execute(query)
    result = cur.fetchall()
    print(result)

def is_student(user_id):
    query = """ SELECT userID
                FROM students
                WHERE userID = %s""", (user_id)
    cur.execute(query)
    if cur.fetchall() == 0:
        return False
    else:
        return True
    
def has_fines(user_id):
    query = """ SELECT Fines.borrowingID
                FROM Fines
                JOIN Borrowing On Fines.borrowingID = Borrowing.borrowingID
                WHERE Fines.Amount > 0
                    AND Borrowing.userID = %s""", (user_id)
    cur.execute(query)
    if len(cur.fetchall()) > 0:
        print("You have unpid fines.")
        return True
    else: 
        return False

def borrowed_books(user_id):
    query = """ SELECT borrowingID
                FROM borrowing
                WHERE userID = %s
                    AND dor IS NULL""", (user_id)
    cur.execute(query)
    if len(cur.fetchall()) >= 4:
        print("You can only borrow 4 books at a time.")
        return True
    else:
        return False

def ISBN_availability(user_id, ISBN):
    cur.execute("SELECT e.ISBN FROM Books b JOIN Edition e ON b.bookID = e.bookID JOIN Resources r ON b.bookID = r.bookID JOIN Borrowing bor ON r.physicalID = bor.physicalID WHERE bor.userID = %s AND e.isbn = %s", (user_id, ISBN))
    if len(cur.fetchall()) >= 6:
        print("You cannot borrow this book again.")
        return False
    cur.execute("SELECT r.physicalID FROM Books b LEFT JOIN Resources r ON b.bookID = r.bookID LEFT JOIN Edition e ON b.bookID = e.bookID LEFT JOIN (SELECT physicalID, MAX(DoB) AS max_borrow_date FROM Borrowing GROUP BY physicalID) AS latest_borrowings ON r.physicalID = latest_borrowings.physicalID LEFT JOIN Borrowing bor ON latest_borrowings.physicalID = bor.physicalID AND latest_borrowings.max_borrow_date = bor.DoB WHERE e.isbn = %s AND (bor.DoR IS NOT NULL OR latest_borrowings.physicalID IS NULL) AND r.physicalID IS NOT NULL", (ISBN,))
    if len(cur.fetchall()) < 1:
        print("This book is not available for borrowing.")
        return False
    else: return True

def insert_borrowing(user_id, ISBN):
    cur.execute("SELECT r.physicalID FROM Books b LEFT JOIN Resources r ON b.bookID = r.bookID LEFT JOIN Edition e ON b.bookID = e.bookID LEFT JOIN (SELECT physicalID, MAX(DoB) AS max_borrow_date FROM Borrowing GROUP BY physicalID) AS latest_borrowings ON r.physicalID = latest_borrowings.physicalID LEFT JOIN Borrowing bor ON latest_borrowings.physicalID = bor.physicalID AND latest_borrowings.max_borrow_date = bor.DoB WHERE e.isbn = %s AND (bor.DoR IS NOT NULL OR latest_borrowings.physicalID IS NULL) AND r.physicalID IS NOT NULL", (ISBN,))
    physical_copies = cur.fetchall()
    physical_id = physical_copies[0]

    cur.execute("SELECT borrowingID FROM borrowing")
    ID_list = cur.fetchall()
    borrowing_id = max(ID_list, key=lambda x: x[0])[0] + 1

    current_date_time = datetime.now()

    dob = current_date_time.date()
    doe = dob + timedelta(days=7)

    cur.execute("INSERT INTO Borrowing(BorrowingID,physicalID,userID,DoB,DoR,DoE) VALUES(%s, %s, %s, %s, %s, %s)",(borrowing_id, physical_id, user_id, dob, None, doe))

    print("Return the book by:", doe)
    conn.commit()



def borrow_book():
    email = input("Email: ")
    cur.execute("SELECT userID FROM users WHERE email = %s", (email,))
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



if __name__ == "__main__":
    get_available_physical_books()
    get_book_title_by_genre()
    get_physical_books_by_title()
    borrow_book()
    