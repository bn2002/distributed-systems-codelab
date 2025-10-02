# Thực hành Master-Salve trong MySQL
## Câu hỏi 1: What is the output did you see? Now, try to add another entry to the table pet in using SQL queries.

Kết quả trên terminal:
```
+---------+--------+---------+------+------------+------------+
| name    | owner  | species | sex  | birth      | death      |
+---------+--------+---------+------+------------+------------+
| Whistler| Gwen   | bird    | NULL | 1997-12-09 | NULL       |
| Fluffy  | Harold | cat     | f    | 1993-02-04 | NULL       |
| Claws   | Gwen   | cat     | m    | 1994-03-17 | NULL       |
| Buffy   | Harold | dog     | f    | 1989-05-13 | NULL       |
| Fang    | Benny  | dog     | m    | 1990-08-27 | 1997-04-04 |
+---------+--------+---------+------+------------+------------+
```
5 rows in set (0.00 sec)

Thêm 1 bản ghi mới
```
INSERT INTO pet VALUES ('John', 'VN', 'dog', 'f', '1998-01-28', NULL);
```

## Câu hỏi 2: What is the name of the log file and the position?
Khi chạy lệnh
```
SHOW MASTER STATUS;
```

Kết quả
```
+------------------+----------+--------------+------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB |
+------------------+----------+--------------+------------------+
| mysql-bin.000001 |      879 | petdatabase  |                  |
+------------------+----------+--------------+------------------+
1 row in set (0.00 sec)
```
Tên file log: mysql-bin.000001

Position: 879

## Câu hỏi 3: Have you received this file in Slave machine? What is the path of this received file in the Slave machine?

Có, Salve machine có nhận được file, với user của Salve machine là bn2002, thì file được lưu tại 
```
/home/bn2002/petdatabase.sql
```

## Câu hỏi 4: What is the status information you received? How do you know the configuration is OK?
Khi chạy lệnh
```
SHOW SLAVE STATUS
```

Ta thấy các thông số:
- Slave_IO_Running: Yes
- Slave_SQL_Running: Yes

Tức là quá trình config đã thành công

## Câu hỏi 5: In the Slave machine, verify if the new inserted data has been
Để xác minh trên máy salve, ta chạy lệnh
```
SELECT * FROM pet;
```
Kết quả
```
+----------+--------+---------+------+------------+------------+
| name     | owner  | species | sex  | birth      | death      |
+----------+--------+---------+------+------------+------------+
| Whistler | Gwen   | bird    | NULL | 1997-12-09 | NULL       |
| Fluffy   | Harold | cat     | f    | 1993-02-04 | NULL       |
| Claws    | Gwen   | cat     | m    | 1994-03-17 | NULL       |
| Buffy    | Harold | dog     | f    | 1989-05-13 | NULL       |
| Fang     | Benny  | dog     | m    | 1990-08-27 | 1997-04-04 |
| John     | VN     | dog     | f    | 1998-01-28 | NULL |
| Puffball | Diane  | hamster | f    | 1999-03-30 | NULL       |
+----------+--------+---------+------+------------+------------+
7 rows in set (0.00 sec)
```
