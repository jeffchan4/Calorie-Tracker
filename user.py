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
    def get_calendar(date):
        db = get_db()
        date_ = db.execute(
            "SELECT date FROM calendar WHERE date = ?", (date,)
        ).fetchone()
        
        if date_ is None:
            return None
        return date_[0]


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
        
    @staticmethod
    def calculate(start,end):
        db=get_db()
        food=db.execute(
            "SELECT date, name, serving FROM food WHERE date BETWEEN ? and ? ",
            (start,end)
        ).fetchall()
        
        # food_list = []
        # for row in food:
        #     food_dict = {
        #         "date": row[0],
        #         "name": row[1],
        #         "serving": row[2]
        #     }
        #     food_list.append(food_dict)

        # return food_list
        return food