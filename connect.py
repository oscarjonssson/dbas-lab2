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

if __name__ == "__main__":
    get_book_title_by_genre()
    get_physical_books_by_title()