# Connectly API: MO-IT152 Integrative Programming and Technologies

**Student:** Harvey Punsalan
**Course:** MO-IT152 — Integrative Programming and Technologies

---

## About This Project

This is the Connectly API project built over the course of MO-IT152. It is a Django REST Framework based API that was developed incrementally across multiple milestones starting from basic CRUD operations, then adding data validation and relational models, then securing the API with HTTPS and token authentication, and finally implementing design patterns (Singleton and Factory) to improve the overall structure and maintainability of the codebase.

All code in this repository was written by me individually as a solo submission.

---

## Branch Information

The **latest and final version** of this project is on the `master` branch.

> All submissions, including the Milestone 1 deliverable, reflect the code currently on `master`.

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
2. Navigate into the project folder:
   ```bash
   cd connectly_project
   ```
3. Activate your virtual environment:
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

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/posts/users/create` | Create a new user |
| GET | `/posts/users/` | Get all users |
| POST | `/posts/posts/` | Create a new post |
| GET | `/posts/posts/` | Get all posts |
| POST | `/posts/comments/` | Create a comment |
| GET | `/posts/comments/` | Get all comments |
| GET | `/posts/posts/<id>/` | Get post detail |
| POST | `/posts/posts/create/` | Create post via Factory Pattern |

---

## Features Implemented

- Full CRUD operations for Users, Posts, and Comments
- DRF Serializers with custom field validation
- Token-based authentication
- HTTPS support via `runserver_plus`
- Object-level permission control using `IsPostAuthor`
- Password hashing with PBKDF2-SHA256
- Singleton Logger for centralized logging
- Singleton Config Manager
- Factory Pattern for post creation with metadata validation by post type (text, image, video)

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

- I used Claude to help me **understand the system diagrams** provided in the course materials. The diagrams were sometimes detailed and I wanted to make sure I had a clear picture of the architecture before I started coding, so I described the diagrams to Claude and asked for explanations to guide my understanding.
- I asked Claude to help me **identify what parts of the API I needed to test in Postman**. Since I was not fully familiar with API testing workflows at the start of the project, Claude helped me understand what endpoints to hit, what request bodies to use, and what responses to expect based on the diagrams.

**What I did NOT use Claude for:**

I did not use Claude to write or generate any of the code in this repository. All code written in VS Code including the models, views, serializers, permissions, factory, and singleton implementations was written entirely by me. The task instructions for this project were clear and detailed, and I was able to follow them and write the code on my own without any AI coding assistance.

---

**Grammarly**

I used Grammarly solely for grammar and spelling checks on my written worksheet responses. English is not my strongest area and I wanted to make sure my written answers were readable and clear. Grammarly was only used to correct grammar all the content, ideas, and answers in the worksheets are entirely my own.

