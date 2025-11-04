"""
Unit tests for Document Management API
"""

import pytest
import json
import io
from app import app, db, customers_collection, documents_collection
from bson.objectid import ObjectId


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def cleanup():
    """Cleanup test data after tests"""
    yield
    # Clean up test collections
    customers_collection.delete_many({'email': {'$regex': 'test@.*'}})
    documents_collection.delete_many({})


@pytest.fixture
def test_customer(client, cleanup):
    """Register a test customer and return API key"""
    response = client.post('/api/v1/customers/register',
                          json={'name': 'Test User', 'email': 'test@example.com'},
                          content_type='application/json')
    data = json.loads(response.data)
    return data['api_key']


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_customer_registration(client, cleanup):
    """Test customer registration"""
    response = client.post('/api/v1/customers/register',
                          json={'name': 'John Doe', 'email': 'test@newuser.com'},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'api_key' in data
    assert 'customer_id' in data
    assert len(data['api_key']) > 20


def test_duplicate_customer_registration(client, test_customer, cleanup):
    """Test duplicate customer registration is rejected"""
    response = client.post('/api/v1/customers/register',
                          json={'name': 'Test User', 'email': 'test@example.com'},
                          content_type='application/json')
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'already registered' in data['error'].lower()


def test_upload_document_without_api_key(client):
    """Test document upload without API key fails"""
    data = {'file': (io.BytesIO(b"test content"), 'test.pdf')}
    response = client.post('/api/v1/documents/upload', data=data)
    
    assert response.status_code == 401


def test_upload_document_success(client, test_customer):
    """Test successful document upload"""
    headers = {'X-API-Key': test_customer}
    data = {'file': (io.BytesIO(b"test pdf content"), 'test.pdf')}
    
    response = client.post('/api/v1/documents/upload',
                          data=data,
                          headers=headers,
                          content_type='multipart/form-data')
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert 'document_id' in response_data
    assert response_data['filename'] == 'test.pdf'


def test_upload_duplicate_document(client, test_customer):
    """Test duplicate document detection"""
    headers = {'X-API-Key': test_customer}
    data = {'file': (io.BytesIO(b"duplicate content"), 'dup.pdf')}
    
    # First upload
    response1 = client.post('/api/v1/documents/upload',
                           data=data,
                           headers=headers,
                           content_type='multipart/form-data')
    assert response1.status_code == 201
    
    # Duplicate upload
    data = {'file': (io.BytesIO(b"duplicate content"), 'dup2.pdf')}
    response2 = client.post('/api/v1/documents/upload',
                           data=data,
                           headers=headers,
                           content_type='multipart/form-data')
    
    assert response2.status_code == 409
    response_data = json.loads(response2.data)
    assert 'duplicate' in response_data['message'].lower()


def test_upload_invalid_file_type(client, test_customer):
    """Test upload with invalid file type"""
    headers = {'X-API-Key': test_customer}
    data = {'file': (io.BytesIO(b"test content"), 'test.exe')}
    
    response = client.post('/api/v1/documents/upload',
                          data=data,
                          headers=headers,
                          content_type='multipart/form-data')
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'not allowed' in response_data['error'].lower()


def test_list_documents(client, test_customer):
    """Test listing documents"""
    headers = {'X-API-Key': test_customer}
    
    # Upload a document first
    data = {'file': (io.BytesIO(b"list test content"), 'list.pdf')}
    client.post('/api/v1/documents/upload',
               data=data,
               headers=headers,
               content_type='multipart/form-data')
    
    # List documents
    response = client.get('/api/v1/documents', headers=headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'documents' in response_data
    assert len(response_data['documents']) >= 1
    assert 'total' in response_data


def test_list_documents_pagination(client, test_customer):
    """Test document listing with pagination"""
    headers = {'X-API-Key': test_customer}
    
    response = client.get('/api/v1/documents?page=1&per_page=5', headers=headers)
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['page'] == 1
    assert response_data['per_page'] == 5


def test_get_document_not_found(client, test_customer):
    """Test getting non-existent document"""
    headers = {'X-API-Key': test_customer}
    fake_id = str(ObjectId())
    
    response = client.get(f'/api/v1/documents/{fake_id}', headers=headers)
    
    assert response.status_code == 404


def test_delete_document(client, test_customer):
    """Test document deletion"""
    headers = {'X-API-Key': test_customer}
    
    # Upload a document
    data = {'file': (io.BytesIO(b"delete test content"), 'delete.pdf')}
    upload_response = client.post('/api/v1/documents/upload',
                                 data=data,
                                 headers=headers,
                                 content_type='multipart/form-data')
    
    document_id = json.loads(upload_response.data)['document_id']
    
    # Delete the document
    delete_response = client.delete(f'/api/v1/documents/{document_id}', headers=headers)
    
    assert delete_response.status_code == 200
    response_data = json.loads(delete_response.data)
    assert 'deleted successfully' in response_data['message'].lower()


def test_rate_limiting(client, test_customer):
    """Test that rate limiting is configured"""
    # This test just verifies the endpoint exists with rate limiting
    # Actual rate limit testing would require many requests
    headers = {'X-API-Key': test_customer}
    response = client.get('/api/v1/documents', headers=headers)
    
    # Should not hit rate limit on first request
    assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])