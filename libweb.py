#!/bin/env python

import urllib2
import logging

logging.basicConfig(level=logging.DEBUG)

POST_URL = "http://10.0.0.55/cgi-bin/do_login"
TEST_USERNAME = 'lyi'
TEST_PASSWORD =  'jisuanji640'
TEST_RESULT = "username=lyi&password=4590ee10495f1f1e&drop=0&type=1&n=100"

"""
var pass1=hex_md5(pass);
var pass2=pass1.substr(8,16);

var drop=(document.form1.drop.value==1)?1:0;
var data="username="+uname+"&password="+pass2+"&drop="+drop+"&type=1&n=100";
var con=postData("/cgi-bin/do_login", "post", data);

"""

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
    req = urllib2.Request(POST_URL, data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    f = urllib2.urlopen(req)

    for response_data in f:
        print response_data
        return response_data
        
def test_post_data():

    test_case = {"username": TEST_USERNAME, "password": TEST_PASSWORD, "result": TEST_RESULT}
    data = get_login_data(test_case['username'], test_case['password'])
    loggging.debug("post_data: %s", data)
    assert data == test_case['result']
    print "PASS"
            
def test_login(username=TEST_USERNAME,password=TEST_PASSWORD):
    assert login(username, password).isdigit()
    assert login(username, "---wrong password---") == "password_error"
    assert login("wrong username", "--wrong password--") == "username_error"
    print "ALL PASS"
    
if __name__ == "__main__":
    #test_post_data()
    test_login()