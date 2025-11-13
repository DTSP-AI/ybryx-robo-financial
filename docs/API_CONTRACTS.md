# Ybryx Capital API Contracts

## Overview
This document defines the API contracts between the Next.js frontend and FastAPI backend for the Ybryx Capital robotics financing platform.

## Authentication
All endpoints will eventually support JWT-based authentication. Initial implementation can use API keys.

## Response Format
All responses use snake_case JSON formatting and include standard structure:

```json
{
  "success": boolean,
  "data": {},
  "error": null | { "message": string, "code": string }
}
```

---

## 1. Prequalification API

### POST /api/v1/prequalifications
Submit a prequalification application for equipment leasing.

**Request Body:**
```json
{
  "business_name": "string",
  "business_type": "llc" | "corporation" | "partnership" | "sole-proprietor",
  "industry": "logistics" | "agriculture" | "manufacturing" | "delivery" | "construction" | "retail",
  "email": "string",
  "phone": "string",
  "selected_equipment": ["string"],  // Array of equipment IDs
  "quantity": "1" | "2-5" | "6-10" | "11-20" | "20+",
  "annual_revenue": "0-500k" | "500k-1m" | "1m-5m" | "5m-10m" | "10m+",
  "business_age": "0-1" | "1-2" | "2-5" | "5+",
  "credit_rating": "excellent" | "good" | "fair" | "poor",
  "consent": boolean
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "application_id": "string (UUID)",
    "status": "pending" | "approved" | "declined" | "needs_review",
    "estimated_decision_date": "ISO8601 timestamp",
    "preliminary_terms": {
      "estimated_monthly_payment": number,
      "lease_term_months": number,
      "total_equipment_value": number
    } | null
  },
  "error": null
}
```

---

## 2. Robots/Equipment API

### GET /api/v1/robots
Retrieve equipment catalog with optional filtering.

**Query Parameters:**
- `search`: string (optional) - Search by name, manufacturer, or description
- `category`: "AMR" | "AGV" | "Drone" | "Robotic Arm" | "all" (optional)
- `use_case`: "logistics" | "agriculture" | "manufacturing" | "delivery" | "construction" | "retail" | "all" (optional)
- `page`: integer (default: 1)
- `limit`: integer (default: 20, max: 100)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "robots": [
      {
        "id": "string",
        "name": "string",
        "manufacturer": "string",
        "category": "string",
        "description": "string",
        "payload": "string",
        "autonomy_level": "string",
        "lease_from": "string",
        "use_case": "string",
        "specifications": {
          "weight": "string",
          "dimensions": "string",
          "battery_life": "string"
        },
        "image_url": "string (optional)"
      }
    ],
    "pagination": {
      "total": integer,
      "page": integer,
      "limit": integer,
      "total_pages": integer
    }
  },
  "error": null
}
```

### GET /api/v1/robots/{robot_id}
Get detailed information about a specific robot.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "manufacturer": "string",
    "category": "string",
    "description": "string",
    "payload": "string",
    "autonomy_level": "string",
    "lease_from": "string",
    "use_case": "string",
    "specifications": {},
    "related_robots": ["string"]
  },
  "error": null
}
```

---

## 3. Dealers API

### GET /api/v1/dealers
Retrieve authorized dealer listings.

**Query Parameters:**
- `zip_code`: string (optional) - Filter by ZIP code
- `specialty`: string (optional) - Filter by specialty
- `page`: integer (default: 1)
- `limit`: integer (default: 20, max: 100)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "dealers": [
      {
        "id": "string",
        "name": "string",
        "coverage": "string",
        "address": "string",
        "phone": "string",
        "email": "string",
        "specialties": ["string"],
        "zip_codes": ["string"],
        "distance_miles": number | null,
        "website": "string (optional)"
      }
    ],
    "pagination": {
      "total": integer,
      "page": integer,
      "limit": integer,
      "total_pages": integer
    }
  },
  "error": null
}
```

### POST /api/v1/dealers/match
Request dealer matching based on requirements.

**Request Body:**
```json
{
  "zip_code": "string",
  "equipment_type": "string",
  "industry": "string",
  "contact_info": {
    "name": "string",
    "email": "string",
    "phone": "string"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "matched_dealers": [
      {
        "id": "string",
        "name": "string",
        "contact": {},
        "match_score": number,
        "estimated_response_time": "string"
      }
    ],
    "notification_sent": boolean
  },
  "error": null
}
```

---

## 4. Industries API

### GET /api/v1/industries
Retrieve all supported industries.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "industries": [
      {
        "title": "string",
        "description": "string",
        "slug": "string",
        "icon": "string (lucide icon name)",
        "use_cases": ["string"],
        "benefits": [
          {
            "label": "string",
            "value": "string"
          }
        ]
      }
    ]
  },
  "error": null
}
```

### GET /api/v1/industries/{slug}
Get detailed information about a specific industry.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "title": "string",
    "description": "string",
    "slug": "string",
    "use_cases": ["string"],
    "benefits": [
      {
        "label": "string",
        "value": "string"
      }
    ],
    "recommended_robots": [
      {
        "id": "string",
        "name": "string",
        // ... full robot object
      }
    ],
    "case_studies": [
      {
        "company": "string",
        "summary": "string",
        "results": "string"
      }
    ] | []
  },
  "error": null
}
```

---

## 5. Future: Conversational Agent API

### POST /api/v1/agents/{agent_id}/chat
Interact with conversational agents (for future UI).

**Request Body:**
```json
{
  "message": "string",
  "thread_id": "string (optional)",
  "context": {
    "page": "string",
    "user_state": {}
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "string",
    "thread_id": "string",
    "agent_id": "string",
    "suggested_actions": [
      {
        "label": "string",
        "action": "string",
        "payload": {}
      }
    ] | null
  },
  "error": null
}
```

---

## Branding Notes

- All responses should reference "Ybryx Capital" as the company name
- Email domain: Use appropriate Ybryx domain
- All copy should reflect professional financial services tone

---

## Data Models Summary

### Prequalification Application
- Business information (name, type, industry)
- Contact details (email, phone)
- Equipment needs (types, quantities)
- Financial information (revenue, business age, credit)
- Consent flags

### Robot/Equipment
- Basic info (id, name, manufacturer, category)
- Technical specs (payload, autonomy level)
- Pricing (lease_from amount)
- Use case associations

### Dealer
- Contact information
- Service coverage (geographic, specialties)
- ZIP code coverage areas

### Industry
- Descriptive content
- Use cases and benefits
- Related equipment/robots
