# American Car Club Website Project: Technical Documentation

## 1. User Stories and Mockups

### User Stories (MoSCoW Prioritization)

#### Must Have:
1. As a car club member, I want to create a profile showcasing my vehicle, so that I can connect with other enthusiasts.
2. As a club administrator, I want to approve new member registrations, so that I can maintain quality membership.
3. As a club member, I want to view upcoming events, sot I can participate in club activities.
4. As a club member, I want to RSVP to events, so that organizer thas know who is attending.
5. As a club administrator, I want to create and manage events, so that I can organize club activities.

#### Should Have:
6. As a club member, I want to search the member directory, so that I can find members with similar interests or vehicles.
7. As a club member, I want to update my profile information, so that my details remain current.
8. As a club administrator, I want to assign roles to members, so that responsibilities are clearly defined.

#### Could Have:
9. As a club member, I want to upload multiple photos of my vehicle, so that I can showcase it from different angles.
10. As a club member, I want to be notified about new events, so that I don't miss any activities.
11. As a club administrator, I want to see analytics about event attendance, so that I can plan better events.

#### Won't Have (for MVP):
12. As a club member, I want to participate in forum discussions, so that I can share knowledge with others.
13. As a club member, I want to sell parts in a marketplace, so that I can help others with their projects.
14. As a club member, I want to send direct messages to other members, so that I can communicate privately.

*Note: No mockups were created as the pages were developed directly without prior design documentation.*

## 2. System Architecture

### High-Level Architecture Diagram

```
┌───────────────────┐     ┌────────────────────────┐     ┌───────────────────┐
│                   │     │                        │     │                   │
│  React Frontend   │◄────┤  Django REST Framework │◄────┤   PostgreSQL DB   │
│                   │     │                        │     │                   │
└───────┬───────────┘     └────────────┬───────────┘     └───────────────────┘
        │                              │                          ▲
        │                              │                          │
        ▼                              ▼                          │
┌───────────────────┐     ┌────────────────────────┐              │
│                   │     │                        │              │
│  User Interface   │     │   JWT Authentication   │──────────────┘
│    Components     │     │                        │
│                   │     └────────────────────────┘
└───────────────────┘               │
                                    │
                                    ▼
                    ┌────────────────────────┐
                    │                        │
                    │    Media Storage       │
                    │    (Server Files)      │
                    │                        │
                    └────────────────────────┘
```

### Data Flow:
1. Users interact with the React frontend, which sends requests to the Django REST API.
2. The API handles authentication via JWT and processes requests.
3. Data is stored in and retrieved from the PostgreSQL database.
4. Media files (images) are stored directly on the server filesystem.
5. The frontend receives data from the API and renders it to the user.

## 3. Components, Classes, and Database Design

### Backend Classes (Django)

**User Model (extends Django User)**
- Attributes: username, email, password, is_active, is_staff, date_joined
- Methods: authenticate(), save(), get_profile()

**Profile Model**
- Attributes: user (FK), profile_image, member_id, join_date, last_active, role
- Methods: approve(), reject(), update_last_active()

**Car Model**
- Attributes: owner (FK to Profile), brand, model, year, description, primary_image
- Methods: add_image(), remove_image(), update_details()

**Event Model**
- Attributes: title, description, date, time, location, organizer (FK to Profile), is_approved
- Methods: approve(), cancel(), update_details()

**RSVP Model**
- Attributes: event (FK), member (FK to Profile), status, timestamp
- Methods: update_status(), cancel()

### Database Design (PostgreSQL)

**ER Diagram**
```
User (1) ────────► Profile (1)
                     │
                     │
                     ├─────► Car (Many)
                     │
                     ├─────► Event (Many)
                     │         │
                     └─────────┘
                          │
                          ▼
                        RSVP
```

**Tables:**

1. **users**
   - id (PK)
   - username
   - email
   - password (hashed)
   - is_active
   - is_staff
   - date_joined

