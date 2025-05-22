American Car Club Website Project Planning - Stage 1 Report

1. Project Overview

My Role:
I'm a student at Holberton School and almost finishing my first year. I enjoy learning technologies outside of my school curriculum, such as Lua and React, which will help me in developing this project independently.

Project Management Approach:
I work on the project almost every day, typically for 5-6 hours straight. This consistent dedication allows me to maintain momentum and make steady progress on the development.

Tools & Communication:
I use GitHub for version control and maintaining different versions of the project, VS Code as my primary development environment, and Figma for design work when needed for mockups or UI planning even if I didn't use it a lot.

2. Research and Brainstorming

Initial Research:
I didn't extensively research other websites initially. Instead, I began with a written concept document outlining what I wanted to create. After establishing the base functionality, I identified additional features that would enhance the user experience.

Brainstorming Results:
- Core features: Must-have features include member profiles, event calendar, and admin approval system. Nice-to-have features for future implementation include forum functionality, a marketplace for parts/cars, and photo galleries for car shows and meetups.
- User experience: Simplified registration flow with 3 steps: basic info → admin approval → profile creation. This ensures quality control of membership while keeping the process straightforward.
- Technical implementation: Django REST framework for the backend API, React for the frontend interface, with images stored directly on the server rather than using external storage solutions.
- Design approach: Clean, minimalist design with emphasis on car imagery, mobile-responsive layout with card-based components to showcase members and events effectively.

Inspiration Sources:
The project is primarily inspired by the needs of car club communities and modern web design principles focusing on usability and clean aesthetics.


3. Idea Evaluation

Evaluation Criteria:
For this project, I'm prioritizing feasibility (can I build it with my current skills?), user value (will club members find it useful?), and development efficiency (can I complete it in reasonable time?).

Feature Prioritization:
I've evaluated the key features based on their importance to the core functionality:


Feature
Priority
Reasoning
User Profiles
High
Essential for member identity and community building
Admin Approval
High
Critical for maintaining quality membership
Event Calendar
High
Primary activity coordination tool for the club
Member Directory
Medium
Important for community but simpler than profiles
Forum System
Medium
Valuable but complex
Photo Galleries
Medium
Enhances experience but not core functionality



Technical Constraints:
My limited experience with React's advanced features might slow down frontend development. Server configuration will be simple at first, focusing on reliability rather than advanced features.

Risk Assessment:
- High risk: Time management - balancing school commitments with consistent development time
- Medium risk: Technical complexity of user approval flow and permission systems
- Low risk: Basic CRUD operations for profiles and events are well within my capabilities




4. Decision and Refinement

Selected Approach:
Community-focused platform centered around member profiles and events, with emphasis on visual appeal and ease of use for non-technical car enthusiasts. The platform will serve as a digital home for car club members.

Problem Definition:
Current car club communication and event organization happen through fragmented channels (Facebook, email, phone calls), making it difficult to maintain a cohesive community and keep track of events and members.

Target Audience:
Primary: American car owners with varying technical abilities who want to connect with other enthusiasts.
Secondary: Car enthusiasts without American cars but interested in the community and events.

Core Features:
- User Profiles: Custom avatars, car details, member ID system, role assignments (founder, co-founder, member)
- Event System: Calendar view, RSVP functionality, location maps, automatic email notifications (email functionality to be added in later phases)
- Admin Dashboard: New member approval workflow, content moderation tools, analytics reporting

Technical Architecture:
Django backend with PostgreSQL database, Django REST framework for API, React frontend, JWT authentication, media stored directly on the server, Django templating for admin interfaces.

5. Documentation

Project Scope:
MVP includes: user authentication, admin approval flow, user profiles, member directory, and simple event listing.
Future phases will add: forums, media galleries, member-to-member messaging, and email notifications.

Feature Specifications:
- User Profiles: Profiles will include public display name, member ID (auto-incremented), profile image (with default option), join date, last active date, role (from predefined choices: founder, co-founder, member, developer), car details (brand, model, year, optional description and photos), and privacy settings.

- Admin Approval System: New user registrations will be placed in a pending state. Admins will receive notifications of new registrations and can approve or reject them through a dedicated interface. Approved users will be prompted to complete their profiles.

- Event System: Events will have title, description, date/time, location (with map integration), RSVP capability, and attendee list. The system will display upcoming events on the home page and allow filtering by date range.

- Member Directory: Searchable/filterable list of approved members showing profile image, name, member ID, role, and join date, with links to detailed profile views.

Design Concept:
Modern, clean interface with black and white as base colors. Minimal use of accent colors to maintain a professional, timeless aesthetic. Card-based components for consistent display of members and events, with responsive design for all screen sizes.


