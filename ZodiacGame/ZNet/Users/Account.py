'''存放用户账号密码'''

users =\
{
    'Frozen':'123321',
    'Jerry':'123321',
    'Izumisagiri':'123321',
}

def Authenticate(account,password):
    '''Server校验使用'''
    global users
    if account not in users.keys():
        return False
    if password != users[account]:
        return False
    return True