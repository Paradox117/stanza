from flask import Blueprint, render_template, request, session, redirect
import db_actions
import json
from PIL import Image
import datetime
import random


views = Blueprint(__name__, "views")


def title(s: str):
    o = []
    for i in s.split():
        r = []
        for j in i.split("."):
            r.append(j.capitalize())
        o.append(".".join(r))

    return " ".join(o)


@views.context_processor
def context_processor():
    return dict(title=title, round=format)


@views.route("/")
def home():
    db_actions.connect()

    new = db_actions.new_home()

    best = db_actions.best_home()

    if "user" in session:
        recomend = db_actions.recomend(session["user"])
    else:
        recomend = db_actions.select_random()

    db_actions.disconnect()
    return render_template(
        "index.html", recomend=recomend, name="Home", new=new, best=best
    )


@views.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        session.pop("user")
        session.pop("pic")

    if request.method == "POST":
        email = request.form["email"]
        passwd = request.form["passwd"]

        if "remember" in request.form:
            session.permanent = True
        else:
            session.permanent = False

        db_actions.connect()
        x = db_actions.user_auth(email, passwd)
        db_actions.disconnect()

        if x:
            session["user"] = email
            session["pic"] = x

            if "next" in request.url:
                return redirect(request.args.get("next"))

            return redirect("/")
        else:
            return render_template(
                "login.html", msg="Email or Password not valid", name="Login"
            )
    return render_template("login.html", name="Login")


@views.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
        session.pop("pic")
    return redirect("/")


@views.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        session.pop("user")

    db_actions.connect()
    genres = db_actions.all_genres()
    db_actions.disconnect()

    if request.method == "POST":
        email = request.form["email"]
        user = request.form["user"]
        passwd = request.form["passwd"]
        re_passwd = request.form["re-passwd"]
        prof = request.files["prof"]

        img = None
        if prof.filename != "":
            img = Image.open(prof)

        tags = json.dumps([i for i in request.form if i.isupper()])

        if passwd == re_passwd:
            db_actions.connect()
            x = db_actions.add_user(email, user, passwd, tags, img)
            db_actions.disconnect()

            if x:
                return redirect("/login")

            return render_template(
                "register.html",
                genres=genres,
                msg="Account already exists",
                name="Register",
            )
        else:
            return render_template(
                "register.html",
                genres=genres,
                msg="Passwords do not match",
                name="Register",
            )

    return render_template(
        "register.html", genres=genres, msg="placeholder", name="Register"
    )


@views.route("/profile")
def profile():
    if "user" not in session:
        return redirect(f"/login?next={request.url}")

    db_actions.connect()
    data = db_actions.profile(session["user"])
    orders = db_actions.order_history(session["user"])
    db_actions.disconnect()

    data = list(data)
    data[2] = ", ".join(json.loads(data[2])).title()

    for x, i in enumerate(orders):
        date = i[3]
        exp_date = i[7]

        dif = datetime.datetime.now() - date

        per = dif / (exp_date - date)

        if per > 1:
            per = 1

        orders[x] += (per * 100,)

    return render_template(
        "profile.html", name=f"{data[1].title()}'s Profile", data=data, orders=orders
    )


@views.route("/authors")
def authors():
    db_actions.connect()
    a = db_actions.authors()
    db_actions.disconnect()

    return render_template("alpha_list.html", name="Authors", a=a)


@views.route("/authors/<a>")
def author(a):
    auth = a.upper().replace("+", " ")

    db_actions.connect()
    l = db_actions.author(auth)
    db_actions.disconnect()

    if l:
        return render_template("card_list.html", name=auth.title(), data=l)

    return render_template("404.html", name=404), 404


@views.route("/genres")
def genres():
    db_actions.connect()
    g = db_actions.genre_list()
    db_actions.disconnect()

    return render_template("alpha_list.html", name="Genres", a=g)


@views.route("/genres/<g>")
def genre(g):
    gen = g.upper().replace("-", " ").replace('+', '-')

    db_actions.connect()
    l = db_actions.genre(gen)
    db_actions.disconnect()

    if l:
        return render_template("card_list.html", name=gen.title(), data=l)

    return render_template("404.html", name=404), 404


@views.route("/series")
def series_list():
    db_actions.connect()
    s = db_actions.series_list()
    db_actions.disconnect()

    return render_template("alpha_list.html", name="Series", a=s)


@views.route("/series/<s>")
def series(s):
    ser = s.upper().replace("+", " ")

    db_actions.connect()
    l = db_actions.series(ser)
    db_actions.disconnect()

    if l:
        return render_template("card_list.html", name=ser.title(), data=l)

    return render_template("404.html", name=404), 404


