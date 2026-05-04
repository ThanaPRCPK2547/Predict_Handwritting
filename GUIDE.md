# Frontend Integration Guide — Handwriting Recognition API

## Base URL
```
http://localhost:8000
```
Interactive docs available at: `http://localhost:8000/docs`

---

## Authentication

**All `/predict` and `/train` endpoints require a JWT Bearer token.**

### Register
```
POST /register
Content-Type: application/json

{
  "username": "string",     // 3-50 chars
  "password": "string",     // 6+ chars
  "role": "user" | "admin"  // default: "user"
}
```

### Login
```
POST /login
Content-Type: application/x-www-form-urlencoded

username=<username>&password=<password>

// Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**All authenticated requests must include this header:**
```
Authorization: Bearer <access_token>
```

---

## Canvas / Pixel Data Format

**This is the most important detail for the canvas component.**

All pixel data sent to the API must meet these requirements:

- **Size:** Exactly **28x28 = 784 pixels**
- **Format:** Either a flat array `[784]` or a 2D array `[[28], [28], ...]`
- **Values:** Numbers representing pixel brightness (0-255 or 0.0-1.0)
- **If values are 0-255:** The backend auto-normalizes to 0.0-1.0

**Example payload:**
```json
{
  "canvas": {
    "pixels": [0, 0.1, 0.5, ...]   // 784 values
  }
}
```

**Frontend tip:** If your canvas is larger than 28x28, you MUST downscale before sending. A common approach:
1. Capture canvas as image data
2. Resize to 28x28
3. Convert to grayscale pixel array
4. Send as the `pixels` field

---

## Endpoints

### 1. Predict a Digit
```
POST /predict
Authorization: Bearer <token>
Content-Type: application/json

{
  "canvas": {
    "pixels": [ ... 784 values ... ]
  }
}

// Response (200 OK):
{
  "prediction": 3,
  "confidence": 0.9234,
  "model_version": "active"
}
```

### 2. Train the Model (Real-time Learning)
```
POST /train
Authorization: Bearer <token>
Content-Type: application/json

{
  "canvas": {
    "pixels": [ ... 784 values ... ]
  },
  "label": 3        // correct digit, 0-9
}

// Response (202 Accepted):
{
  "status": "training_accepted",
  "model_version": "v_20260504124311",
  "message": "Model updated in-memory. Accuracy: 0.9100"
}
```

**Typical user flow:** Draw a digit → get prediction → user confirms/corrects label → send to `/train`

### 3. Health Check (No Auth Required)
```
GET /health

// Response:
{
  "status": "ok",
  "model_accuracy": 0.91
}
```

---

## Admin Endpoints
**Require `role: "admin"` on the user account.**

### Activate a Model Version
```
POST /admin/model/{version_id}/activate
Authorization: Bearer <admin_token>
```

### Update a Model Version
```
PATCH /admin/model/{version_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_active": true,
  "accuracy_log": 0.95   // optional
}
```

### Delete a Model Version
```
DELETE /admin/model/{version_id}
Authorization: Bearer <admin_token>
```
> Cannot delete the active version. Deactivate first.

---

## Key Behaviors to Know

1. **Real-time learning** — The model updates instantly on every `/train` call. The next `/predict` call will use the updated model immediately.

2. **Accuracy rollback** — If a training sample causes model accuracy to drop below 85%, the backend automatically reverts that training step silently.

3. **Model persistence** — Updated models are saved to PostgreSQL asynchronously. On app restart, the last saved model is automatically loaded.

4. **Only one active model** — Admins manage model versions, but only one version is `is_active` at any time. Activating a new version automatically deactivates all others.

5. **Token expiration** — JWT tokens expire after 30 minutes. Handle 401 responses by redirecting to login.

---

## Recommended Frontend Architecture

```
Canvas Component
  ↓ (28x28 pixel array)
Predict API → Show prediction + confidence
  ↓ (user confirms correct label)
Train API → Update accuracy display
  ↓
Accuracy History → Chart over time
```
