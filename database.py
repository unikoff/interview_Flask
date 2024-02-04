class UserDB:
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.active = True

    def find_user(self, user_login):
        if self.exist_user(user_login):
            self.user = self.db.session.execute(self.db.select(self.table).
                                                filter_by(login=user_login)).scalar_one()
            return self

    def new_user(self, login, password):
        try:
            if self.exist_user(login):
                raise Exception
            user = self.table(login=login, password=password)
            self.db.session.add(user)
            self.db.session.flush()
            self.db.session.commit()
        except:
            return False
        return True

    def exist_user(self, user_login):
        return self.db.session.query(self.table).filter_by(login=user_login).first() is not None

    def update_data(self, login, password, new_login, new_password):
        try:
            user = self.find_user(login).user
            if user and user.password == password:
                    if new_login:
                        user.login = new_login
                    if new_password:
                        user.password = new_password
                    self.db.session.commit()
            else:
                raise Exception
        except:
            return False
        return True

    def delete(self, login, password):
        try:
            user = self.find_user(login).user
            if user and user.password == password:
                self.db.session.delete(user)
                self.db.session.commit()
            else:
                raise Exception
        except:
            return False
        return True

    def get_id(self):
        return self.user.id


class WalletDB:
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.active = True

    def find_wallet(self, wallet_id):
        if self.exist_wallet(wallet_id):
            self.wallet = self.db.session.execute(self.db.select(self.table).
                                                  filter_by(id=wallet_id)).scalar_one()
            return self

    def new_wallet(self, userID, address, net, value):
        try:
            wallet = self.table(userID=userID, address=address, net=net, value=value)
            self.db.session.add(wallet)
            self.db.session.flush()
            self.db.session.commit()
        except:
            return False
        return True

    def exist_wallet(self, wallet_id):
        return self.db.session.query(self.table).filter_by(id=wallet_id).first() is not None

    def sellect_all(self, userID):
        wallets = self.db.session.query(self.table).filter_by(userID=userID).all()
        return wallets

    def transfer(self, wallet1_id, wallet2_id, value, admin=False):
        try:
            if admin:
                wallet2 = self.find_wallet(wallet2_id).wallet
                wallet2.value = wallet2.value + value
                self.db.session.commit()
            else:
                wallet1 = self.find_wallet(wallet1_id).wallet
                wallet2 = self.find_wallet(wallet2_id).wallet
                wallet1.value = wallet1.value - value
                wallet2.value = wallet2.value + value
                self.db.session.commit()
        except:
            return False
        return True

