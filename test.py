from EHR import app
import unittest 
from unittest import mock 
from flask_testing import TestCase


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

    # test patientA trying to check patientB's documents
    # @mock.patch('flask_login.utils._get_user')
    def test_privacy(self):
        with self.client:
            # user = mock.MagicMock()
            response = self.client.post(
                '/login',
                data=dict(id='p', password='p'), follow_redirects=True)
            print(response.data)
        # self.assertIn(b'Unregistered', response.data)

    # test register

if __name__ == '__main__':
    unittest.main()
