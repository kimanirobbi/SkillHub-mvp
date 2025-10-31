SkillHub-mvp/
│
├── .env
├── .gitignore
├── requirements.txt
├── manage.py
├── run.py
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── database.py
│   │
│   ├── routes.py              # Authentication + Dashboard routes
│   ├── geo_routes.py          # ✅ Map + Geo-location endpoints
│   ├── ai_routes.py           # ✅ AI-based skill matching
│   ├── payment_routes.py      # ✅ M-Pesa payment endpoints
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── map.html
│   │   └── payments.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── tailwind.css
│   │   │   └── style.css
│   │   ├── js/
│   │   │   ├── map.js
│   │   │   ├── ai_recommend.js
│   │   │   └── payment.js
│   │   └── images/
│   │       └── logo.png
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   └── recommender.py     # ✅ Simple AI recommendation system
│   │
│   ├── payments/
│   │   ├── __init__.py
│   │   └── mpesa_api.py       # ✅ Daraja API integration for payments
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   │
│   └── config.py              # Configuration setup
│
├── migrations/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_geo.py
│   ├── test_ai.py
│   └── test_payment.py
│
└── .github/
    └── workflows/
        └── ci.yml
