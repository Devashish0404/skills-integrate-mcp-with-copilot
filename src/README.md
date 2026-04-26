# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- **Role-Based Authentication**: Login system with three user roles (student, staff, admin)
- View all available extracurricular activities
- Sign up for activities (staff/admin only)
- Session-based token authentication
- Credential file storage for users

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn python-multipart
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - Frontend: http://localhost:8000/
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## Authentication

### User Roles

- **Student**: Can view activities (no signup/unregister permissions)
- **Staff**: Can view activities and manage participant signups
- **Admin**: Full system access

### Authentication Endpoints

| Method | Endpoint        | Description                          |
| ------ | --------------- | ------------------------------------ |
| POST   | `/auth/login`   | Login with username and password     |
| POST   | `/auth/logout`  | Logout and invalidate token          |
| GET    | `/auth/me`      | Get current user information         |

### Login Request

```json
{
  "username": "john_staff",
  "password": "password123"
}
```

### Login Response

```json
{
  "access_token": "token_string",
  "token_type": "bearer",
  "user": {
    "username": "john_staff",
    "role": "staff"
  }
}
```

## API Endpoints

| Method | Endpoint                                                          | Description                                                         | Auth Required |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- | ------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count | No            |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up a student for an activity                                   | Yes (Staff+)  |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Remove a student from an activity                                   | Yes (Staff+)  |

## Credentials

Default credentials are stored in `credentials.json`:

- **Username**: `john_staff` | **Role**: Staff
- **Username**: `admin_user` | **Role**: Admin

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

3. **Users** - Defined in credentials.json:
   - Username
   - Role (student, staff, admin)
   - Active status

All data is stored in memory, which means data will be reset when the server restarts.

## Security Notes

- Tokens expire after 24 hours
- Passwords are stored in credentials.json (use proper hashing in production)
- Protected endpoints require valid authentication token in Authorization header
- Role-based access control prevents unauthorized operations