@views.route("/best")
def best_sellers():
    db_actions.connect()
    l = db_actions.best()
    db_actions.disconnect()

    return render_template("card_list.html", name="Best Sellers", data=l)


@views.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = (
            request.form["query"]
            .lower()
            .replace(" ", "+")
            .removeprefix(" ")
            .removesuffix(" ")
        )

        return redirect(f"/search/{query}")

    return render_template("search.html", name="Search")


@views.route("/search/<query>", methods=["GET", "POST"])
def search_results(query):
    db_actions.connect()
    l = db_actions.search(n := query.replace("+", " "))
    db_actions.disconnect()

    if request.method == "POST":
        q = (
            request.form["search"]
            .lower()
            .replace(" ", "+")
            .removeprefix(" ")
            .removesuffix(" ")
        )

        return redirect(f"/search/{q}")

    return render_template("search_results.html", name=n, data=l, len=len)


@views.route("/new")
def new():
    db_actions.connect()
    l = db_actions.new()
    db_actions.disconnect()

    return render_template("card_list.html", name="New Releases", data=l)


@views.route("/book/<b>")
def book(b):
    name, author = [" ".join(i.split("_")) for i in b.upper().split("+")]

    if name == "URANIUM 235" and author == "JESSE RUSSELL":
        return redirect("https://www.youtube.com/watch?v=uYPbbksJxIg")

    if name == "THERE IS NOTHING WE CAN DO" and author == "NEPOLEON BONAPARTE":
        return redirect("https://youtu.be/b_fHC2TT4xY?si=WIrH7dMhQu1ATTlj")
    
    if name == "MY JOURNEYS ON A VELOCIRAPTOR" and author == "JESUS CHRIST":
        l = ['MY JOURNEYS ON A VELOCIRAPTOR', 'JESUS CHRIST', 'ENGLISH', '["MEME", "EGG"]', None, None, 666.0, 'jesus.jpeg', datetime.date(2023, 11, 7), "Amidst the age of dinosaurs, in a land untouched by modern civilization, Jesus Christ's footsteps take an unexpected turn. Discover a tale of wonder and connection as he shares an incredible journey with a Velociraptor, a creature both fierce and captivating. Together, they'll navigate the primordial world, facing perils and forging an extraordinary friendship that transcends the boundaries of time and existence. Join them in a story of faith, courage, and the eternal bond between man and beast, woven into the fabric of history itself.",0]
    else:

        db_actions.connect()
        l = db_actions.book(name, author)
        db_actions.disconnect()


    l = list(l)
    l[8] = str(l[8])
    l[3] = ", ".join(json.loads(l[3]))

    return render_template(
        "book.html", name=f"{name.title()} - {author.title()}", data=l
    )


@views.route("/checkout/<b>", methods=["GET", "POST"])
def checkout(b):
    if "user" not in session:
        return redirect(f"/login?next={request.url}")

    name, author = [" ".join(i.split("_")) for i in b.upper().split("|")]

    if request.method == "POST":
        qty = request.form["qty"]
        addr = request.form["addr"]
        total = request.form["total"]

        db_actions.connect()
        x = db_actions.sale(name, author, session["user"], addr, total, int(qty))
        db_actions.disconnect()

        if x:
            return render_template("order_success.html", name="Order Placed")

        return render_template("order_failed.html", name="Order Failed")

    db_actions.connect()
    l = db_actions.book(name, author)
    db_actions.disconnect()

    delivery = float(random.randint(120, 150))
    discount = random.randint(5, 10)

    exp_date = datetime.datetime.now() + datetime.timedelta(days=3)

    l = list(l)
    l[8] = str(l[8])
    l[3] = ", ".join(json.loads(l[3]))

    return render_template("checkout.html", name="Checkout", data=l, charges=(delivery, discount), exp_date=exp_date)


@views.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin/login")

    return render_template("admin.html", name="Admin")


@views.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "admin" in session:
        session.pop("admin")

    if request.method == "POST":
        email = request.form["email"]
        passwd = request.form["passwd"]

        if "remember" in request.form:
            session.permanent = True
        else:
            session.permanent = False

        db_actions.connect()
        x = db_actions.user_auth(email, passwd)
        db_actions.disconnect()

        if x:
            session["admin"] = email

            if "next" in request.url:
                return redirect(request.args.get("next"))

            return redirect("/admin")
        else:
            return render_template(
                "login.html", msg="Email or Password not valid", name="Admin Login"
            )

    return render_template("login.html", name="Admin Login")


@views.route("/admin/logout")
def admin_logout():
    if "admin" in session:
        session.pop("admin")

    return redirect("/")


