import psycopg2

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
    query = f"SELECT books.title FROM books LEFT JOIN genre ON books.bookid = genre.bookid WHERE genre.genre = '{genre}'"
    cur.execute(query)
    result = cur.fetchall()
    titles = [row[0] for row in result]

    print(titles)

# function to Show all physical books with a given title.
def get_physical_books_by_title():
    title = input("Please enter a title: ")
    query = f"SELECT resources.physicalID, books.title FROM resources JOIN Books ON resources.bookid = books.bookid WHERE books.title = '{title}'"
    cur.execute(query)
    result = cur.fetchall()
    print(result)

# function to Show a list of titles and how many physical copies are available (i.e. all copiesthat are not borrowed).
def get_available_physical_books():
    query = """SELECT b.title, COUNT(DISTINCT r.physicalid) - COUNT(DISTINCT CASE WHEN bor.dor IS NULL THEN r.physicalid END) AS available_copies
                FROM books b
                LEFT JOIN Resources r ON b.bookid = r.bookid
                LEFT JOIN (
                    SELECT physicalid, MAX(dob) AS max_borrow_date
                    FROM borrowing
                    GROUP BY physicalid
                ) AS latest_borrowings ON r.physicalid = latest_borrowings.physicalid
                LEFT JOIN borrowing bor ON latest_borrowings.physicalid = bor.physicalid AND latest_borrowings.max_borrow_date = bor.dob
                GROUP BY b.title
                ORDER BY b.title"""
    cur.execute(query)
    result = cur.fetchall()
    print(result)

#function to check if the user is a student
def is_student(user_id):
    cur.execute("SELECT * FROM students WHERE userid = %s", (user_id,))
    result = cur.fetchone()
    if len(result) > 0:
        return True
    else:
        return False

# function to check if the user has any fines

def check_fine(cur, user_id):
    cur.execute("SELECT * FROM fines WHERE userid = %s", (user_id,))
    result = cur.fetchone()
    if result:
        print("You have a fine")
        return False
    else:
        return True
    
def check_nr_of_borrowed_books(cur, user_id):
    cur.execute("SELECT COUNT(*) FROM borrowing WHERE userid = %s", (user_id,))
    result = cur.fetchone()
    if result[0] >= 5:
        print("You have borrowed 5 books")
        return False
    else:
        return True
    
def check_isbn(cur, user_id, isbn):
    cur.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
    result = cur.fetchone()
    if result:
        return True
    else:
        print("Invalid ISBN")
        return False
    
def retrieve_values_for_insert(user_id, isbn):
    cur.execute("SELECT bookid FROM books WHERE isbn = %s", (isbn,))
    book_id = cur.fetchone()
    cur.execute("SELECT physicalid FROM resources WHERE bookid = %s", (book_id,))
    physical_id = cur.fetchone()
    cur.execute("INSERT INTO borrowing (userid, physicalid) VALUES (%s, %s)", (user_id, physical_id))
    conn.commit()
    print("You have borrowed the book")

# function to borrow a book using a given email of an existing user in the database.
# - Check that the email exists in the database.
# - Add the borrowed book in the relevant table and tell the user when they’re expected to return it.
def borrow_book():
    # Check if the email exists in the users table
    email = input("Please enter email: ")
    cur.execute("SELECT userID FROM users WHERE email = %s", (email,))
    user_id = cur.fetchone()

    if user_id:
        # Check constraints
        # For students
        if is_student(user_id):
            if check_fine(cur, user_id) and check_nr_of_borrowed_books(cur, user_id):
                isbn = input("Please enter the ISBN of the book you want to borrow: ")
                if check_isbn(cur, user_id, isbn):
                    retrieve_values_for_insert(user_id, isbn)

        # For Admins
        else:
            isbn = input("Please enter the ISBN of the book you want to borrow: ")
            retrieve_values_for_insert(user_id, isbn)
    else:
        print("Invalid Email")

if __name__ == "__main__":
    get_available_physical_books()
    get_book_title_by_genre()
    get_physical_books_by_title()
    borrow_book()
    
    