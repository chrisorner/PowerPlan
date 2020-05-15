from energyapp.extensions import db

class Newsletter(db.Model):
    __tablename__ = 'newsletter'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by their e-mail or username.

        :param identity: Email or username
        :type identity: str
        :return: User instance
        """
        return Newsletter.query.filter(
          (Newsletter.email == identity)).first()

    def __repr__(self):
        return '<User {}>'.format(self.email)