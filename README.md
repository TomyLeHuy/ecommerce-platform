# Local Retail Platform

## 1. Project Vision

This project is a modern, decoupled web application designed to empower small, local retailers by providing them with the digital tools necessary to compete with large-scale e-commerce giants. The platform consists of two main components: a **B2B SaaS Platform** for retailers to manage their business online and a **B2C Online Marketplace** for customers, offering a unique, geo-fenced shopping experience.

The core mission is to bridge the digital divide for local retailers and foster a stronger connection between them and their surrounding community.

---

## 2. Core Features

### For Retailers (The SaaS Dashboard)
* **Simple Shop Builder:** An intuitive web app for retailers to build and customize their online storefront without technical expertise.
* **Inventory & Sales Management:** A comprehensive system for tracking product stock and analyzing detailed sales data (daily, weekly, yearly).
* **Automated Reordering:** An intelligent system that notifies retailers when to reorder products based on sales trends and stock levels.
* **DATEV Integration:** A crucial interface for German retailers to seamlessly export accounting data.
* **Real-time Order Notifications:** Instant alerts with all necessary shipping information when a sale is made.

### For Customers (The Marketplace)
* **Geo-based "Tinder" Search:** The central feature, displaying products exclusively from retailers within a user-defined radius (e.g., 150 km).
* **Favorites & Travel Function:** Allows customers to save their favorite shops and continue to browse and purchase from them, even when outside the shop's geographic radius.
* **Token Loyalty System:** A rewards program where customers earn tokens on purchases, which can be used as a payment method.
* **Digital Receipt Inbox:** All receipts are stored digitally in the user's profile, sorted, filterable, and with automatic tracking of return deadlines.

---

## 3. Technology Stack

This project is built using a modern, decoupled architecture to ensure scalability, maintainability, and a fast development cycle.


| Component      | Technology                                    | Rationale                                                                        |
| -------------- | --------------------------------------------- | -------------------------------------------------------------------------------- |
| **Architecture** | Decoupled / API-First ("Headless")            | [cite_start]Allows independent development and scaling of frontend and backend. [cite: 5008]              |
| **Backend** | Python / Django / Django REST Framework       | [cite_start]Rapid, secure development of the complex, data-driven retailer dashboard. [cite: 5011]        |
| **Frontend** | TypeScript / React / Next.js (with App Router) | [cite_start]Optimal for performance, SEO, and creating a modern user experience. [cite: 5014, 5015]             |
| **Database** | PostgreSQL with PostGIS (planned) / SQLite (current)  | [cite_start]Robust database with essential geo-spatial capabilities for search. [cite: 5019, 5020] |
| **Deployment** | Phased: PaaS (e.g., Heroku) → CaaS (Docker/K8s)     | [cite_start]Start fast with minimal ops, scale cost-effectively with full control later. [cite: 5022, 5023]     |

---

## 4. Getting Started: Local Development

Follow these steps to set up and run the project on your local machine.

### Prerequisites
* [Python 3.12+](https://www.python.org/downloads/)
* [Poetry](https://python-poetry.org/docs/#installation) for Python package management.
* [Node.js 18+](https://nodejs.org/) (which includes `npm`).

### One-Time Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/TomyLeHuy/ecommerce-platform
    cd local-retail-platform
    ```

2.  **Run the automated setup script:**
    This script will install all backend and frontend dependencies and set up the initial database.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    You will be prompted to create a password for the `admin` user during the setup.

### Running the Application

After the one-time setup is complete, you will need to run the backend and frontend servers simultaneously in **two separate terminals**.

**Terminal 1: Start the Backend**
```bash
cd backend
python manage.py runserver
```
The backend API will now be running on http://127.0.0.1:8000.

**Terminal 2: Start the Frontend**
```bash
cd ..
cd frontend
npm run dev
```
The frontend website will now be accessible at http://localhost:3000.

## 5. Project Structure
The project is organized as a monorepo with two primary packages:

- `./backend/`: The Django project containing all backend logic, API definitions, and database models.

- `./frontend/`: The Next.js project containing all user-facing components and pages.

