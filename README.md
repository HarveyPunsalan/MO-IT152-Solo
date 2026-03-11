# Connectly API: MO-IT152 Integrative Programming and Technologies
## Milestone 2

---

## About This Project

This is my Connectly API project for MO-IT152. I built this incrementally across two milestones. MS1 covered the core stuff like CRUD, authentication, design patterns, and HTTPS. MS2 is where I added user interactions (likes and comments), Google OAuth login, and a news feed endpoint.

This is a solo submission. All code was written by me.

---

## Branch Information

Everything is on the `master` branch.

> "All submissions, including the Milestone 2 deliverable, reflect the code currently on `master`."

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
    │   ├── permissions.py
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
   ```bash
   cd connectly_project
   ```
3. Activate the virtual environment:
   ```bash
   source env/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```
6. Start the server:
   ```bash
   python3 manage.py runserver_plus --cert-file cert.pem
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
| GET | `/posts/feed/` | Get a paginated feed of posts (newest first) | HW7 |

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

#### HW5: Likes and Comments on Specific Posts

Before this, the API had a general comments endpoint but nothing post-specific, and no likes at all. HW5 added those missing pieces.

I added a `Like` model in `models.py` with foreign keys to both `User` and `Post`. The important part is the `unique_together` constraint, without it, users could like the same post multiple times, so that constraint makes the database reject duplicates. On top of that, I added validation in `LikeSerializer` to catch it early and return a readable error instead of a raw database crash.

For the views, I wrote three new classes:
- `LikePostView` for `POST /posts/posts/<id>/like/` — checks if the post exists, checks for duplicate likes, then saves
- `CommentPostView` for `POST /posts/posts/<id>/comment/` — pulls the author from the token automatically so the client doesn't have to send it manually
- `GetPostCommentsView` for `GET /posts/posts/<id>/comments/` — returns all comments for a post, or an empty list if there are none yet

All three are protected with `TokenAuthentication` and log events using the Singleton Logger. I also updated both diagrams (Data Relationship and CRUD Interaction Flow) to reflect these changes before writing any code.

#### HW6: Integrating Third-Party Services

This was about giving users a second way to log in instead of only username and password, they can now use their Google account. The existing login still works exactly the same; Google OAuth is just an extra option.

I installed `django-allauth` and created a new file `posts/google_views.py` with the `GoogleLoginView`. When a client sends a POST to `/auth/google/login/` with a Google `id_token`, the view sends that token to Google's servers to verify it. If it's valid, Google tells us who the user is. From there, the view either finds the existing account or creates a new one, then returns the app's own DRF token so the user can make authenticated requests normally.

I updated `settings.py` with the allauth config, added the new URLs in `connectly_project/urls.py`, ran migrations for allauth's social account tables, and updated the Auth Flow diagram to show the new Google login path running parallel to the original one.

#### HW7: Building a News Feed

This added a `GET /feed` endpoint that returns posts sorted newest first with pagination so instead of dumping every post at once, the client gets them in pages of 20.

I created a `FeedPagination` class that extends DRF's `PageNumberPagination` and a `FeedView` class in `views.py` that queries all posts ordered by `created_at` descending, runs them through the paginator, serializes, logs, and returns the response. The response follows the standard DRF paginated format with `count`, `next`, `previous`, and `results`. I registered it as `path('feed/', FeedView.as_view())` in `posts/urls.py`, making the full URL `/posts/feed/` since the posts app is mounted at `/posts/` in the main urls.py. I also updated the CRUD Interaction Flow diagram to include the feed path.

---

## MS2 Summary

| Homework | What I added | Files touched |
|----------|-------------|---------------|
| HW5 | Like model, like/comment endpoints, get comments endpoint | `models.py`, `serializers.py`, `views.py`, `urls.py` |
| HW6 | Google OAuth login | `google_auth_views.py` (new), `settings.py`, `connectly_project/urls.py` |
| HW7 | News feed with sorting and pagination | `views.py`, `posts/urls.py` |

---

## Intellectual Property Notice

This project was completed as part of the coursework for MO-IT152 at Mapua-Malayan Digital College. All course materials, instructions, diagrams, and templates used in this project are the exclusive property of Mapua-Malayan Digital College and are protected under **Republic Act No. 8293**, also known as the *Intellectual Property Code of the Philippines*. Unauthorized reproduction, distribution, or uploading of any part of these materials is strictly prohibited under Sections 172, 177, and 216 of the IP Code.

This repository contains only my own code and work. No proprietary course materials, templates, or assessment content from MMDC have been uploaded or reproduced here.

---

## AI Disclosure Statement

In the interest of transparency and in compliance with course documentation requirements, I am disclosing my use of AI and other tools during this project.

**Tools used:** Claude, Grammarly

---

**Claude**

- I want to be upfront about how I used Claude in this project. I mostly used it as a reference the same way you'd Google something or read documentation when you're stuck or want to double-check your understanding before moving forward.

The main things I asked Claude about were the system diagrams. Some of them were dense and I wanted to make sure I was reading them correctly before I started implementing anything. I'd describe what I was looking at and ask Claude to help me make sense of it. Same thing with the diagram updates in MS2. I used it as a sounding board to check if the changes I was planning actually made sense architecturally.

I also asked for some guidance on Postman testing, mostly for HW6. Google OAuth testing is genuinely confusing the first time because you're dealing with tokens from an external provider, and I wasn't sure I was testing it the right way. Claude helped me figure out what requests to send and what responses to expect.

All the actual implementation the models, views, serializers, URLs, the Like constraint, the OAuth view, the feed pagination. I wrote all of that myself in VS Code. Claude never touched the code. I used it to understand things, not to build things.

---

**QuillBot**

I used QuillBot  solely for grammar and spelling checks on my written worksheet responses. English is not my strongest area and I wanted to make sure my written answers were readable and clear. QuillBot was only used to correct grammar all the content, ideas, and answers in the worksheets are entirely my own.
