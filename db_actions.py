import mysql.connector
import json
import random
import bcrypt
from uuid import uuid4
from flask import url_for
from werkzeug.utils import secure_filename


db = None
cursor = None


def connect():
    global db
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="user",
        passwd="password",
        auth_plugin="mysql_native_password",
        database="BookStore",
    )

    global cursor
    cursor = db.cursor(buffered=True)


def disconnect():
    db.disconnect()


def user_auth(email, passwd):
    cursor.execute(
        f'select email, cast(passwd as char(60)), profile_pic from user where email = "{email}"'
    )
    l = cursor.fetchall()
    if len(l) > 0:
        if bcrypt.checkpw(passwd.encode("utf-8"), l[0][1].encode("utf-8")):
            if l[0][2]:
                return l[0][2]
            else:
                return True

    return False


def all_genres():
    s = set()
    cursor.execute("select genre from genres")

    l = cursor.fetchall()
    return [i[0] for i in l]


def add_user(email, user, passwd, tags, img):
    cursor.execute("select email from user")

    l = cursor.fetchall()

    if (email,) not in l:
        hashed = str(bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt()))[2:-1]

        cursor.execute(
            f'insert into user(email, username, passwd, tags) values ("{email}","{user}","{hashed}",\'{tags}\')'
        )

        if img:
            img.thumbnail((600, 600))

            filename = secure_filename(email + ".png")

            img.save("." + url_for("static", filename=f"profiles/{filename}"), "png")

            cursor.execute(
                f'update user set profile_pic = "{filename}" where email = "{email}"'
            )

        db.commit()
        return True
    else:
        return False


def recomend(email):
    cursor.execute(f'select tags from user where email = "{email}"')
    tags = json.loads(cursor.fetchone()[0])

    if len(tags) > 0:
        s = set()
        for i in tags:
            cursor.execute(
                f'select name, author, price, thumb from books where (name, author, 1) in (select name, author, JSON_CONTAINS(tags, JSON_ARRAY("{i}")) from books)'
            )

            l = cursor.fetchall()
            for j in l:
                s.add(j)

        lis = list(s)
        random.shuffle(lis)

        if len(lis) <= 5:
            return lis

        out = []
        n = 0
        while len(out) < 5:
            out.append(lis[n])
            n += 1

        return out

    else:
        return select_random()


def select_random():
    cursor.execute("select name, author, price, thumb from books order by rand()")
    l = cursor.fetchmany(49)

    l.append(("Uranium-235", "Jesse Russell", 235.0, "URANIUM.png"))

    random.shuffle(l)

    f = []
    n = 0
    while n < 5:
        f.append(l[n])
        n += 1

    return f


def authors():
    cursor.execute("select distinct author from books order by author")
    l = cursor.fetchall()

    d = dict()
    for i in l:
        if i[0][0] in d:
            d[i[0][0]] += (i[0],)
        else:
            d[i[0][0]] = (i[0],)

    return {i: d[i] for i in d}


def author(a):
    cursor.execute(
        f'select name, author, price, thumb from books where author = "{a}" order by release_date desc'
    )

    l = cursor.fetchall()

    if len(l) > 0:
        return l

    return False


def genre_list():
    g = all_genres()

    d = dict()
    for i in g:
        if i[0][0] in d:
            d[i[0][0]] += (i,)
        else:
            d[i[0][0]] = (i,)

    return d


def genre(gen):
    if gen in all_genres():
        cursor.execute(
            f'select name, author, price, thumb from books where (name, author, 1) in (select name, author, JSON_CONTAINS(tags, JSON_ARRAY("{gen}")) from books) order by name'
        )
        l = cursor.fetchall()

        return l

    return False


def series_list():
    cursor.execute(
        f"select distinct series from books where series is not null order by series"
    )
    l = cursor.fetchall()

    d = dict()
    for i in l:
        if i[0][0] in d:
            d[i[0][0]] += (i[0],)
        else:
            d[i[0][0]] = (i[0],)

    return {i: d[i] for i in d}


def series(s):
    cursor.execute(
        f'select name, author, price, thumb from books where series = "{s}" order by series_sl_no'
    )
    l = cursor.fetchall()

    if len(l) > 0:
        return l

    return False


