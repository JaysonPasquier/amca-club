# American Car Club France (AMCF) - Demo Day Presentation
*Holberton School Student Project - Jayson Pasquier, C25*

---

## Slide 1: Introduction & Personal Background

### Slide Content:
- **Title:** American Muscle Car France (AMCF)
- **Presenter:** Jayson Pasquier, C25 - Holberton School
- **About Me:**
  - First-year student at Holberton School
  - Passionate about technology since childhood
  - Learning beyond curriculum (Lua, React)
  - 5-6 hours daily development commitment

### Slide Text:
Hello everyone, I'm Jayson Pasquier, C25, and today I'm going to talk about a website called American Muscle Car France or AMCF.

But before that, I'm going to talk a little about myself. So I always used computers and consoles in general since I'm a child and I always wanted to work in video game programming, and when I heard that Holberton School exists I was so happy because I was finally going to be able to work and learn something that I like so it was a great opportunity for me.

---

## Slide 2: Presentation Overview

### Slide Content:
- Problem & Inspiration
- Solution Overview
- Live Demo - amc-f.com
- Technologies Used
- Technical Architecture
- Challenges Faced
- What I Learned
- Future Improvements

### Slide Text:
So for the main subject of today, first of all I'm going to talk about the problem we tried to fix with this website and project in general, the solution, how do we access it, the technologies used in the project, the technical architecture, the challenges, what I learned from it, and the next improvements.

---

## Slide 3: The Problem & Inspiration

### Slide Content:
**Family Inspiration:**
- Brother and father wanted to create American car club in France
- Asked me to build a website
- Goal: Expand love of American cars and create connections

**Current Problems:**
- Communication fragmented across platforms (Facebook, email, phone)
- Event organization is chaotic
- No quality control for new members
- Hard to showcase member vehicles

### Slide Text:
The website idea came from my brother and father who wanted to create a club of American cars and they asked me to create a website for it. The point of the club is to expand the love of American cars to other people and to make contact in this sector. Currently, car clubs have fragmented communication across multiple platforms which makes it difficult to organize events and maintain a good community.

---

## Slide 4: The Solution

### Slide Content:
**AMCF Platform:**
- Centralized member management
- Quality-controlled community with admin approval
- Event organization with calendar and RSVP
- Vehicle showcase platform
- Professional online presence

**Target Users:**
- American car owners
- Car enthusiasts
- Event organizers

### Slide Text:
The solution was to create an association and not just a club, and to create a website where people can create a profile, ask for help, participate in different events of ours or others, and just talk about cars in general. This transforms a scattered community into a professional, organized platform.

---

## Slide 5: Website Access

### Slide Content:
**Website URL:** amc-f.com
- Open to anyone interested in American cars
- Registration monitored by admin approval
- Admin validates profiles to maintain quality

**Demo Features:**
- Public registration → Admin approval
- Member profiles with car showcase
- Event calendar and RSVP
- Member directory

### Slide Text:
So how do we access the website? The website URL is amc-f.com and it's open to anyone. The only thing is that the registration is monitored - like an admin needs to validate the profile so nothing bad is added or something like that.

---

## Slide 6: Technologies Used

### Slide Content:
**Backend:**
- Django 4.2.7
- Python 3.12
- SQLite database
- Django Admin interface

**Frontend:**
- HTML, CSS, JavaScript
- Bootstrap 5 for responsive design
- Server-side rendering

**Media Storage:**
- Images saved on server
- Organized folder structure

### Slide Text:
In this project I used HTML, CSS, Django, JavaScript, and SQLite. I chose Django because it has a built-in admin interface that saved me weeks of development, it has built-in security, and it makes complex database relationships simple. The frontend uses server-side rendering which is better for SEO and loads quickly on all devices.

---

## Slide 7: Technical Architecture

### Slide Content:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │    Database     │
│ • HTML/CSS/JS   │◄──►│ • Django 4.2.7  │◄──►│ • SQLite        │
│ • Bootstrap 5   │    │ • Python 3.12   │    │ • File Storage  │
│ • Responsive    │    │ • Django Admin  │    │ • Media Files   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Key Models:**
- User → UserProfile (member profiles)
- Events (with RSVP system)
- Posts (social features)
- Forum (future feature)

### Slide Text:
So the technical architecture isn't too complicated. We have a Django backend that handles all the business logic, a database that stores user profiles, events, and posts, and a frontend that renders everything responsively. The architecture is designed to be scalable and maintainable.

---

## Slide 8: Key Features

### Slide Content:
**1. Registration System:**
- Public registration → Admin review → Profile creation

