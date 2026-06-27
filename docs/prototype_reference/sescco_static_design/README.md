# SESCCO Static HTML/CSS Prototype

This folder contains a static frontend prototype converted from the design direction.

## Pages

- `index.html` — Home page
- `about.html` — About Us
- `services.html` — Services Overview
- `service-detail.html` — Electrical Engineering service detail
- `projects.html` — Projects Overview
- `project-detail.html` — Fiber Optic project case study
- `clients-certifications.html` — Clients & Certifications
- `downloads.html` — Downloads / Documents center
- `contact.html` — Contact / Inquiry
- `admin-dashboard.html` — CMS dashboard

## Assets

- `assets/css/style.css` — full design system and page styles
- `assets/js/main.js` — simple UI interactions

## How to use

Open `index.html` in the browser. The files are static and can later be converted into Django templates.

## Django conversion idea

Move shared sections into:

- `templates/includes/header.html`
- `templates/includes/footer.html`
- `templates/includes/cta_banner.html`
- `templates/base.html`

Then convert each static page into an app template:

- `pages/home.html`
- `pages/about.html`
- `services/service_list.html`
- `services/service_detail.html`
- `projects/project_list.html`
- `projects/project_detail.html`
- `clients/clients_certifications.html`
- `documents/downloads.html`
- `inquiries/contact.html`
- `dashboard/dashboard.html`

## Important

This prototype is a coding reference. The final Django project should use database-driven content and CKEditor 5 only for rich body content.
