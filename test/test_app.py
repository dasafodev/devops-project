from application import application, db
import unittest
import uuid
from flask import json

import sys
sys.path.insert(0, '..')


class ApplicationTestCase(unittest.TestCase):
    def setUp(self):
        application.config['TESTING'] = True
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = application.test_client()
        with application.app_context():
            db.create_all()

    def tearDown(self):
        with application.app_context():
            db.session.remove()
            db.drop_all()

    def test_health_check(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"status": "healthy"})

    def test_version(self):
        response = self.app.get('/version')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"version": "1.0.0"})

    def test_get_token(self):
        response = self.app.post('/get-token')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_add_to_blacklist(self):
        token_response = self.app.post('/get-token')
        token = token_response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'email': 'test@example.com',
            'app_uuid': str(uuid.uuid4()),
            'blocked_reason': 'Testing'
        }
        response = self.app.post('/blacklists', headers=headers,
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json, {'message': 'Email agregado a la lista negra exitosamente'})

    def test_check_blacklist(self):
        token_response = self.app.post('/get-token')
        token = token_response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'email': 'test@example.com',
            'app_uuid': str(uuid.uuid4()),
            'blocked_reason': 'Testing'
        }
        self.app.post('/blacklists', headers=headers,
                      data=json.dumps(data), content_type='application/json')
        response = self.app.get(
            '/blacklists/test@example.com', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {'is_blacklisted': True, 'reason': 'Testing'})

    def test_clear_blacklist(self):
        token_response = self.app.post('/get-token')
        token = token_response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'email': 'test@example.com',
            'app_uuid': str(uuid.uuid4()),
            'blocked_reason': 'Testing'
        }
        self.app.post('/blacklists', headers=headers,
                      data=json.dumps(data), content_type='application/json')
        response = self.app.delete('/clear-blacklist', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json, {'message': 'Lista negra limpiada exitosamente'})
        response = self.app.get(
            '/blacklists/test@example.com', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'is_blacklisted': False})


if __name__ == '__main__':
    unittest.main()