2. **profiles**
   - id (PK)
   - user_id (FK)
   - profile_image
   - member_id
   - join_date
   - last_active
   - role (ENUM: 'founder', 'co-founder', 'member', 'developer')
   - is_approved

3. **cars**
   - id (PK)
   - owner_id (FK to profiles)
   - brand
   - model
   - year
   - description
   - primary_image

4. **car_images**
   - id (PK)
   - car_id (FK)
   - image_path
   - is_primary

5. **events**
   - id (PK)
   - title
   - description
   - date
   - time
   - location
   - map_coordinates
   - organizer_id (FK to profiles)
   - is_approved

6. **rsvps**
   - id (PK)
   - event_id (FK)
   - member_id (FK to profiles)
   - status (ENUM: 'attending', 'maybe', 'not_attending')
   - timestamp

### Frontend Components (React)

1. **Authentication Components**
   - LoginForm
   - RegistrationForm
   - PasswordReset

2. **Profile Components**
   - ProfileView
   - ProfileEditForm
   - AvatarUpload
   - CarDetailsForm

3. **Member Directory Components**
   - MemberList
   - MemberCard
   - MemberSearch
   - MemberFilter

4. **Event Components**
   - EventCalendar
   - EventCard
   - EventDetailView
   - EventForm
   - RSVPButton

5. **Admin Components**
   - AdminDashboard
   - MemberApprovalList
   - RoleAssignment
   - EventModeration

## 4. Sequence Diagrams

### User Registration and Approval

```
┌─────┐          ┌────────┐          ┌───────┐          ┌─────┐
│User │          │Frontend│          │Backend│          │Admin│
└──┬──┘          └───┬────┘          └──┬────┘          └──┬──┘
   │   Fill Form     │                  │                  │
   │─────────────────>                  │                  │
   │                 │   POST /register │                  │
   │                 │─────────────────>│                  │
   │                 │                  │ Store as Pending │
   │                 │                  │──────────────────│
   │                 │  201 Created     │                  │
   │                 │<─────────────────│                  │
   │ Success Message │                  │                  │
   │<─────────────────                  │                  │
   │                 │                  │ Notify Admin     │
   │                 │                  │─────────────────>│
   │                 │                  │                  │
   │                 │                  │  Approval UI     │
   │                 │                  │<─────────────────│
   │                 │                  │                  │
   │                 │                  │ Approve/Reject   │
   │                 │                  │<─────────────────│
   │                 │                  │                  │
   │                 │                  │Update User Status│
   │                 │                  │──────────────────│
   │                 │                  │                  │
   │   Notification  │                  │                  │
   │<────────────────────────────────────                  │
   │                 │                  │                  │
┌──┴──┐          ┌───┴────┐         ┌───┴───┐           ┌──┴──┐
│User │          │Frontend│         │Backend│           │Admin│
└─────┘          └────────┘         └───────┘           └─────┘
```

### Event Creation and RSVP

```
┌──────────┐       ┌────────┐      ┌───────┐       ┌──────┐
│Organizer │       │Frontend│      │Backend│       │Member│
└────┬─────┘       └───┬────┘      └───┬───┘       └──┬───┘
     │ Create Event    │               │              │
     │─────────────────>               │              │
     │                 │ POST /events  │              │
     │                 │──────────────>│              │
     │                 │               │ Save Event   │
     │                 │               │──────────────│
     │                 │ 201 Created   │              │
     │                 │<──────────────│              │
     │ Success Message │               │              │
     │<────────────────                │              │
     │                 │               │              │
     │                 │               │ List Events  │
     │                 │               │<─────────────│
     │                 │ GET /events   │              │
     │                 │<──────────────│              │
     │                 │               │              │
     │                 │               │ Events Data  │
     │                 │──────────────>│              │
     │                 │               │ View Events  │
     │                 │               │─────────────>│
     │                 │               │              │
     │                 │               │ RSVP to Event│
     │                 │               │<─────────────│
     │                 │ POST /rsvp    │              │
     │                 │<──────────────│              │
     │                 │               │              │
     │                 │ 200 OK        │              │
     │                 │──────────────>│              │
     │                 │               │ Confirmation │
     │                 │               │─────────────>│
┌────┴─────┐       ┌───┴────┐      ┌───┴───┐       ┌──┴───┐
│Organizer │       │Frontend│      │Backend│       │Member│
└──────────┘       └────────┘      └───────┘       └──────┘
```

