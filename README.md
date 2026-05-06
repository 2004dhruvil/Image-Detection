# Image Detection: Real vs Fake

A full-stack web application built with Flask that uses Machine Learning (HOG feature extraction + SVM) to detect whether an uploaded image is "Real" or "Fake". 

## Features

- **Image Classification:** Upload an image and get an instant prediction (Real or Fake) with a confidence score.
- **Machine Learning Integration:** Uses a pre-trained Support Vector Machine (SVM) model alongside Histogram of Oriented Gradients (HOG) for accurate image feature extraction.
- **User Authentication:** Secure registration and login system using `Flask-Login` and password hashing.
- **Math CAPTCHA & Bot Protection:** Simple math-based CAPTCHA on the login page to prevent automated bots.
- **Scan History:** Logged-in users can view their past image scans and predictions.
- **Admin Dashboard:** A dedicated admin panel to monitor total users, view all scan histories, and track overall application analytics.
- **Database Support:** Defaults to SQLite for easy setup, with built-in support to connect to MySQL via environment variables.

## Technologies Used

### Backend
- Python
- Flask
- Flask-SQLAlchemy (ORM)
- Flask-Login (Authentication)
- Werkzeug (Security & File handling)

### Machine Learning
- scikit-learn (SVM model & Scaler)
- OpenCV (Image processing)
- scikit-image (HOG feature extraction)
- NumPy & Joblib

### Frontend
- HTML5 / CSS3 / JavaScript
- Jinja2 Templating

## Prerequisites

Make sure you have the following installed on your system:
- [Python 3.8+](https://www.python.org/downloads/)
- `pip` (Python package installer)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/2004dhruvil/Image-Detection.git
   cd Image-Detection
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   Navigate to the `demo-1` folder (or wherever the `requirements.txt` is located) and install the required packages:
   ```bash
   cd demo-1
   pip install -r requirements.txt
   ```

4. **Environment Variables (Optional)**
   The application uses SQLite by default. If you want to use MySQL or change the Flask Secret Key, create a `.env` file in the same directory as `app.py`:
   ```env
   SECRET_KEY=your_secure_secret_key
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_NAME=image_detection_db
   ```

5. **Run the Application**
   ```bash
   cd demo-1
   python app.py
   ```
   *(Alternatively, you can double-click `run.bat` on Windows if you have it configured).*

6. **Access the App**
   Open your web browser and go to: `http://127.0.0.1:5000`

> **Note:** The first user to register will automatically be granted Admin privileges!

## Project Structure
```
Image-Detection/
│
├── demo-1/
│   ├── app.py                  # Main Flask application
│   ├── best_svm_model.pkl      # Pre-trained SVM model
│   ├── scaler.pkl              # Pre-trained scaler for model
│   ├── requirements.txt        # Python dependencies
│   ├── static/                 # CSS, JS, and image assets
│   ├── templates/              # HTML Jinja templates
│   ├── uploads/                # Directory for uploaded images
│   └── instance/               # SQLite database directory (auto-generated)
│
├── model.ipynb                 # Jupyter Notebook for model training/experimentation
├── post_training.py            # Script for post-training evaluations
└── .gitignore                  # Git ignore rules
```
