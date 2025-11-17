# SkillHub MVP Deployment Guide

This guide provides step-by-step instructions for deploying the SkillHub MVP application to Google App Engine with a PostgreSQL database hosted on Render.

## 1. Set Up Your PostgreSQL Database on Render

Render offers a free tier for PostgreSQL, which is perfect for your MVP.

1.  **Create a Render Account:** Sign up for a free account at [https://render.com/](https://render.com/).
2.  **Create a New PostgreSQL Database:**
    *   From your Render dashboard, click "New" and then "PostgreSQL".
    *   Give your database a unique name (e.g., `skillhub-db`).
    *   Select the free plan.
    *   Click "Create Database".
3.  **Get Your Database URL:**
    *   After your database is created, go to its dashboard.
    *   Under the "Connections" section, find the "External URL" and copy it. This is your `DATABASE_URL`.

## 2. Configure Your Application for Deployment

Before deploying to Google App Engine, you need to configure your application.

### a. Create `app.yaml`

Create a file named `app.yaml` in the root of your project with the following content:

```yaml
runtime: python310
entrypoint: gunicorn -b :$PORT "app:create_app()"

instance_class: F1

automatic_scaling:
  max_instances: 1

env_variables:
  FLASK_ENV: "production"
  SECRET_KEY: "<Your-Super-Secret-Key>"
  DATABASE_URL: "<Your-Render-Database-URL>"
```

**Important:**

*   Replace `<Your-Super-Secret-Key>` with a long, random string. You can generate one using a password manager or an online generator.
*   Replace `<Your-Render-Database-URL>` with the "External URL" you copied from Render.

### b. Update `requirements.txt`

Make sure your `requirements.txt` file includes `gunicorn`:

```
flask==3.0.3
flask_sqlalchemy==3.1.1
flask_login==0.6.3
pytest==8.4.2
python-dotenv==1.0.1
Flask-WTF==1.2.1
email-validator==2.1.0.post1
sentence-transformers
scikit-learn
numpy
flask-limiter>=4.0.0
flask-migrate>=4.0.5
gunicorn
```

## 3. Deploy to Google App Engine

1.  **Install the Google Cloud SDK:** Follow the instructions at [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install) to install the `gcloud` command-line tool.
2.  **Initialize the SDK:** Run `gcloud init` to log in to your Google account and select your project.
3.  **Deploy the Application:** In your terminal, at the root of your project, run the following command:

    ```bash
    gcloud app deploy
    ```

4.  **Run Database Migrations:** After your application is deployed, you need to run the database migrations. The easiest way to do this is to connect to the Google Cloud Shell and run the commands from there.
    *   Open the [Google Cloud Console](https://console.cloud.google.com/).
    *   Activate the Cloud Shell.
    *   Clone your repository into the Cloud Shell.
    *   Set up your virtual environment and install the dependencies.
    *   Set the `DATABASE_URL` environment variable in the Cloud Shell.
    *   Run the following command:

        ```bash
        flask db upgrade
        ```

Your application should now be live on Google App Engine, connected to your PostgreSQL database on Render.
