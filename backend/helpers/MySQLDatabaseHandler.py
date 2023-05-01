import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MySQLDatabaseHandler(object):
    
    def __init__(self,MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE,MYSQL_HOST = "localhost"):
        self.IS_DOCKER = True if 'DB_NAME' in os.environ else False
        self.MYSQL_HOST = os.environ['DB_NAME'] if self.IS_DOCKER else MYSQL_HOST
        self.MYSQL_USER = "admin" if self.IS_DOCKER else MYSQL_USER
        self.MYSQL_USER_PASSWORD = "admin" if self.IS_DOCKER else MYSQL_USER_PASSWORD
        self.MYSQL_PORT = 3306 if self.IS_DOCKER else MYSQL_PORT
        self.MYSQL_DATABASE = MYSQL_DATABASE
        self.engine = self.validate_connection()

    def validate_connection(self):
        engine = db.create_engine(f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_USER_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}")
        # conn = engine.connect()
        # conn.execute(f"CREATE DATABASE IF NOT EXISTS {self.MYSQL_DATABASE}")
        # conn.execute(f"USE {self.MYSQL_DATABASE}")
        return engine

    def lease_connection(self):
        return self.engine.connect()
    
    def query_executor(self,query):
        conn = self.lease_connection()
        if type(query) == list:
            for i in query:
                conn.execute(i)
        else:
            conn.execute(query)

    def query_selector(self,query):
        conn = self.lease_connection()
        data = conn.execute(query)
        return data

    def load_file_into_db(self,file_path  = None):
        if self.IS_DOCKER:
            return
        if file_path is None:
            file_path = os.path.join(os.environ['ROOT_PATH'],'init.sql')
        sql_file = open(file_path,"r")
        sql_file_data = list(filter(lambda x:x != '',sql_file.read().split(";\n")))
        self.query_executor(sql_file_data)
        sql_file.close()


# MODELS START HERE
class Webtoon(db.Model):
    __tablename__ = "webtoons"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    webtoon_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    genre = db.Column(db.String(500), nullable=False)
    thumbnail = db.Column(db.String(1000), nullable=False)
    summary = db.Column(db.String(1000), nullable=False)
    episodes = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.String(1000), nullable=False)
    view = db.Column(db.Integer, nullable=False)
    subscribe = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(1000), nullable=False)
    released_date = db.Column(db.String(1000), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    cover = db.Column(db.String(1000), nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    written_by = db.Column(db.String(1000), nullable=False)
    art_by = db.Column(db.String(1000), nullable=False)
    adapted_by = db.Column(db.String(1000), nullable=False)
    original_work_by = db.Column(db.String(1000), nullable=False)
    assisted_by = db.Column(db.String(1000), nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes a Webtoon object
        """

        self.webtoon_id = kwargs.get(webtoon_id)
        self.title = kwargs.get(title)
        self.genre = kwargs.get(genre)
        self.thumbnail = kwargs.get(thumbnail)
        self.summary = kwargs.get(summary)
        self.episodes = kwargs.get(episodes)
        self.created_by = kwargs.get(created_by)
        self.view = kwargs.get(view)
        self.subscribe = kwargs.get(subscribe)
        self.grade = kwargs.get(grade)
        self.released_date = kwargs.get(released_date)
        self.url = kwargs.get(url)
        self.cover = kwargs.get(cover)
        self.likes = kwargs.get(likes)
        self.written_by = kwargs.get(written_by)
        self.art_by = kwargs.get(art_by)
        self.adapted_by = kwargs.get(adapted_by)
        self.original_work_by = kwargs.get(original_work_by)
        self.assisted_by = kwargs.get(assisted_by)

    def serialize(self):
        """
        Serializes a webtoon object 
        """

        return {
            "id": self.id,
            "webtoon_id": self.webtoon_id,
            "title": self.title,
            "genre": self.genre, 
            "thumbnail": self.thumbnail,
            "summary": self.summary, 
            "episodes": self.episodes, 
            "created_by": self.create_by, 
            "view": self.view, 
            "subscribe": self.subscribe, 
            "grade": self.grade,
            "released_date": self.released_date,
            "url": self.url, 
            "cover": self.cover, 
            "likes": self.likes,
            "written_by": self.written_by,
            "art_by": self.art_by, 
            "adapted_by": self.adapted_by, 
            "original_work_by": self.original_work_by,
            "assisted_by": self.assisted_by 
        }

    def simple_serialize(self):
        """
        Doesn't serialize everything
        """
        return {
            "id": self.id,
            "webtoon_id": self.webtoon_id,
            "title": self.title,
            "genre": self.genre,
            "thumbnail": self.thumbnail,
            "summary": self.summary
        }
    
    def likes_serialize(self):
        """
        Serializes a webtoon with a weighted average between likes value and views value for sorting purposes
        """
        return {
            "id": self.id,
            "webtoon_id": self.webtoon_id,
            "title": self.title,
            "genre": self.genre,
            "thumbnail": self.thumbnail,
            "summary": self.summary,
            "social": self.likes / self.view
        }



