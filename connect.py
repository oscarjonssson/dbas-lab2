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
    query = f"SELECT Resources.physicalID, Books.title FROM Resources JOIN Books ON Resources.bookID = Books.bookID WHERE Books.title = '{title}'"
    cur.execute(query)
    result = cur.fetchall()
    print(result)

# function to Show a list of titles and how many physical copies are available (i.e. all copiesthat are not borrowed).
def get_available_physical_books():
    query = """SELECT b.title, COUNT(DISTINCT r.physicalID) - COUNT(DISTINCT CASE WHEN bor.dor IS NULL THEN r.physicalid END) AS available_copies
                FROM books b
                LEFT JOIN resources r ON b.bookID = r.bookid
                LEFT JOIN (
                    SELECT physicalid, MAX(dob) AS max_borrow_date
                    FROM borrowing
                    GROUP BY physicalid
                ) AS latest_borrowings ON r.physicalid = latest_borrowings.physicalid
                LEFT JOIN borrowing bor ON latest_borrowings.physicalid = bor.physicalid AND latest_borrowings.max_borrow_date = bor.dob
                GROUP BY b.title
                ORDER BY b.title"""
    result = cur.fetchall()
    print(result)


if __name__ == "__main__":
    get_available_physical_books()
    get_book_title_by_genre()
    get_physical_books_by_title()
    
    