"""
test_auth.py - Integration Test Suite for Authentication & Officer Management
=============================================================================
Smart ANPR Vehicle Verification System
"""

import unittest
import json
from app import create_app
from database import get_db_connection

class AuthTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_login_missing_fields(self):
        """Verify login rejects missing username or password."""
        res = self.client.post('/api/auth/login', json={})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn('error', data)

    def test_02_login_invalid_credentials(self):
        """Verify login rejects invalid credentials with 401."""
        res = self.client.post('/api/auth/login', json={
            'username': 'officer',
            'password': 'WrongPassword999'
        })
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertIn('Invalid', data.get('error', ''))

    def test_03_login_valid_officer(self):
        """Verify login succeeds for default officer with token and profile."""
        res = self.client.post('/api/auth/login', json={
            'username': 'officer',
            'password': 'Officer@123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('token', data)
        self.assertIn('officer', data)
        officer = data['officer']
        self.assertEqual(officer['username'], 'officer')
        self.assertEqual(officer['role'], 'OFFICER')
        self.assertNotIn('password_hash', officer)

    def test_04_login_valid_admin(self):
        """Verify login succeeds for default administrator."""
        res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['officer']['role'], 'ADMIN')

    def test_05_auth_me_without_token(self):
        """Verify GET /api/auth/me returns 401 when token is missing."""
        res = self.client.get('/api/auth/me')
        self.assertEqual(res.status_code, 401)

    def test_06_auth_me_with_valid_token(self):
        """Verify GET /api/auth/me returns authenticated officer profile."""
        login_res = self.client.post('/api/auth/login', json={
            'username': 'officer',
            'password': 'Officer@123'
        })
        token = login_res.get_json()['token']

        res = self.client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['officer']['username'], 'officer')

    def test_07_officer_cannot_access_officer_roster(self):
        """Verify an OFFICER role cannot access GET /api/auth/officers (403 Forbidden)."""
        login_res = self.client.post('/api/auth/login', json={
            'username': 'officer',
            'password': 'Officer@123'
        })
        token = login_res.get_json()['token']

        res = self.client.get('/api/auth/officers', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 403)

    def test_08_admin_can_access_officer_roster(self):
        """Verify an ADMIN role can access GET /api/auth/officers (200 OK)."""
        login_res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        token = login_res.get_json()['token']

        res = self.client.get('/api/auth/officers', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(len(data.get('officers', [])), 3)

    def test_09_admin_can_create_new_officer(self):
        """Verify an ADMIN can register a new officer."""
        login_res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        token = login_res.get_json()['token']

        # Use unique timestamped badge and username
        import time
        ts = int(time.time())
        new_user = f"patrol_{ts}"

        res = self.client.post('/api/auth/officers', headers={'Authorization': f'Bearer {token}'}, json={
            'username': new_user,
            'password': 'Password@123',
            'full_name': 'Sub-Insp. Rakesh Verma',
            'badge_number': f'TP-DEL-{ts % 10000:04d}',
            'station': 'SEC-04-EXPRESSWAY',
            'role': 'OFFICER'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['officer']['username'], new_user)

    def test_10_duplicate_officer_fails(self):
        """Verify registering duplicate username returns 409 Conflict."""
        login_res = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        token = login_res.get_json()['token']

        res = self.client.post('/api/auth/officers', headers={'Authorization': f'Bearer {token}'}, json={
            'username': 'admin',
            'password': 'Password@123',
            'full_name': 'Duplicate Admin',
            'badge_number': 'ADMIN-DUP',
            'role': 'ADMIN'
        })
        self.assertEqual(res.status_code, 409)

if __name__ == '__main__':
    unittest.main(verbosity=2)
