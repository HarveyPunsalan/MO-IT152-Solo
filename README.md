# Connectly API: MO-IT152 Integrative Programming and Technologies
## Terminal Assessment

---

## About This Project

This is my Connectly API project for MO-IT152. I built this across two milestones and a terminal assessment. MS1 was the foundation "CRUD, authentication, design patterns, and HTTPS". MS2 built on top of that with likes and comments, Google OAuth, and a news feed. The Terminal Assessment is HW8 and HW9, which added privacy controls, role-based access, and performance improvements to the feed.

This is a solo submission. All code was written by me.

---

## Branch Information

Everything is on the `master` branch.

> "All submissions, including the Terminal Assessment deliverable, reflect the code currently on master."

---

## Project Structure

```
MO-IT152-SOLO/
└── connectly_project/
    ├── .vscode/
    │   └── launch.json
    ├── connectly_project/
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── factories/
    │   ├── __init__.py
    │   └── post_factory.py
    ├── posts/
    │   ├── migrations/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── google_views.py    ← added in MS2 (HW6)
    │   ├── models.py
    │   ├── permissions.py     ← modified in Terminal Assessment (HW8)
    │   ├── serializers.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── singletons/
    │   ├── __init__.py
    │   ├── config_manager.py
    │   └── logger_singleton.py
    ├── env/
    ├── cert.pem
    ├── key.pem
    ├── db.sqlite3
    ├── manage.py
    └── .gitignore
```

---

## How to Run

1. Clone the repository
2. Go into the project folder:
   ```
   cd connectly_project
   ```
3. Activate the virtual environment:
   ```
   source env/bin/activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
6. Start the server:
   ```
   python3 manage.py runserver_plus --cert-file cert.pem --key-file key.pem
   ```

---

## API Endpoints

### Milestone 1 (still working)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/posts/users/create` | Create a new user |
| GET | `/posts/users/` | Get all users |
| POST | `/posts/posts/` | Create a new post |
| GET | `/posts/posts/` | Get all posts |
| POST | `/posts/comments/` | Create a comment |
| GET | `/posts/comments/` | Get all comments |
| GET | `/posts/posts/<id>/` | Get a specific post |
| POST | `/posts/posts/create/` | Create post using the Factory Pattern |

### Milestone 2 (new)

| Method | Endpoint | Description | HW |
|--------|----------|-------------|----|
| POST | `/posts/posts/<id>/like/` | Like a post | HW5 |
| POST | `/posts/posts/<id>/comment/` | Comment on a post | HW5 |
| GET | `/posts/posts/<id>/comments/` | Get all comments on a post | HW5 |
| POST | `/auth/google/login/` | Log in or sign up via Google | HW6 |
| GET | `/posts/feed/` | Paginated feed of posts, newest first | HW7 |

### Terminal Assessment (one new endpoint + existing ones updated)

| Method | Endpoint | Description | HW |
|--------|----------|-------------|----|
| GET | `/posts/admin/posts/` | All posts including private ones admin only | HW8 |

The following endpoints already existed but were updated internally no new routes:

| Method | Endpoint | What changed | HW |
|--------|----------|-------------|----|
| GET | `/posts/posts/<id>/` | Blocks non-owners from viewing private posts (403) | HW8 |
| PUT | `/posts/posts/<id>/` | Only author or admin can edit | HW8 |
| DELETE | `/posts/posts/<id>/` | Only author or admin can delete | HW8 |
| GET | `/posts/posts/` | Filters results by privacy setting and role | HW8 |
| GET | `/posts/feed/` | Privacy filter added; supports `?page_size=N`; results now cached | HW8 + HW9 |

---

## What I Built

### Milestone 1 (recap)

- CRUD for Users, Posts, and Comments
- Serializers with validation
- Token-based authentication
- HTTPS with a self-signed certificate
- `IsPostAuthor` permission for object-level access control
- Password hashing with PBKDF2-SHA256
- Singleton Logger and Config Manager
- Factory Pattern for post creation (supports text, image, video types)

