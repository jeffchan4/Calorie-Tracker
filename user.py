from flask_login import UserMixin

from db import get_db



class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        # cart= db.execute(
        #     "SELECT * FROM cart WHERE user_id = ?",(user_id,)
        # ).fetchone()
        
        if not user:
            return None
        
        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user
    @staticmethod
    def get_all_users():
        db = get_db()
        users = db.execute(
            "SELECT * FROM user "
        ).fetchall()
        return users

    @staticmethod
    def get_all_food():
        db = get_db()
        cursor = db.execute("SELECT * FROM food")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        # Convert rows to a list of dictionaries
        foods = [dict(zip(columns, row)) for row in rows]

        return foods

        
    def get_calendar(date):
        db = get_db()
        date_ = db.execute(
            "SELECT date FROM calendar WHERE date = ?", (date,)
        ).fetchone()
        
        if date_ is None:
            return None
        return date_[0]
    def get_cart(date, user_id):
        db = get_db()
        
        # Retrieve the cart_id for the given user_id
        cart_id = db.execute(
            "SELECT id FROM cart WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if cart_id:
            cart_id = cart_id[0]  # Extract the cart_id from the result

            # Fetch food items for the specified date and cart_id
            cart_ = db.execute(
                "SELECT name, serving, id FROM food "
                "WHERE date = ? AND cart_id = ?",
                (date, cart_id)
            ).fetchall()

            # Rest of your code to work with the 'cart_' result
            return cart_
        else:
            # Handle the case where no cart is found for the given user_id
            return None

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        try:
            db.execute(
                "INSERT INTO user (id, name, email, profile_pic)"
                " VALUES (?, ?, ?, ?)",
                (id_, name, email, profile_pic),
            )
            db.execute(
                "INSERT INTO cart (user_id)"
                "VALUES (?)",
                (id_,)
            )
            db.commit()
        except Exception as e:
            db.rollback()  # Roll back the transaction in case of an error
            raise e
    @staticmethod
    def create_calendar(date):
        db=get_db()
        db.execute(
            "INSERT INTO calendar (date)"
            "VALUES (?)",
            (date,)
        )
        db.commit()
        
    @staticmethod
    def insert(id_, food, serving,date):
        db=get_db()
        cart_id=db.execute(
            "SELECT id FROM cart WHERE user_id =?", (id_,)
        ).fetchone()
        if not cart_id:
            return None
        
        
        db.execute(
            "INSERT INTO food (name,serving,cart_id,date) "
            "VALUES (?,?,?,?)" ,
            (food,serving,cart_id[0],date)
        )
        db.commit()
        print('insert was successful')
    

    def calculate(start,end,user_id):
        db=get_db()
        cart_id = db.execute(
            "SELECT id FROM cart WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if cart_id:
            cart_id = cart_id[0] 
            food=db.execute(
                "SELECT date, name, serving FROM food WHERE date BETWEEN ? and ? and cart_id = ? ",
                (start,end, cart_id)
            ).fetchall()
            
        
            return food
        
    @staticmethod ##### specify user id
    def delete_food(foodid):
        db = get_db()
        db.execute("""
            DELETE FROM food
            WHERE ROWID IN (
                SELECT ROWID
                FROM food
                WHERE id = ?
                LIMIT 1
            )
        """, (foodid,))

        db.commit()  