def search(query):
    l = query.upper().split()

    cursor.execute(
        "select JSON_MERGE(tags, JSON_ARRAY(series, name, author)) from books"
    )
    lis = cursor.fetchall()

    fin = []
    for i in lis:
        c = 0
        for j in l:
            if j in i[0]:
                c += 1
        fin.append([i[0], c])

    res = [i[0] for i in sorted(fin, key=(lambda x: x[1]), reverse=True) if i[1] > 0]

    out = []
    for i in res:
        name = json.loads(i)[-2]
        author = json.loads(i)[-1]

        cursor.execute(
            f'select name, author, price, thumb from books where name = "{name}" and author = "{author}"'
        )
        t = cursor.fetchone()

        out.append(t)

    return out


def new():
    cursor.execute(
        "select name, author, price, thumb from books order by release_date desc"
    )

    l = cursor.fetchmany(10)

    return l


def new_home():
    cursor.execute(
        "select name, author, price, thumb from books order by release_date desc"
    )

    l = cursor.fetchmany(5)

    return l


def best():
    cursor.execute(
        "select b.name, b.author, b.price, b.thumb, count(c.cid) as cnt from books as b, copies as c where b.name = c.book and b.author = c.author and c.avail = 0 group by b.name order by cnt desc"
    )

    l = cursor.fetchmany(10)

    return l


def best_home():
    cursor.execute(
        "select b.name, b.author, b.price, b.thumb, count(c.cid) as cnt from books as b, copies as c where b.name = c.book and b.author = c.author and c.avail = 0 group by b.name order by cnt desc"
    )

    l = cursor.fetchmany(5)

    return l


def admin_auth(email, passwd):
    cursor.execute(
        f'select email, cast(passwd as char(60)) from admins where email = "{email}"'
    )
    l = cursor.fetchall()
    if len(l) > 0:
        if bcrypt.checkpw(passwd.encode("utf-8"), l[0][1].encode("utf-8")):
            return True

    return False


def add_admin(email, passwd):
    cursor.execute("select email from admins")

    l = cursor.fetchall()

    if (email,) not in l:
        hashed = str(bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt()))[2:-1]

        cursor.execute(
            f'insert into admins(email, passwd) values ("{email}","{hashed}")'
        )
        db.commit()
        return True
    else:
        return False


def list_books():
    cursor.execute(
        "select author, book, sum(avail) from copies group by (book) order by author;"
    )
    l = cursor.fetchall()

    return l


def add_book(
    name,
    author,
    qty,
    lang=None,
    tags=None,
    rel_date=None,
    series=None,
    series_sl_no=None,
    thumb=None,
    price=None,
    desc=None,
):
    cursor.execute("select name, author from books")
    l = cursor.fetchall()

    if (name, author) not in l:
        if all((lang, tags, rel_date, thumb, price, desc)):
            cursor.execute("select genre from genres")
            g = cursor.fetchall()
            for i in tags:
                if (i,) not in g:
                    cursor.execute(f'insert into genres (genre) values ("{i}")')

            j = json.dumps(tags)

            price = float(price)

            if series and series_sl_no:
                series_sl_no = int(series_sl_no)
            else:
                series_sl_no = None
                series = None

            thumb.thumbnail((600, 600))
            filename = secure_filename(name + "_" + author + ".png")
            thumb.save("." + url_for("static", filename=f"thumbs/{filename}"), "png")

            if series and series_sl_no:
                cursor.execute(
                    f'insert into books (name, author, lang, tags, series, series_sl_no, price, thumb, release_date, description) values ("{name}","{author}","{lang}",\'{j}\',"{series}",{series_sl_no},{price},"{filename}", "{rel_date}", "{desc}")'
                )
            else:
                cursor.execute(
                    f'insert into books (name, author, lang, tags, price, thumb, release_date, description) values ("{name}","{author}","{lang}",\'{j}\',{price},"{filename}", "{rel_date}", "{desc}")'
                )

            db.commit()
        else:
            return False

    for _ in range(int(qty)):
        cursor.execute("select cid from copies")
        l = cursor.fetchall()

        while True:
            cid = str(uuid4()).upper()[-5:]

            if (cid,) not in l:
                break

        cursor.execute(
            f'insert into copies (cid, book, author, avail) values ("{cid}", "{name}", "{author}", 1)'
        )

    db.commit()


