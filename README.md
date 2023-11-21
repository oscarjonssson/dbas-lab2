# dbas-

admins: userid, department, phonenumber

author: bookid, author

books: bookid, title, pages

borrowing: borrowingid, physicalid, userid, dob, dor, doe

edition: bookid, isbn, edition, publisher, dop

fines: borrowingid; amount
  
genre: bookid, genre

language: bookid, language

prequel: bookid, prequelid

resources: physicalid, bookid, damaged

students: userid, program

transaction: transactionid, borrowingid, paymentmethod, dop

users: userid, name, address, email

Assignment 1

```
SELECT
  b.title,
  STRING_AGG(g.genre, ', ') AS genre
FROM
  books b
JOIN
  genre g ON b.bookid = g.bookid
GROUP BY
  b.title
ORDER BY
  CAST(b.title AS BYTEA);
```
Assignment 2

```
WITH BookBorrowCounts AS (
    SELECT
        b.bookid,
        COUNT(bor.borrowingid) AS borrow_count
    FROM
        books b
    INNER JOIN
        genre g ON b.bookid = g.bookid
    INNER JOIN
        resources res ON b.bookid = res.bookid
    INNER JOIN
        borrowing bor ON res.physicalid = bor.physicalid
    WHERE
        g.genre = 'RomCom'
    GROUP BY
        b.bookid
),
RankedBooks AS (
    SELECT
        b.title,
        DENSE_RANK() OVER (ORDER BY bbc.borrow_count DESC) AS rank
    FROM
        books b
    INNER JOIN
        BookBorrowCounts bbc ON b.bookid = bbc.bookid
)
SELECT
    title,
    rank
FROM
    RankedBooks
WHERE
    rank <= 5
ORDER BY
    rank;

```

Assignment 3

```
WITH Borrowed AS (
    SELECT 
        date_part('week', dob) AS week,
        COUNT(*) AS borrowed_count
    FROM 
        borrowing
    WHERE 
        date_part('week', dob) BETWEEN 1 AND 30
    GROUP BY 
        week
),
Returned AS (
    SELECT 
        date_part('week', dor) AS week,
        COUNT(*) AS returned_count,
        COUNT(*) FILTER (WHERE dor > doe) AS late_count
    FROM 
        borrowing
    WHERE 
        date_part('week', dor) BETWEEN 1 AND 30
    GROUP BY 
        week
)
SELECT 
    COALESCE(b.week, r.week) AS week,
    COALESCE(b.borrowed_count, 0) AS borrowed,
    COALESCE(r.returned_count, 0) AS returned,
    COALESCE(r.late_count, 0) AS late
FROM 
    Borrowed b
FULL OUTER JOIN 
    Returned r ON b.week = r.week
ORDER BY 
    week;

```

Assignment 4

```
SELECT
    b.title,
    EVERY(p.prequelid IS NOT NULL) AS EVERY,
    bor.dob 
FROM
    books b
JOIN
    resources res ON b.bookid = res.bookid
JOIN
    borrowing bor ON res.physicalid = bor.physicalid
LEFT JOIN
    prequels p ON b.bookid = p.bookid
WHERE
    EXTRACT(MONTH FROM bor.dob) = 2
GROUP BY
    b.title, bor.dob
ORDER BY
    CAST(b.title AS BYTEA);


```

Assignment 5

```
WITH RECURSIVE HarryPotterSeries AS (
    SELECT 
        b.bookid, 
        b.title, 
        p.prequelid 
    FROM 
        books b
    LEFT JOIN 
        prequels p ON b.bookid = p.bookid
    WHERE 
        b.title = 'Harry Potter and the Deathly Hallows'
    UNION ALL
    SELECT 
        b.bookid, 
        b.title, 
        p.prequelid 
    FROM 
        books b
    INNER JOIN 
        prequels p ON b.bookid = p.bookid
    INNER JOIN 
        HarryPotterSeries hps ON p.bookid = hps.prequelid
)
SELECT
    title,
    bookid, 
    prequelid
    
FROM 
    HarryPotterSeries
ORDER BY 
    title;


```

Assigment P+

```
SELECT
    a.author,
    MAX(
        CASE WHEN EXISTS (
                SELECT 
                  r.physicalid
                FROM 
                  resources r
                JOIN 
                  borrowing b ON r.physicalid = b.physicalid
                WHERE 
                  r.bookid = a.bookid
                AND EXTRACT(MONTH FROM b.dor) = 5
            ) THEN 1
            ELSE 0
        END
    )::BOOLEAN AS "true/false"
FROM
    author a
GROUP BY
    a.author;
```