**2. Member Profiles:**
- Sequential member IDs (#001, #002...)
- Role badges (Founder, Member, Developer, Admin)
- Car showcase with photos and details
- Social media integration

**3. Event Management:**
- Create events with date, time, location
- Upload event flyers
- RSVP system
- Participant tracking

### Slide Text:
The platform has three main features. First, a smart registration system where users register publicly, then admins review and approve them, and finally approved users create detailed profiles. Second, member profiles that showcase their cars with photos and details, plus social media links. Third, an event management system where organizers can create events and members can RSVP.

---

## Slide 9: Challenges Faced

### Slide Content:
**Challenge 1: File Upload Management**
- Problem: Handling profile images and event flyers
- Solution: Custom file naming system and organized folders

**Challenge 2: User Approval Workflow**
- Problem: Balancing open registration with quality control
- Solution: Separate model for pending registrations

**Challenge 3: Responsive Design**
- Problem: Mobile compatibility across devices
- Solution: Custom CSS media queries + Bootstrap 5

**Challenge 4: Database Relationships**
- Problem: Complex relationships between users, events, posts
- Solution: Careful foreign key design with proper CASCADE behaviors

### Slide Text:
I faced several technical challenges. The biggest was implementing the user approval workflow - I had to balance making registration open to everyone while maintaining quality control. I solved this by creating a separate model for pending registrations and building an admin notification system. Another challenge was making the site work well on mobile devices, which I solved with responsive design techniques.

---

## Slide 10: What I Learned

### Slide Content:
**Technical Skills:**
- Django framework from zero to full application
- Database design and relationships
- User authentication and approval systems
- File upload and media handling
- Responsive web design

**Personal Development:**
- Time management (5-6 hours daily)
- Project management and planning
- Real-world problem solving
- Communication with non-technical users

### Slide Text:
This project taught me a lot. Technically, I learned Django from scratch, how to design databases with complex relationships, how to handle user authentication and file uploads, and how to make responsive websites. Personally, I learned discipline to work consistently every day, how to manage a long-term project, and how to solve real problems for actual users - my family.

---

## Slide 11: Current Status

### Slide Content:
**Live Platform:** amc-f.com (deployed and accessible)

**Completed Features:**
- ✅ User registration and approval system
- ✅ Member profiles with car showcases
- ✅ Event calendar and RSVP system
- ✅ Admin dashboard
- ✅ Basic forum system
- ✅ Product catalog

**In Development:**
- 🚧 Email notifications
- 📋 Mobile app (future)

### Slide Text:
The platform is currently live at amc-f.com with all core features working. Users can register, get approved by admins, create profiles, showcase their cars, and participate in events. The admin dashboard allows for content management and user approval. I'm currently working on email notifications for new members and event reminders.

---

## Slide 12: Future Improvements

### Slide Content:
**Phase 2 (Next 3 months):**
- Email integration for notifications
- Advanced forum with categories
- Mobile app development

**Phase 3 (6-12 months):**
- Marketplace for parts trading
- Analytics dashboard
- API development

**Phase 4 (12+ months):**
- Multi-club support
- Regional chapters
- National network expansion

### Slide Text:
For future improvements, I'm planning to add email notifications for new members and events, expand the forum system with categories for different topics like engine modifications and bodywork, and eventually develop a mobile app. Longer term, I want to add a marketplace where members can trade parts, and support for multiple regional clubs across France.

---

## Slide 13: Demo Time

### Slide Content:
**Live Demonstration:**
- Navigate to amc-f.com
- Show registration process
- Browse member profiles
- View event calendar
- Admin dashboard walkthrough

**Code Examples:**
- Django model design
- Admin interface customization
- Security implementations

### Slide Text:
Now let me show you the actual website. We'll go to amc-f.com and I'll walk you through the registration process, show you member profiles with their cars, look at the event calendar, and demonstrate the admin dashboard where we approve new members and manage content.

---

## Slide 14: Lessons for Students

### Slide Content:
**Key Takeaways:**
1. Start with real problems (building for actual users)
2. Use iterative development (MVP first, then features)
3. Balance learning with delivery
4. Consistent daily work is crucial
5. Deploy early and often

**Advice:**
- Choose projects that solve actual problems
- Document everything
- Version control saves projects
- Real deployment teaches valuable lessons

### Slide Text:
For my fellow Holberton students, my main advice is to start with real problems that affect actual people. Building for my family gave me clear requirements and immediate feedback. Work consistently every day rather than in big bursts, use version control religiously, and deploy early so you can catch issues that only appear in production.

---

## Slide 15: Technical Deep Dive

### Slide Content:
**Django Admin Customization:**
```python
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'user', 'role', 'is_approved')
    actions = ['approve_members', 'reject_members']
```

**Security Features:**
- CSRF protection on all forms
- User authentication required
- File upload validation
- SQL injection protection through Django ORM

### Slide Text:
Let me show you some of the code. I customized Django's admin interface to make member approval efficient, implemented security measures like CSRF protection and file validation, and designed the database models to handle complex relationships between users, events, and posts while maintaining data integrity.

---

## Slide 16: Thank You & Questions

### Slide Content:
**Project Links:**
- Live Platform: amc-f.com
- GitHub: Available upon request

**Contact:**
- Jayson Pasquier, C25
- Holberton School

**Special Thanks:**
- My family for the inspiration
- Holberton School for the foundation
- Fellow students for feedback

### Slide Text:
Thank you for your attention. The website is live at amc-f.com if you want to check it out. I'm happy to answer any questions you have about the technical implementation, the challenges I faced, or advice for your own projects. This project represents not just code, but a bridge between passion and technology, connecting American car enthusiasts across France.

---

### Demo Day Presentation Timing Guide:
- **Slides 1-3:** Personal intro and problem (3 minutes)
- **Slides 4-6:** Solution and access (3 minutes)
- **Slides 7-9:** Technical details and challenges (5 minutes)
- **Slides 10-12:** Learning and current status (4 minutes)
- **Slides 13-15:** Demo and code examples (4 minutes)
- **Slide 16:** Q&A and closing (1 minute)

**Total: 20 minutes** ✅