def modify_book(
    name_old,
    author_old,
    name=None,
    author=None,
    lang=None,
    tags=None,
    release_date=None,
    series=None,
    series_sl_no=None,
    file=None,
    price=None,
    desc=None,
):
    cursor.execute("select name, author from books")
    l = cursor.fetchall()

    if (name_old, author_old) not in l:
        return False

    thumb = None
    n = name if name else name_old
    a = author if author else author_old
    if file:
        thumb = secure_filename(n + "_" + a + ".png")
        file.thumbnail((600, 600))
        file.save("." + url_for("static", filename=f"thumbs/{thumb}"), "png")

    if series_sl_no:
        series_sl_no = int(series_sl_no)

    if price:
        price = float(price)

    if tags:
        tags = json.dumps(tags)

    index = [
        "lang",
        "tags",
        "release_date",
        "series",
        "series_sl_no",
        "thumb",
        "price",
        "description",
    ]
    for x, i in enumerate(
        [lang, tags, release_date, series, series_sl_no, thumb, price, desc]
    ):
        if i:
            if i == "tags" or i == desc:
                cursor.execute(
                    f'update books set {index[x]} = "{i}" where name = "{name_old}" and author = "{author_old}"'
                )
            else:
                cursor.execute(
                    f'update books set {index[x]} = \'{i}\' where name = "{name_old}" and author = "{author_old}"'
                )

    db.commit()

    if name or author:
        cursor.execute(
            f'select cid, avail from copies where book = "{name_old}" and author = "{author_old}"'
        )
        l = cursor.fetchall()

        lis = []
        for i in l:
            if i[1] == 0:
                lis.append(i[0])

        tup = tuple(lis) if len(lis) > 0 else ("____", "____")

        cursor.execute(
            f"select sid, cid, user, date, address, exp_date, price from sales where cid in {tup}"
        )
        s = cursor.fetchall()

        for i in s:
            cursor.execute(f'delete from sales where sid = "{i[0]}"')

        for i in l:
            cursor.execute(f'delete from copies where cid = "{i[0]}"')

        if name:
            cursor.execute(
                f'update books set name = "{name}" where name = "{name_old}" and author = "{author_old}"'
            )

            db.commit()

            if author:
                cursor.execute(
                    f'update books set author = "{author}" where name = "{name}" and author = "{author_old}"'
                )
        else:
            cursor.execute(
                f'update books set author = "{author}" where name = "{name_old}" and author = "{author_old}"'
            )

        db.commit()

        if not name:
            name = name_old

        if not author:
            author = author_old

        for i in l:
            cursor.execute(
                f'insert into copies (cid, book, author, avail) values ("{i[0]}", "{name}", "{author}", {i[1]})'
            )

        for i in s:
            cursor.execute(
                f'insert into sales(sid, cid, user, date, address, exp_date, price) values ("{i[0]}", "{i[1]}", "{i[2]}", "{str(i[3])}", "{i[4]}", "{str(i[5])}", {i[6]})'
            )

        db.commit()

    return True


def list_admins():
    cursor.execute("select email from admins")
    l = cursor.fetchall()

    return l


def list_all_books():
    cursor.execute(
        "select b.*, sum(c.avail) from books as b, copies as c where b.name = c.book and b.author = c.author group by b.name order by b.author, b.release_date, b.name"
    )
    l = cursor.fetchall()

    return l


def book(name, author):
    cursor.execute(
        f'select b.*, sum(c.avail) from books as b, copies as c where b.name = c.book and b.author = c.author and b.name = "{name}" and b.author = "{author}"'
    )

    l = cursor.fetchone()

    if len(l) > 0:
        return l

    return False


def sale(name, author, user, addr, total, qty):
    try:
        for _ in range(qty):
            cursor.execute("select sid from sales order by sid")
            l = cursor.fetchall()

            if len(l) == 0:
                sid = "00001"
            else:
                last = int(l[-1][0])
                new = last + 1

                sid = "0" * (5 - len(str(new))) + str(new)

            cursor.execute(
                f'select cid from copies where book = "{name}" and author = "{author}" and avail = 1'
            )
            cid = cursor.fetchone()[0]

            cursor.execute(
                f'insert into sales (sid, cid, user, address, price) values ("{sid}", "{cid}", "{user}", "{addr}", {total})'
            )
            cursor.execute(f'update copies set avail = 0 where cid = "{cid}"')

    except:
        return False

    db.commit()

    return True


def profile(email):
    cursor.execute(f"select email, username, tags from user where email = '{email}'")

    l = cursor.fetchone()

    return l


def order_history(user):
    cursor.execute(
        f"select c.book, c.author, b.thumb, s.date, count(*), b.price, s.address, s.exp_date, s.price from copies as c, sales as s, books as b where c.cid = s.cid and c.book = b.name and c.author = b.author and s.user = '{user}' group by s.date order by s.date desc"
    )

    l = cursor.fetchall()

    return l


def exclusives():
    cursor.execute("select name, author, price, thumb from exclusives")

    l = cursor.fetchall()

    return l


connect()
