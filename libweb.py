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
"""

import urllib2
import logging

logging.basicConfig(level=logging.DEBUG)

POST_LOGIN_URL = "http://10.0.0.55/cgi-bin/do_login"


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
    
def login(username, password):
    assert username != None and password != None
    data = get_login_data(username, password)
    req = urllib2.Request(POST_LOGIN_URL, data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    f = urllib2.urlopen(req)

    for response_data in f:
        print response_data
        return response_data
        
def test_post_data():

    test_case = get_user_info()
    data = get_login_data(test_case['username'], test_case['password'])
    logging.debug("post_data: %s", data)
    assert data == test_case['result']
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
    test_post_data()
    test_login()
    
