# dbas-

* admins table
  userid
  department
  phonenumber

* author table
  nookid
  author

* books table
  bookid
  title 
  pages

* borrowing table
  borrowingid
  physicaliduserid
  dob
  dor
  doe

* edition table
  bookid
  isbn 
  edition
  publisher
  dop

* fines table
  borrowingid
  amount
  
* genre table
  bookid
  genre

* language table
  bookid
  language

* prequel tables
  bookid
  prequelid

* resources table
  physicalid
  bookid
  damaged

* students table
  userid
  program

* transaction table
  transactionid
  borrowingid
  paymentmethod
  dop

* users table
  userid
  name
  address
  email

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

