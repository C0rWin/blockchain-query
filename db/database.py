from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from db.model.cache import Base, Cache


class CacheManager:
    """
    CacheManager is a class that manages the cache database.
    """

    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        """
        session = self.session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def put(self, key, value, type):
        """
        Put a value to the cache database.

        Parameters:
        key (str): The key of the cache.
        value (str): The value of the cache.
        type (str): The type of the сached entry.

        Returns:
        None
        """
        with self.session_scope() as session:
            cache = Cache(key=key, value=value, type=type)
            session.add(cache)

    def get(self, key, type):
        """
        Get a value from the cache database.

        Parameters:
        key (str): The key of the cache.
        type (str): The type of the сached entry.

        Returns:
        str: The value of the cache
        """
        with self.session_scope() as session:
            cache = session.query(Cache).filter_by(key=key, type=type).first()
            if cache:
                return cache.value
            return None
