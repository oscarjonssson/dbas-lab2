## Labb 2

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
        b.title,
        b.bookid, 
        p.prequelid 
    FROM 
        books b
    LEFT JOIN 
        prequels p ON b.bookid = p.bookid
    WHERE 
        b.bookid = '3747'

    UNION

    SELECT 
        b.title,
        b.bookid, 
        p.prequelid 
    FROM 
        books b
    LEFT JOIN 
        prequels p ON b.bookid = p.bookid
    INNER JOIN 
        HarryPotterSeries hps ON(b.bookid = hps.prequelid OR p.prequelid = hps.bookid)
)
SELECT * FROM HarryPotterSeries;


```
    
```
SELECT
    a.author,
    MAX( CASE WHEN EXISTS (SELECT r.physicalid
FROM 
    resources r
JOIN 
    borrowing b ON r.physicalid = b.physicalid
WHERE 
    r.bookid = a.bookid AND EXTRACT(MONTH FROM b.dor) = 5)
THEN 1
ELSE 0
END
    )::BOOLEAN AS "true/false"
FROM
    author a
GROUP BY
    a.author
ORDER BY
  "true/false" DESC

```

## Labb 3

### P

#### Asingnment 1
```
SELECT C.Name AS Land,
       COUNT(B.Country2) AS number
FROM Country AS C
JOIN borders AS B ON C.Code = B.Country1 OR C.Code = B.Country2
GROUP BY C.Name
ORDER BY number DESC;
```
#### Assignment 2
```
SELECT S.Language, CAST(SUM(C.Population * (S.Percentage / 100)) AS INTEGER) AS TotalSpeakers
FROM Country C
JOIN Spoken S ON C.Code = S.Country
GROUP BY S.Language
ORDER BY TotalSpeakers DESC NULLS LAST, language;

```
#### Assignment 3

```

SELECT  b.Country1, 
    CAST(e1.GDP AS INT) as GDP1, 
    b.Country2, 
    CAST(e2.GDP AS INT) as GDP2,(CASE
    WHEN e1.GDP > e2.GDP THEN e1.GDP / e2.GDP
    ELSE e2.GDP / e1.GDP END) AS ContrastRatio
FROM borders b
JOIN Economy e1 ON b.Country1 = e1.Country
JOIN Economy e2 ON b.Country2 = e2.Country
ORDER BY ContrastRatio DESC NULLS LAST, contrastratio;
```
### P+

#### Assignment 1
```
WITH RECURSIVE PathFinder AS (
  SELECT 
    CASE 
      WHEN b.Country1 = 'S' THEN b.Country2 
      ELSE b.Country1 
    END AS destination, 
    1 AS steps, 
    ARRAY['S'] AS route
  FROM 
    borders b
  WHERE 
    'S' = ANY(ARRAY[b.Country1, b.Country2])

  UNION ALL

  SELECT 
    CASE 
      WHEN b.Country1 = pf.destination THEN b.Country2 
      ELSE b.Country1 
    END, 
    pf.steps + 1, 
    pf.route || ARRAY[CASE 
                        WHEN b.Country1 = pf.destination THEN b.Country2 
                        ELSE b.Country1 
                      END]::text[]
  FROM 
    borders b
  INNER JOIN 
    PathFinder pf ON pf.destination IN (b.Country1, b.Country2)
  WHERE 
    pf.steps < 5
)

SELECT 
  pf.destination AS code,
  c.Name,
  MIN(pf.steps) AS shortest_path
FROM 
  PathFinder pf
JOIN 
  Country c ON pf.destination = c.Code
WHERE 
  pf.destination <> 'S'
GROUP BY 
  pf.destination, c.Name
ORDER BY 
  shortest_path, c.Name;


```



#### Assignment 2

```
WITH Recursive RiverPaths AS (
    SELECT 
        r.Name AS PrimaryRiver,
        '' AS AlternativePath,
        r.Name AS CurrentPath,
        1 AS Level,
        1 AS RiverCount,
        r.Length AS TotalLength
    FROM 
        River r
    WHERE 
        r.Name IN ('Nile', 'Amazonas', 'Yangtze', 'Rhein', 'Donau', 'Mississippi')

    UNION ALL

    SELECT 
        rp.PrimaryRiver,
        CASE
            WHEN rp.AlternativePath = '' THEN r.River
            ELSE rp.AlternativePath || '-' || r.River
        END AS AlternativePath,
        r.Name AS CurrentPath,
        rp.Level + 1 AS Level,
        rp.RiverCount + 1 AS RiverCount,
        rp.TotalLength + r.Length AS TotalLength
    FROM 
        River r
        JOIN RiverPaths rp ON r.River = rp.CurrentPath
),
MaxRiverCounts AS (
    SELECT 
        PrimaryRiver,
        MAX(RiverCount) AS MaxRiverCount
    FROM RiverPaths
    GROUP BY PrimaryRiver
)

SELECT 
    RANK() OVER (ORDER BY rp.RiverCount) AS Rank,
    rp.AlternativePath || '-' || rp.CurrentPath AS RiverPath,
    rp.RiverCount AS RiverCount,
    rp.TotalLength AS TotalLength
FROM 
    RiverPaths rp
JOIN 
    MaxRiverCounts mrc ON rp.PrimaryRiver = mrc.PrimaryRiver
    AND rp.RiverCount = mrc.MaxRiverCount
ORDER BY 
    Rank,
    TotalLength DESC;

```









