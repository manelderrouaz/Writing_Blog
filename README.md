# Writing_Blog
# Django Blog API

A comprehensive Django REST API for a blogging platform with JWT authentication, social login (Google), and full CRUD operations for stories, comments, likes, and more.

## Features

- 📝 Story/Blog post management
- 👤 Custom user authentication with email verification
- 🔐 JWT token-based authentication
- 🌐 Google OAuth integration
- 💬 Comments and nested replies
- ❤️ Like/Unlike functionality
- 👥 Follow/Unfollow users
- 📚 Personal libraries for organizing stories
- 🔔 Real-time notifications
- 🏷️ Tag system
- 📖 Swagger API documentation

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd blog-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=blog_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth (optional - for social auth)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 5. Database Setup

```bash
# Create PostgreSQL database
createdb blog_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## Authentication Setup

### Email Authentication

#### 1. User Registration

```http
POST /api/rest_auth/registration/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123"
}
```

**Response:**
```json
{
    "detail": "Verification e-mail sent."
}
```

#### 2. Email Verification

Users will receive an email with a verification link. Once clicked, they can proceed to login.

#### 3. Login

```http
POST /api/token/
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. Token Refresh

```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Google OAuth Setup

#### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/`

#### 2. Django Admin Setup

1. Go to `/admin/` and login
2. Navigate to **Sites** and update the domain to `127.0.0.1:8000`
3. Go to **Social Applications** and add a new Google application:
   - Provider: Google
   - Name: Google
   - Client ID: Your Google Client ID
   - Secret Key: Your Google Client Secret
   - Sites: Select your site

#### 3. Google Login Flow

```http
GET /accounts/google/login/
```

This will redirect to Google OAuth. After successful authentication, users will be redirected to `/api/auth/session-to-jwt/` which converts the session to JWT tokens.

## API Usage

All authenticated requests need this header: `Authorization: Bearer <your-access-token>`

### Stories API
- **Create Story**: `POST /api/stories/` - Write a new blog post (requires login)
- **Get All Stories**: `GET /api/stories/` - View all published stories (public)
- **Get Single Story**: `GET /api/stories/{id}/` - View a specific story (public)
- **Update Story**: `PUT /api/stories/{id}/` - Edit your own story (author only)
- **Delete Story**: `DELETE /api/stories/{id}/` - Remove your own story (author only)

### Comments API
- **Add Comment**: `POST /api/comments/` - Comment on a story (requires login)
- **Get Story Comments**: `GET /api/comments/story/{story_id}/` - View all comments on a story (public)
- **Reply to Comment**: `POST /api/comments/{comment_id}/reply/` - Reply to a comment (requires login)
- **Comment Count**: `GET /api/comments/story/{story_id}/count/` - Get total comment count (public)

### Likes API
- **Like Story**: `POST /api/likes/` - Like a story (requires login)
- **Get Story Likes**: `GET /api/likes/story/{story_id}/` - View who liked a story (public)
- **Like Count**: `GET /api/likes/story/{story_id}/count/` - Get total like count (public)
- **Unlike Story**: `DELETE /api/likes/{like_id}/` - Remove your like (requires login)

### Follow System
- **Follow User**: `POST /api/follower/` - Follow another user (requires login)
- **Get Followers**: `GET /api/follower/user/{user_id}/followers/` - View user's followers (requires login)
- **Get Following**: `GET /api/follower/user/{user_id}/followings/` - View who user follows (requires login)
- **Follower Count**: `GET /api/follower/user/{user_id}/followers/count/` - Get follower count (requires login)
- **Following Count**: `GET /api/follower/user/{user_id}/followings/count/` - Get following count (requires login)
- **Unfollow**: `DELETE /api/follower/{follower_id}/` - Stop following a user (requires login)

### Libraries (Personal Collections)
- **Create Library**: `POST /api/library/` - Create a reading list (requires login)
- **Get User Libraries**: `GET /api/library/user/{user_id}/libraries/` - View user's public libraries, or all your own (requires login)
- **Add Story to Library**: `POST /api/library-story/` - Save a story to your library (requires login)
- **Get Library Stories**: `GET /api/library-story/library/{library_id}/get-all-stories/` - View stories in a library (requires login)

### Notifications
- **Get Notifications**: `GET /api/notifications/` - View your notifications (requires login)
- **Filter Notifications**: `GET /api/notifications/?type=like&is_read=false` - Filter by type and read status (requires login)
- **Mark All Read**: `POST /api/notifications/mark_all_read/` - Mark all notifications as read (requires login)
- **Mark Single Read**: `PATCH /api/notifications/{id}/` - Mark one notification as read (requires login)

### Tags
- **Get All Tags**: `GET /api/tags/` - View all available tags (public)
- **Create Tag**: `POST /api/tags/` - Create new tags (admin only)

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error responses include details:

```json
{
    "detail": "Error message here"
}
```

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React frontend)
- `http://127.0.0.1:8000` (Django backend)

## Security Features

- JWT token authentication with refresh mechanism
- CSRF protection
- Email verification for new accounts
- Permission-based access control
- Password validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please create an issue in the GitHub repository or contact [derrouazmanel@gmail.com](mailto:derrouazmanel@gmail.com).