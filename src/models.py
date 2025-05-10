from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    max_count = 3

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


    def __repr__(self):
        cols = []
        for id, num  in enumerate(self.__table__.columns.keys()):
            if id> self.max_count:
                break
            cols.append(f'{num}={getattr(self, num)}')

        return f'{self.__class__.__name__}({",".join(cols)})'