@views.route("/admin/add-book", methods=["GET", "POST"])
def add_book():
    if "admin" not in session:
        return redirect("/admin/login?next=/admin/add-book")

    if request.method == "POST":
        name = request.form["name"].upper()
        author = request.form["author"].upper()
        lang = request.form["lang"].upper()
        tags = request.form["tags"].upper().replace(" ", "").split(",")
        rel_date = request.form["rel_date"]
        series = request.form["series"].upper()
        series_sl_no = request.form["series_sl_no"]
        price = request.form["price"]
        qty = request.form["qty"]
        thumb = request.files["thumb"]
        desc = request.form["desc"]

        img = None

        if thumb.filename:
            img = Image.open(thumb)

        db_actions.connect()
        db_actions.add_book(
            name, author, qty, lang, tags, rel_date, series, series_sl_no, img, price, desc
        )
        db_actions.disconnect()

        return redirect("/admin/add-book")

    db_actions.connect()
    l = db_actions.list_books()
    db_actions.disconnect()

    return render_template("add-book.html", name="Add Book", data=l, title=title)


@views.route("/admin/modify-book", methods=["GET", "POST"])
def modify_book():
    if "admin" not in session:
        return redirect("/admin/login?next=/admin/modify-book")

    if request.method == "POST":
        name_old = request.form["name-old"].upper()
        name = request.form["name-new"].upper()
        author_old = request.form["author-old"].upper()
        author = request.form["author-new"].upper()
        lang = request.form["lang"].upper()
        tags = request.form["tags"].upper().replace(" ", "").split(",")
        rel_date = request.form["rel_date"]
        series = request.form["series"].upper()
        series_sl_no = request.form["series_sl_no"]
        price = request.form["price"]
        thumb = request.files["thumb"]
        desc = request.form["desc"]

        if tags == [""]:
            tags = None

        img = None

        if thumb.filename:
            img = Image.open(thumb)

        db_actions.connect()
        db_actions.modify_book(
            name_old,
            author_old,
            name,
            author,
            lang,
            tags,
            rel_date,
            series,
            series_sl_no,
            img,
            price,
            desc
        )
        db_actions.disconnect()

        return redirect("/admin/modify-book")

    db_actions.connect()
    l = db_actions.list_books()
    db_actions.disconnect()

    return render_template("add-book.html", name="Modify Book", data=l, title=title)


@views.route("/admin/add-admin", methods=["POST", "GET"])
def add_admin():
    if "admin" not in session:
        return redirect("/admin/login?next=/admin/add-admin")

    db_actions.connect()
    l = db_actions.list_admins()
    db_actions.disconnect()

    if request.method == "POST":
        email = request.form["email"]
        passwd = request.form["passwd"]
        re_passwd = request.form["re-passwd"]

        if passwd == re_passwd:
            db_actions.connect()
            x = db_actions.add_admin(email, passwd)
            db_actions.disconnect()
            if x:
                return redirect("/admin/add-admin")
            else:
                return render_template(
                    "add_admin.html",
                    name="Add Admin",
                    data=l,
                    msg="Account already exists",
                )
        else:
            return render_template(
                "add_admin.html", name="Add Admin", data=l, msg="Passwords do not match"
            )

    return render_template("add_admin.html", name="Add Admin", data=l)


@views.route("/admin/list-books")
def list_books():
    if "admin" not in session:
        return redirect("/admin/login?next=/admin/list-books")

    db_actions.connect()
    data = db_actions.list_all_books()
    db_actions.disconnect()

    lis = []
    for i in data:
        i = list(i)
        i[8] = str(i[8])
        i[3] = ", ".join(json.loads(i[3]))
        lis.append(i)

    return render_template("list_books.html", name="Book List", data=lis, title=title)






@views.route("/eggs/zinnia")
def zinnia_egg():
    return render_template("zinnia.html", name="A Messege from the Magician")

@views.route("/eggs/trisha")
def trisha_egg():
    return render_template("trisha.html", name="Random Facts about Books")

@views.route("/eggs/naireet")
def naireet_egg():
    db_actions.connect()
    l = db_actions.exclusives()
    db_actions.disconnect()

    return render_template('card_list.html', name="Naireet's Exclusives", data=l)

@views.route("/eggs/suchitrak")
def suchitrak_egg():
    return render_template("suchitrak.html", name="Encrypted")

@views.route("/eggs/ayushmaan")
def ayushmaan():
    return render_template("ayushmaan.html", name="Thoughts")


@views.route("/eggs/abhinaba", methods=["GET","POST"])
def inte():
    if request.method=="POST":
        a=request.form["ans"]
        if int(a)==42:
            return redirect("/book/the_hitchhiker's_guide_to_the_galaxy+douglas_adams")
    return render_template("abhinaba.html", name="lol")






@views.route("/asdjfihnndfsfghdg")
def nsfw():
    return render_template("something.html", name="nsfw")