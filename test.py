from EHR import app
import unittest 

class FlaskTestCases(unittest.TestCase):

    # test if flask was set up correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test login with correct credential
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(id='n',password='n'), follow_redirects=True) 
        self.assertIn(b'role', response.data)
    
    # test login with false credential
    def test_flase_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(id='hello',password='world'), follow_redirects=True)
        self.assertIn(b'Unregistered', response.data)

    # test login with empty credential 
    def test_empty_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/register',
            data=dict(role='nurse'), follow_redirects=True)
        print(response.data)
        # self.assertIn(b'Unregistered', response.data)

    # test register

if __name__ == '__main__':
    unittest.main()