### Milestone 2

**HW5: Likes and Comments on Specific Posts**

Before this the API had a general comments endpoint but nothing post-specific, and no likes at all. I added a `Like` model with a `unique_together` constraint so users can't like the same post twice, the database rejects duplicates and `LikeSerializer` catches it early with a readable error instead of a raw crash. I wrote three new views: `LikePostView`, `CommentPostView`, and `GetPostCommentsView`. All three use `TokenAuthentication` and log events through the Singleton Logger.

**HW6: Integrating Third-Party Services**

This gave users a second way to log in on top of the existing username/password flow. I installed `django-allauth` and created `posts/google_views.py` with `GoogleLoginView`. The client sends a Google `id_token`, the view verifies it with Google's servers, and then either finds the existing account or creates a new one and returns the app's own DRF token so the user can make authenticated requests normally. The original login still works exactly the same.

**HW7: Building a News Feed**

Added `GET /feed` returning posts sorted newest first with pagination. I created a `FeedPagination` class that extends `PageNumberPagination` and pulls the default page size from `ConfigManager` instead of hardcoding it. The response follows the standard DRF format with `count`, `next`, `previous`, and `results`.

### Terminal Assessment

**HW8: Privacy Settings and Role-Based Access Control (RBAC)**

HW8 was the biggest task in the terminal assessment. I added a `role` field to the `User` model (`admin` or `user`, defaults to `user`) and a `privacy` field to the `Post` model (`public` or `private`, defaults to `public`). Both used `choices=` so Django validates the values. Ran migrations after both changes.

The bigger part was `posts/permissions.py`, a new file I created to keep permission logic in one place. It has two classes. `IsAdminUser` checks `request.user.role == 'admin'` and returns 403 if the user isn't an admin. `IsOwnerOrAdmin` is the one used for post-level operations, it checks if the requesting user is either the post's author or an admin. Regular users can only edit or delete their own posts.

From there I updated the views. `PostDetailView` now uses `IsOwnerOrAdmin` for write operations. `PostListCreate.get()` and `FeedView` both use Q objects to filter: regular users see all public posts plus their own private ones, admins see everything. I also added `AdminPostListView` at `/posts/admin/posts/` which is locked behind `IsAdminUser` only admins can hit that endpoint. Added `privacy` to `PostSerializer` fields so clients can set and read it.

Updated all the diagrams before coding: CRUD Interaction Flow v6 → v7 (added role check, ownership check, and privacy filter to Security Middleware and the endpoints), System Architecture v5 → v6 (added RBAC Permission Layer), Data Relationship diagram (added `role` to User and `privacy` to Post), and the Access Control Decision Flow diagram.

**HW9: Performance Optimization**

HW9 built on top of the feed from HW7 and HW8. Two things were added: better pagination and caching.

For pagination, I noticed during testing that `FeedPagination` was ignoring the `?page_size=N` query param because `get_page_size()` always returned the `ConfigManager` value. I fixed it by checking the query param first and only falling back to `ConfigManager` if the client didn't send one. This way clients can control page size when they need to, but the default still comes from one central place.

For caching, I added `LocMemCache` to `settings.py` and updated `FeedView` to check the cache before touching the database. The cache key is built per-user per-page so `adminuser` and `regularuser` never share a cache. On a miss the feed gets fetched from the database, stored with a 300-second timeout, and returned. On a hit the database is skipped entirely. To keep the cache from going stale I added cache invalidation in `PostListCreate.post()` when a new post is created it clears the first 5 page keys for that user so the next feed request always gets fresh data. Every cache event (HIT, MISS, invalidated) goes through `LoggerSingleton` so it shows up in the server logs.

