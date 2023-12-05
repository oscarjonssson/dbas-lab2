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

Väljer tabellerna C.Name och COUNT(B.country2) som räknar antalet gånger en unik värde i kolumnen Country2 från tabellen borders förekommer för varje land,
alltså antalet angränsande länder. En JOIN-operation sammanför Country och borders tabellerna genom att matcha Country-tabellens Code med Country1 eller Country2 i borders.
Om en landkod i Country överensstämmer med någon kod i borders, kombineras dessa rader.

```
SELECT C.Name AS Land,
       COUNT(B.Country2) AS number
FROM Country AS C
JOIN borders AS B ON C.Code = B.Country1 OR C.Code = B.Country2
GROUP BY C.Name
HAVING COUNT(B.Country2) = 1
ORDER BY number;
```
#### Assignment 2

Väljer S.laguage för att få alla språk sedan används `SUM(C.Population * (S.Percentage / 100))` för att beräknar det totala antalet talare för varje språk genom att multiplicera befolkningen i varje land med andelen som talar språket och sedan summera dessa värden för alla länder där språket talas. `CAST` gör så att värdet blir en integer och `COALESCE(...,0)`
gör att vi skkeiver 0 istället för null. JOIN-operationen kombinerar tabellerna Countruy och Spoken baserat på landkoden (Code i Country och Country i Spoken). Det innebär att för varje rad i Country, kopplas de motsvarande raderna i Spoken som har samma landkod.

```
SELECT S.Language, COALESCE(CAST(SUM(C.Population * (S.Percentage / 100)) AS INTEGER),0) AS TotalSpeakers
FROM Country C
JOIN Spoken S ON C.Code = S.Country
GROUP BY S.Language
ORDER BY TotalSpeakers DESC NULLS LAST, language;

```
#### Assignment 3

Först gör vi om country1 och country2s GDP till heltar sedan beräknar vi förhållandet mellan de två ländernas GDP.
CASE-satserna avgör vilket land som har högre BNP och delar det högre BNP-värdet med det lägre och avrundar till närmsat heltal.
Utför två JOIN-operationer för att koppla varje land i paren (country1 och country) med motsvarande post i Economy-tabellen, baserat på landets kod. Detta ger tillgång till GDP-information för varje land i paret. Använder `WHERE e1.GDP IS NOT NULL AND e2.GDP IS NOT NULL` för att säkerställa att endast de gränsparen där båda länderna har BNP-data (inte NULL) inkluderas i resultatet.

tar bort null värden för att det kan finnas länder vars gdp är null och därav anser vi att det inte är nödvändigt att ha med
```

SELECT  b.Country1, 
        CAST(e1.GDP AS INT) as GDP1, 
        b.Country2, 
        CAST(e2.GDP AS INT) as GDP2,
        ROUND((CASE
            WHEN e1.GDP > e2.GDP THEN e1.GDP / e2.GDP
            ELSE e2.GDP / e1.GDP END), 0) AS ContrastRatio
FROM borders b
JOIN Economy e1 ON b.Country1 = e1.Country
JOIN Economy e2 ON b.Country2 = e2.Country
WHERE e1.GDP IS NOT NULL AND e2.GDP IS NOT NULL
ORDER BY ContrastRatio DESC;

```
### P+

#### Assignment 1

Börjar med ett "basfall" där vi alltid startar från S (sverige) sedan skapar vi en konstant 1 eftersom i den första iterationen av queryn är antalet steg alltid 1, eftersom det är det första steget från 'S' till ett gränsande land. Skapar sedan en array där det i första itterationen bara finns S. väljer sedan alla rader från borders-tabellen där S är antingen Country1 eller Country2. Det innebär att den hittar alla länder som gränsar direkt till S. `pf.route || ARRAY[CASE...END]::text[]`  Uppdaterar rutten genom att lägga till den senaste destinationen. `FROM borders b INNER JOIN PathFinder pf ON pf.destination IN (b.Country1, b.Country2):` Denna JOIN kopplar ihop den nuvarande destinationen i rekursionen med nästa möjliga destination. Begränsar sedan rekursionen till mindre än 5. i det sista SELECT statementet ser vi till att det bara är den kostaste vägen som är med i resultaten samt att S är utesluten ur resultatet.


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

skapar en rekursiv CTE och väljer några specifika floder samt initierar några startvärden. Vi kollar sedan om  `rp.AlternativePath` är tom isåfall är vi i början av flodvägen, annars 
används || för att sammanfoga den befintliga (AlternativePath) med det aktuella flodnamnet. Använder JOIN för att länka floder (r) med tidigare flodvägar (rp) baserat på nuvarande flodväg (CurrentPath). Skapar sedan en separat CTE som beräknar den maximala antalet floder (RiverCount) i varje flodväg (PrimaryRiver). I huvud SEELECT satsen så rankar `RANK() OVER (ORDER BY rp.RiverCount)`  flodvägarna baserat på antalet floder i varje väg (RiverCount). Använder JOIN för att filtrera så att endast de längsta flodvägarna för varje PrimaryRiver inkluderas, baserat på MaxRiverCount.


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









