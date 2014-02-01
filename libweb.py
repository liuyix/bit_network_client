#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
网页版中的javascript登陆代码如下：
var pass1=hex_md5(pass);
var pass2=pass1.substr(8,16);

var drop=(document.form1.drop.value==1)?1:0;
var data="username="+uname+"&password="+pass2+"&drop="+drop+"&type=1&n=100";
var con=postData("/cgi-bin/do_login", "post", data);

Note: 由于目前不再区分流量，因此drop是1/0都无影响

Keeplive:
# 系统会返回一行数据
# 76,383542,35887,17851581966,2148418034,155989,0,lyi
# 解析
# 上网时间 76seconds
# 入流量 383542Bytes
# 出流量 35887Bytes
# 可用总流量 17851581966 Byte
# 总流量 2148418034
# unknown: （每次登录都不同,但是在登录期间不会改变) 155989
# unknown: 0 (type ?教师和学生都是0)
# username: lyi ()

"""

import urllib2
import logging

logging.basicConfig(level=logging.DEBUG)

LOGIN_INFO_KEYS = ["time", "in", "out", "available_data", "max_data", "unknown1", "unknown2", "username"]

POST_LOGIN_URL = "http://10.0.0.55/cgi-bin/do_login"
POST_LOGOUT_URL = "http://10.0.0.55/cgi-bin/do_logout"
POST_FORCE_LOGOUT_URL = "http://10.0.0.55/cgi-bin/force_logout"
POST_KEEP_LIVE = "http://10.0.0.55/cgi-bin/keeplive"
SHOWINFO_URL = "http://10.0.0.55/user_info.php?"

LOGIN_SESSIONID = ""
# 若要测试，需要将个人的用户名和密码以及post数据中md5加密后的密码串放入.user_info中
def get_user_info(filename=".user_info"):
    info_list = []
    with open(filename) as fobj:
        info_list = [ d.strip() for d in fobj]
        assert len(info_list) >= 3
        logging.debug("username: %s | password: %s | password_phase2: %s\n", info_list[0], info_list[1], info_list[2])
        result = "username=%s&password=%s&drop=0&type=1&n=100" %(info_list[0], info_list[2])
        return {"username": info_list[0], "password": info_list[1], "result": result}
    return None

def get_login_data(username, passwd):
    assert username != None and passwd != None
    import md5
    passwd_md5 = md5.new(passwd).hexdigest()
    logging.info("passwd hex: %s", passwd_md5)
    passwd_phase2 = passwd_md5[8:8+16]
    post_data = "username=%(username)s&password=%(password)s&drop=0&type=1&n=100" % {"username": username, "password": passwd_phase2}
    logging.info("post_data: %s", post_data)
    return post_data

def do_post(url, data, timeout=5):
    assert url != None
    request = urllib2.Request(url, data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        response_file = urllib2.urlopen(request, timeout=timeout)
    except urllib2.URLError as err:
        print "URLError: %s" % err
        return None
    else:
        return response_file

def login(username, password):
    assert username != None and password != None
    data = get_login_data(username, password)
    f = do_post(POST_LOGIN_URL, data)
    if f == None:
        # bad things happened
        logging.error("login failed!")
        return None
    for response_data in f:
        print response_data
        if response_data.isdigit(): # login success
            global LOGIN_SESSIONID
            LOGIN_SESSIONID = response_data
            logging.info("login success, session id: %s" % (LOGIN_SESSIONID ))
        return response_data

def do_force_logout(username, password):
    assert username != None and password != None
    flogout_post_data = "username=%(username)s&password=%(password)s&drop=0&n=1" % {'username': username, 'password': password}
    response = do_post(POST_FORCE_LOGOUT_URL, flogout_post_data)
    for data in response:
        return data
    pass

def logout(username, password, force=False):
    if force:
        return do_force_logout(username, password)
    else:
        if LOGIN_SESSIONID != None and LOGIN_SESSIONID != "":
            logout_post_data = "uid=%s" % (LOGIN_SESSIONID)
            response = do_post(POST_LOGOUT_URL, logout_post_data)
            for data in response:
                return data
        else:
            logging.error("SESSION ID is invalid!")
            return None

def parse_login_info(data):
    logging.debug(data)
    assert data != None
    items = data.strip().split(",")
    if len(items) == len(LOGIN_INFO_KEYS):
        login_info = dict(zip(LOGIN_INFO_KEYS, items))
        for k,v in login_info.iteritems():
            print k,": ",v
    else:
        logging.warn("login info mismatch, [data] = [%s], length: %d", str(data), len(items))
        print "login info mismatch"
        for item in items:
            print item
    
def keep_alive(sessionid=None):
    sid = sessionid
    if sid == None and LOGIN_SESSIONID != '':
        sid = LOGIN_SESSIONID
    if sid != None:
        keeplive_data = "uid=%s" % (sid)
        response_file = do_post(POST_KEEP_LIVE, keeplive_data)
        for data in response_file:
            print data
            parse_login_info(data)
            
    else:
        logging.error("session id is not valid!")

def show_userinfo(sessionid=None):
    sid = sessionid
    if sid == None and LOGIN_SESSIONID != '':
        sid = LOGIN_SESSIONID
    if sid != None:
        uid = "uid=%s" % (sid)
        #response_file = do_post(POST_SHOW_INFO, postdata)
        res = urllib2.urlopen(SHOWINFO_URL + uid)
        # 需要注意返回网页的编码 gb18030
        for data in res:
            print data.decode("gb18030")
            print '---'
            
def test_parse_login_info():
    test = "9149,221259023,10848348,17845117399,2187307845,169788,0,lyi"
    parse_login_info(test)
    test2 = "9123,1234"
    parse_login_info(test2)
            
def test_show_userinfo():
    user_info = get_user_info()
    return_data = login(user_info['username'], user_info['password'])
    if return_data.isdigit():
        show_userinfo()
            
def test_keep_alive():
    user_info = get_user_info()
    return_data = login(user_info['username'], user_info['password'])
    if return_data.isdigit():
        keep_alive()
    
def test_force_logout():
    user_info = get_user_info()
    data = logout(user_info['username'], user_info['password'], force=True)
    print data
    
def test_logout():
    user_info = get_user_info()
    return_data = login(user_info['username'],user_info['password'])
    if return_data.isdigit():
        logout_status = logout(user_info['username'], user_info['password'], force=False)
        print logout_status
    

def test_post_data():
    user_info = get_user_info()
    data = get_login_data(user_info['username'], user_info['password'])
    logging.debug("post_data: %s", data)
    assert data == user_info['result']
    print "PASS"
            
def test_login():
    user_info = get_user_info()
    username = user_info['username']
    password = user_info['password']
    assert login(username, password).isdigit()
    assert login(username, "---wrong password---") == "password_error"
    assert login("wrong username", "--wrong password--") == "username_error"
    print "ALL PASS"
    
if __name__ == "__main__":
    #test_post_data()
    test_login()
    #test_logout()
    #test_force_logout()
    #test_keep_alive()
    #test_show_userinfo()
    #test_parse_login_info()
