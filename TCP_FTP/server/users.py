'''所有FTP用户信息（用户名，密码）'''

users={
    'Frozen':'123321',
    'Jerry':'123321',
    'IzumiSagiri':123321,
}

def authenticate(uid,pwd):
    if uid in users.keys():
        if users[uid] == pwd:
            return True
        else:
            return False
    else: return False