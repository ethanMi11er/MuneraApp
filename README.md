# Munera: Integrated Task Management System

**Team:** The Django Developers  
**Group 11** — *Ethan • Tyler • Zack • Thomas • Adam*  

---

## 1. Introduction

**Munera** is a full-stack, web-based platform engineered to facilitate **project and task management** in a collaborative, structured, and scalable manner.  
The system is designed for teams that require transparency, accountability, and efficient coordination between managers and team members.

At its core, Munera introduces a **dual-role access model**:

- **Managers** oversee projects, assign tasks, and monitor progress metrics.
- **Team Members** engage through an optimized interface that provides clarity on assigned work, progress status, and deadlines.

The goal of Munera is to **eliminate friction** in task management by consolidating planning, communication, and execution into a unified, role-aware interface.  
This results in reduced coordination overhead and improved overall project throughput.

---

## 2. System Objectives

1. **Centralization** — Provide a single, web-accessible platform for managing all project activities.  
2. **Transparency** — Ensure managers and team members have role-appropriate visibility into task and project states.  
3. **Scalability** — Build on a modular stack that can evolve to support more complex organizations.  
4. **Usability** — Deliver an intuitive, responsive interface that minimizes cognitive load while maximizing task efficiency.  
5. **Security** — Leverage Django’s built-in authentication and authorization mechanisms for data integrity and access control.

---

## 3. System Architecture

Munera is structured as a **two-tier application** built on modern and industry-standard web technologies.

### 3.1 Backend

| Component | Technology | Purpose |
|------------|-------------|----------|
| **Language** | Python 3.x | Core backend logic, data modeling, and API management |
| **Framework** | Django | Provides MVC structure, authentication, ORM, and routing |
| **API Layer** | Django REST Framework (DRF) | Exposes data models to the frontend through RESTful endpoints |
| **Database** | SQLite | Lightweight, serverless RDBMS suitable for development and testing |

The backend provides the **data models**, **business logic**, and **REST API endpoints** that connect the frontend to the underlying system.

### 3.2 Frontend

| Component | Technology | Purpose |
|------------|-------------|----------|
| **Language** | JavaScript (ES6+) | Core scripting for the UI |
| **Framework** | React | Builds a reactive, component-driven user interface |
| **Communication** | Axios / Fetch API | Handles requests between React and Django REST endpoints |

The frontend acts as the presentation layer, providing a responsive and role-driven experience for all users.

---

## 4. Data Model Design

The data architecture is founded on **relational principles**, ensuring normalized relationships and referential integrity between entities.

### 4.1 Entities

#### **User**

An extension of Django’s built-in `User` model with an additional field for user role differentiation.  

| Attribute | Type | Description |
|------------|------|-------------|
| `id` | Primary Key | Unique identifier for the user |
| `username` | String (Unique) | System login credential |
| `email` | String (Unique) | User’s contact address |
| `first_name` | String | User’s given name |
| `last_name` | String | User’s surname |
| `password` | Hashed String | Authentication credential |
| `role` | Enum(`Manager`, `Team Member`) | Defines permission level |

#### **Project**

Represents a unit of organizational work.  

| Attribute | Type | Description |
|------------|------|-------------|
| `id` | Primary Key | Unique identifier for each project |
| `name` | Text | Title of the project |
| `description` | Text | Project overview and objectives |
| `start_date` | Date | Project initiation date |
| `end_date` | Date | Expected completion date |
| `created_by` | Foreign Key → User | Project manager/owner |

#### **Task**

A discrete actionable item within a project’s scope.  

| Attribute | Type | Description |
|------------|------|-------------|
| `id` | Primary Key | Unique task identifier |
| `title` | Text | Task summary |
| `description` | Text | Task details |
| `status` | Enum(`To Do`, `In Progress`, `Done`) | Tracks workflow progression |
| `due_date` | Date | Completion deadline |
| `project` | Foreign Key → Project | Links task to parent project |
| `assigned_to` | Foreign Key → User | Person responsible for execution |

### 4.2 Relationships

- A **Manager** can create multiple **Projects**
- A **Project** can contain multiple **Tasks**
- A **Team Member** can be assigned to multiple **Tasks**

---

## 5. Functional Overview

### 5.1 Common Features

- Secure registration and login system  
- Unified dashboard summarizing relevant data  
- Role-based view rendering

### 5.2 Manager Features

- Project lifecycle management (create, update, delete)  
- Task assignment and deadline tracking  
- Team overview and progress metrics  
- Reporting dashboard for real-time insight  

### 5.3 Team Member Features

- Personalized dashboard listing assigned tasks  
- Real-time task status updates  
- Detailed task descriptions and deadlines  
- Contextual feedback and task progress visualization  

---

## 6. Development Methodology

Munera follows **Agile principles**, emphasizing iterative development and continuous integration.

**Version Control:** Git + GitHub  
**Issue Tracking:** Jira  
**Collaboration:** Branch-based workflow with pull requests for review  
**Testing:** Manual and automated integration testing before deployment  

---

## 7. Environment Setup and Configuration

### 7.1 System Requirements

| Requirement | Recommended Version |
|--------------|----------------------|
| **Python** | 3.10+ |
| **Node.js** | 18+ |
| **npm** | 9+ |
| **Git** | Latest |
| **Operating System** | Windows 10+, macOS, or Linux |

---

## 8. Project Setup Instructions

### 8.1 Repository Setup

Clone the project to your local environment:

```bash
git clone https://github.com/your-username/munera.git
cd munera
```
### 8.2 Virtual Environment Setup
```bash
python -m venv .venv
pip install django djangorestframework
```
### 8.2 Launching VENV 
```bash
.venv/Scripts/activate
```
### 8.3 Stopping VENV
```bash
deactivate
```
### 8.3 Starting Frontend Environment 
```bash
cd frontend
yarn
yarn run dev
```