## 5. API Specifications

### External APIs

No external APIs are being used in the MVP. All functionality is self-contained within the application.

### Internal API Endpoints

#### Authentication

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/auth/register` | POST | Register new user | `{username, email, password, name}` | `{user_id, status: "pending"}` |
| `/api/auth/login` | POST | Login user | `{username, password}` | `{token, user}` |
| `/api/auth/refresh` | POST | Refresh JWT token | `{refresh_token}` | `{access_token}` |

#### Users & Profiles

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/users/:id` | GET | Get user profile | - | `{profile_data}` |
| `/api/users/:id` | PUT | Update profile | `{profile_fields}` | `{updated_profile}` |

#### Admin Management

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/admin/pending-users` | GET | List pending users | - | `[{user_data}]` |
| `/api/admin/users/:id/approve` | PUT | Approve user | `{approved: true}` | `{updated_user}` |
| `/api/admin/users/:id/role` | PUT | Change user role | `{role}` | `{updated_user}` |

#### Events

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/events` | GET | List events | - | `[{event_data}]` |
| `/api/events` | POST | Create event | `{event_details}` | `{new_event}` |
| `/api/events/:id` | GET | Get event details | - | `{event_data}` |
| `/api/events/:id` | PUT | Update event | `{event_fields}` | `{updated_event}` |
| `/api/events/:id/rsvp` | POST | RSVP to event | `{status}` | `{rsvp_data}` |

## 6. SCM and QA Strategies

### Source Control Management (SCM)

**Repository Structure:**
- Main GitHub repository for version control
- README with setup instructions and project overview

**Workflow:**
1. Direct commits to main repository
2. Regular commits with descriptive messages
3. Manual backups of important milestones
4. Documentation of significant changes

### Quality Assurance (QA)

**Testing Strategy:**

1. **Unit Testing:**
   - Backend: Django test suite for models, views, and API endpoints
   - Frontend: React component tests using Jest and React Testing Library

2. **Integration Testing:**
   - API endpoint testing with Postman
   - Frontend-backend integration tests for key workflows

3. **Manual Testing:**
   - Critical user journeys (registration, profile creation, event RSVP)
   - Cross-browser testing (Chrome, Firefox, Safari)
   - Mobile responsiveness testing

**Deployment Pipeline:**
1. Local development environment
2. Testing on development server
3. Staging environment for final verification
4. Production deployment

**Tools:**
- Jest for React component testing
- Django test suite for backend
- Postman for API testing
- ESLint and Prettier for code quality
- GitHub Actions for CI/CD automation (future implementation)

## 7. Technical Justifications

### Technology Stack Selection

**Django & Django REST Framework:**
- Strong ORM for database interactions
- Built-in admin interface for easy management
- Robust authentication system
- Excellent documentation and community support
- Personal familiarity with Python

**React Frontend:**
- Component-based architecture for reusability
- Virtual DOM for efficient updates
- Large ecosystem of libraries
- Strong community support
- Personal interest in expanding React skills

**PostgreSQL:**
- Reliable relational database with excellent support for Django
- Strong data integrity through constraints and transactions
- Good performance for the expected data volume
- Easy to set up and maintain

**JWT Authentication:**
- Stateless authentication method
- Secure token-based approach
- Good fit for React + Django REST Framework architecture
- Supports mobile clients in the future

**Direct Server File Storage:**
- Simplicity for MVP implementation
- Adequate for expected initial user base and image uploads
- Can be migrated to cloud storage in future iterations
