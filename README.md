#  Drone Food Delivery Kenya — Full Stack Project

> Django REST Framework backend + React frontend for managing drone food delivery operations in Kenya.

---

## Project Structure

```
drone-food-delivery-kenya/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   └── drone_delivery/
│       ├── __init__.py
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── admin.py
│       ├── permissions.py
│       └── migrations/
│           └── 0001_initial.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       │   └── client.js
│       ├── components/
│       │   ├── DroneList.jsx
│       │   ├── OrderForm.jsx
│       │   ├── OrderStatus.jsx
│       │   └── ZoneMap.jsx
│       └── pages/
│           ├── Home.jsx
│           ├── Orders.jsx
│           └── Dashboard.jsx
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Django 5 + Django REST Framework |
| Database | PostgreSQL |
| Auth | djangorestframework-simplejwt |
| Frontend | React 18 + Vite |
| HTTP Client | Axios |
| Containerization | Docker + Docker Compose |

---

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### With Docker
```bash
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/operators/` | List all drone operators |
| GET | `/api/operators/:id/` | Single operator detail |
| GET/POST | `/api/orders/` | List or create orders |
| GET/PATCH | `/api/orders/:id/` | Order detail & status update |
| GET | `/api/zones/` | List delivery zones |
| GET | `/api/menu-items/` | Available food items |
| POST | `/api/auth/token/` | Obtain JWT token |
| POST | `/api/auth/token/refresh/` | Refresh JWT token |

---

## Environment Variables (`.env`)

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=drone_delivery
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

# Drone Food Delivery in Kenya — Research Guide

> A research and reference guide to drone logistics operators in Kenya, with a focus on the state of commercial food delivery via autonomous aerial systems.

---

## Overview

Commercial drone food delivery remains highly limited in Kenya. The local drone logistics industry overwhelmingly prioritizes **medical, humanitarian, and agricultural services** over consumer food delivery. While major international logistics companies have tested general retail or food models, practical infrastructure is still focused on emergency supply chains.

---

## Active Drone Logistics Operators

### [Zipline Kenya](https://www.zipline.com/)
The most active autonomous logistics operator in Kenya. Operating from a major distribution hub in **Chemelil, Kisumu County**, Zipline primarily delivers blood, vaccines, and medical items on demand.

- Globally operates a retail and food platform
- Previously partnered with **Jumia** to test retail deliveries in Africa
- Kenyan mandate is heavily focused on **healthcare and rural agricultural supply chains** (veterinary medicines, livestock materials)
- Not currently operating standard household food delivery in Kenya

---

### [The Good Drone Company](https://www.facebook.com/U.S.EmbassyNairobi/posts/innovation-partnership-and-opportunity-on-display-by-the-good-drone-company-a-us/1441773157994117/)
A **U.S.-backed** commercial cargo drone network expanding affordable aerial delivery solutions in Kenya.

- Target applications: healthcare, regional emergency response, infrastructure support
- Not focused on consumer-facing urban food delivery

---

### [Astral Aerial Solutions](https://astral-aerial.com/astral-aerial-and-partners-begin-drone-delivery-demonstrations-in-kenya/)
A Kenyan-registered operator holding a **KCAA Drone Operating Certification**, partnered with international entities including Swoop Aero and Skyports.

- Last-mile logistics demonstrations based out of **Tilisi**
- Focused on healthcare, agricultural spraying, and remote mapping
- Not operating food retail delivery

---

## Emerging & Specialized Concepts

### A&K Drone Delivery
An early-stage, on-demand **Food & Beverage logistics concept**.

- Leverages a standalone mobile app (**A&K Foods**) to partner with local kitchens
- Aims to extend food and drink brand reach using aerial drops
- Currently at concept/startup stage

---

### [Ando Foods](https://www.andofoods.co/)
A prominent digital **food delivery operating system** and cloud kitchen network active in Nairobi.

- Does **not** use drones — relies entirely on a traditional ground courier ecosystem
- Included for context as a benchmark of last-mile delivery innovation in Kenya

---

## Regulatory Landscape

### Kenya Civil Aviation Authority (KCAA)

Consumer drone food delivery has not expanded widely in Nairobi or Mombasa due to strict KCAA regulations:

| Constraint | Detail |
|---|---|
| **BVLOS Flights** | Beyond Visual Line of Sight operations are tightly controlled |
| **Urban Restrictions** | Built-up neighborhoods face significant flight limitations |
| **Rural Focus** | Permitted operations skew toward rural, critical-use deployments |
| **Licensing** | Operators must hold a KCAA Drone Operating Certification |

> Logistics operators like DHL note that drone use remains constrained to **niche, critical use cases in rural areas** rather than urban environments where food delivery demand is highest.

---

## Summary Table

| Company | Food Delivery? | Primary Focus | Status |
|---|---|---|---|
| Zipline Kenya |  (food tested globally) | Medical / Agricultural | Active |
| The Good Drone Company |  | Healthcare / Emergency | Expanding |
| Astral Aerial Solutions |  | Healthcare / Mapping | Active |
| A&K Drone Delivery |  (concept) | Food & Beverage | Early Stage |
| Ando Foods |  (ground only) | Cloud Kitchens / Food | Active |

---

## Further Reading & Sources

- [DHL Logistics Trend Radar – Drones](https://www.dhl.com/ke-en/home/innovation-in-logistics/logistics-trend-radar/drones-logistics.html)
- [The Star – Kenya's Fastest Medical Deliveries](https://www.the-star.co.ke/health/2025-11-15-the-silent-aircrafts-behind-kenyas-fastest-medical-deliveries)
- [Zipline hits one million deliveries](https://lakeregionbulletin.co.ke/2024/04/27/ziplines-drone-technology-hits-one-million-deliveries/)
- [Zipline & Jumia Drone Delivery Partnership](https://biznakenya.com/zipline-and-jumia-drone-delivery/)
- [Astral Aerial & Partners – Drone Demonstrations](https://astral-aerial.com/astral-aerial-and-partners-begin-drone-delivery-demonstrations-in-kenya/)
- [Asian Sky Group – Drone Deliveries in Kenya](https://www.asianskygroup.com/new-partnership-to-launch-drone-deliveries-in-kenya-319/)

---

## Contributing

If you have updated information on drone operators, new KCAA regulatory changes, or emerging startups in this space, feel free to open a pull request or issue.

---

## License

MIT — free to use, adapt, and share with attribution.