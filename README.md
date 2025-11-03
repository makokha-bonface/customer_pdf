# customer_pdf
Secure, scalable PDF upload system leveraging Flask, MongoDB, and GridFS — with smart hash-based duplicate detection and customer-specific data isolation.

This project is a Python-based web application. It allows customer-specific PDF uploads with duplicate detection, storage in MongoDB using GridFS, text extraction, and basic analytics like sentiment analysis and keyword search. Built with Flask, it demonstrates scalable data handling and insights generation.

## Features
- **Customer-Specific Uploads**: Each customer has a dedicated MongoDB collection.
- **Duplicate Detection**: Uses MD5 hashing to prevent redundant uploads.
- **File Storage**: PDFs stored in GridFS for efficient handling of large files.
- **Text Extraction & Analytics**: Extracts text from PDFs and performs simple sentiment analysis using TextBlob.
- **Query Endpoint**: Analyze customer data with aggregations (e.g., average sentiment, keyword search).
- **Optional Frontend**: Basic HTML form for uploads.
- **Extensibility**: Inspired by Palantir's expertise in data pipelines—add auth, ML models, or integrations as needed.

## Prerequisites
- Python 3.10+
- MongoDB (local instance or Atlas)
- Git

## Setup Instructions
1. Clone the repository:
git clone https://github.com/YOUR_USERNAME/palantir-inspired-pdf-app.git
cd palantir-inspired-pdf-app
text2. Create and activate a virtual environment:
python -m venv venv
text- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
pip install -r requirements.txt
text4. Start MongoDB (if local):
- Ensure it's running on `mongodb://localhost:27017/`.

5. Run the application:
python app.py
text- Access at `http://localhost:5000/`.
- For uploads: POST to `/upload/<customer_id>` with form-data `file` (PDF).
- For analytics: GET to `/analyze/<customer_id>?keyword=<term>`.

## Testing
- Use tools like Postman or curl for API testing.
- Example upload (curl):
curl -X POST -F 'file=@/path/to/your.pdf' http://localhost:5000/upload/test_customer
text- Check MongoDB for stored data (use MongoDB Compass).

## Optional Enhancements
- **Frontend**: Serve `static/index.html` by adding routes in `app.py`.
- **Docker**: Build and run:
docker build -t pdf-app .
docker run -p 5000:5000 -d pdf-app
text- **Security**: Add authentication (e.g., Flask-Login) for production.

## Contributing
Feel free to fork and submit pull requests. Issues welcome!


Learning: Python, Flask, MongoDB, and data analytics.
