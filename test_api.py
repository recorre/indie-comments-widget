#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

BASE_URL = 'https://openapi.nocodebackend.com'
INSTANCE_ID = os.getenv('INSTANCE', '41300_teste')
API_KEY = os.getenv('NOCODEBACKEND_API_KEY')

HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

payload = {
    'email': 'test@example.com',
    'password_hash': '123456',
    'api_key': 'test_api_key_123',
    'plan_level': 'free',
    'is_supporter': 0,
    'name': 'Test User'
}

endpoint = f'{BASE_URL}/create/users?Instance={INSTANCE_ID}'
r = requests.post(endpoint, headers=HEADERS, json=payload)
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')