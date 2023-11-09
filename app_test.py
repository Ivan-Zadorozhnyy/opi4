from flask_testing import TestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver  # Import for type hinting
import unittest
from app import app, users_data
import json
from selenium.webdriver.chrome.options import Options


# Unit Tests
class FlaskTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_total_time_valid_user(self):
        user_id = users_data['data'][0]['userId']
        response = self.client.get(f'/api/stats/user/total?userId={user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('totalTime', response.json)

    def test_total_time_invalid_user(self):
        response = self.client.get('/api/stats/user/total?userId=nonexistent-id')
        self.assertEqual(response.status_code, 404)

    def test_average_time_valid_user(self):
        user_id = users_data['data'][0]['userId']
        response = self.client.get(f'/api/stats/user/average?userId={user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('dailyAverage', response.json)
        self.assertIn('weeklyAverage', response.json)

    def test_forget_valid_user(self):
        user_id = users_data['data'][0]['userId']
        response = self.client.post(f'/api/user/forget?userId={user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(user_id, [user['userId'] for user in users_data['data']])

    def test_forget_already_deleted_user(self):
        user_id = "some_deleted_id"
        response = self.client.post(f'/api/user/forget?userId={user_id}')
        self.assertEqual(response.status_code, 404)

    def test_get_user_ids(self):
        response = self.client.get('/api/users/ids')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))
        for user_id in response.json:
            self.assertTrue(any(user['userId'] == user_id for user in users_data['data']))


# E2E Tests
class FlaskE2ETestCase(unittest.TestCase):
    driver: WebDriver  # Type hint for the driver

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Ensure the WebDriver executable is in your PATH or specify the executable path.
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    def test_total_time_e2e(self):
        self.driver.get('http://127.0.0.1:5000/api/stats/user/total?userId=044fea9b-822a-4f44-832b-1808719277b2')
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        response_data = json.loads(body_text)
        self.assertIn('totalTime', response_data)
        self.assertIsInstance(response_data['totalTime'], int)
        self.assertGreaterEqual(response_data['totalTime'], 0)

    def test_average_time_e2e(self):
        self.driver.get('http://127.0.0.1:5000/api/stats/user/average?userId=044fea9b-822a-4f44-832b-1808719277b2')
        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
        response_data = json.loads(body_text)
        self.assertIn('dailyAverage', response_data)
        self.assertIn('weeklyAverage', response_data)
        self.assertIsInstance(response_data['dailyAverage'], int)
        self.assertGreaterEqual(response_data['dailyAverage'], 0)
        self.assertIsInstance(response_data['weeklyAverage'], int)
        self.assertGreaterEqual(response_data['weeklyAverage'], 0)

    def test_forget_user_e2e(self):
        self.driver.get('http://127.0.0.1:5000/api/users/ids')
        initial_user_ids_json = self.driver.find_element(By.TAG_NAME, 'body').text
        initial_user_ids = json.loads(initial_user_ids_json)
        user_id_to_forget = initial_user_ids[0]
        self.driver.get(f'http://127.0.0.1:5000/api/user/forget?userId={user_id_to_forget}')
        response_body = self.driver.find_element(By.TAG_NAME, 'body').text
        self.assertIn(user_id_to_forget, response_body)
        self.driver.get('http://127.0.0.1:5000/api/users/ids')
        updated_user_ids_json = self.driver.find_element(By.TAG_NAME, 'body').text
        updated_user_ids = json.loads(updated_user_ids_json)
        self.assertNotIn(user_id_to_forget, updated_user_ids)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()