Updated CRUD Interaction Flow v7 → v8 (added Cache Layer with the check/hit/miss/invalidate flow) and System Architecture v6 → v7 (added Cache Layer box between Django Server and SQLite).

---

## MS2 Summary

| Homework | What I added | Files touched |
|----------|--------------|---------------|
| HW5 | Like model, like/comment endpoints, get comments endpoint | `models.py`, `serializers.py`, `views.py`, `urls.py` |
| HW6 | Google OAuth login | `google_views.py` (new), `settings.py`, `connectly_project/urls.py` |
| HW7 | News feed with sorting and pagination | `views.py`, `posts/urls.py` |

## Terminal Assessment Summary

| Homework | What I added | Files touched |
|----------|--------------|---------------|
| HW8 | RBAC roles, privacy settings, ownership checks, admin endpoint | `models.py`, `permissions.py` (new), `views.py`, `serializers.py`, `urls.py` |
| HW9 | Caching for feed, pagination fix, cache invalidation on new post | `settings.py`, `views.py` |

---

## Design Patterns

The Singleton and Factory patterns from MS1 are still actively used throughout the terminal assessment, not just left in the code unused.

`LoggerSingleton` = every view logs through this, including the new cache HIT, MISS, and invalidation events added in HW9. Nothing uses `print()` directly.

`ConfigManager` = the default feed page size comes from `ConfigManager().get_setting("DEFAULT_PAGE_SIZE")` inside `FeedPagination.get_page_size()`. If the page size ever needs to change it's one place to update, not scattered across the code.

`PostFactory` = all post creation in `CreatePostView` still goes through `PostFactory`. It validates the post type and enforces metadata requirements before hitting the database.

---

## Intellectual Property Notice

This project was completed as part of the coursework for MO-IT152 at Mapua-Malayan Digital College. All course materials, instructions, diagrams, and templates used in this project are the exclusive property of Mapua-Malayan Digital College and are protected under Republic Act No. 8293, also known as the Intellectual Property Code of the Philippines. Unauthorized reproduction, distribution, or uploading of any part of these materials is strictly prohibited under Sections 172, 177, and 216 of the IP Code.

This repository contains only my own code and work. No proprietary course materials, templates, or assessment content from MMDC have been uploaded or reproduced here.

---

## AI Disclosure Statement

In the interest of transparency and in compliance with course documentation requirements, I am disclosing my use of AI and other tools during this project.

Tools used: Claude, Grammarly, QuillBot

**Claude**

I want to be upfront about how I used Claude in this project. I mostly used it as a reference the same way you'd Google something or read documentation when you're stuck or want to double check your understanding before moving forward.

The main things I asked Claude about were the system diagrams. Some of them were dense and I wanted to make sure I was reading them correctly before I started implementing anything. I'd describe what I was looking at and ask Claude to help me make sense of it. Same thing with the diagram updates across MS2 and the terminal assessment. I used it as a sounding board to check if the changes I was planning made sense before drawing them in Lucidchart.

I also asked for guidance on Postman testing. HW6 was confusing the first time because of how Google OAuth tokens work. For HW8 I needed help figuring out how to properly test with three different tokens (regularuser, a different regular user, and adminuser) to cover all the RBAC cases. For HW9 I needed to understand how to verify cache hits and misses through the server terminal logs since you can't see that directly in Postman.

All the actual implementation the models, views, serializers, URLs, the Like constraint, the OAuth view, the feed pagination, the RBAC permission classes, the privacy filter Q objects, the caching logic, and the cache invalidation, I wrote all of that myself in VS Code. Claude never touched the code. I used it to understand things, not to build things.

**QuillBot**

I used QuillBot solely for grammar and spelling checks on my written worksheet responses. English is not my strongest area and I wanted to make sure my written answers were readable and clear. QuillBot was only used to correct grammar, all the content, ideas, and answers in the worksheets are entirely my own.

**Grammarly**

Same as QuillBot used only for grammar checking on written responses, not for generating any content.
