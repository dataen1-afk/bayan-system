# Testing Guide - Service Contract Management System

## Quick Testing Workflow

### 1. Test User Registration & Login

**Register as Admin:**
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin User","email":"admin@test.com","password":"admin123","role":"admin"}'
```

**Register as Client:**
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Client User","email":"client@test.com","password":"client123","role":"client"}'
```

**Login:**
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

Save the token from the response for subsequent requests.

### 2. Test Form Creation (Admin Only)

```bash
# Replace TOKEN with your admin JWT token
TOKEN="your-admin-token-here"

curl -X POST http://localhost:8001/api/forms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "client_id": "client-user-id-here",
    "fields": [
      {"label": "Company Name", "type": "text", "required": true},
      {"label": "Project Description", "type": "textarea", "required": true},
      {"label": "Budget", "type": "number", "required": false}
    ]
  }'
```

### 3. Test Form Submission (Client)

```bash
CLIENT_TOKEN="your-client-token-here"
FORM_ID="form-id-from-previous-step"

curl -X POST http://localhost:8001/api/forms/$FORM_ID/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -d '{
    "responses": {
      "Company Name": "TechCorp Inc",
      "Project Description": "Need a new website",
      "Budget": "50000"
    }
  }'
```

### 4. Test Quotation Creation (Admin)

```bash
TOKEN="your-admin-token-here"

curl -X POST http://localhost:8001/api/quotations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "form_id": "form-id-here",
    "client_id": "client-user-id",
    "client_email": "client@test.com",
    "price": 45000,
    "details": "Website Development Package with all features"
  }'
```

### 5. Test Quotation Approval (Client)

```bash
CLIENT_TOKEN="your-client-token-here"
QUOTATION_ID="quotation-id-here"

curl -X POST http://localhost:8001/api/quotations/$QUOTATION_ID/respond \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -d '{"status": "approved"}'
```

This will automatically generate a PDF contract!

### 6. Test Contract Download

```bash
CONTRACT_ID="contract-id-from-approval"

curl -X GET http://localhost:8001/api/contracts/$CONTRACT_ID/download \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  --output contract.pdf
```

## UI Testing

### Admin Dashboard Testing

1. Navigate to `http://localhost:3000`
2. Login with admin credentials: `admin@test.com` / `admin123`
3. **Forms Tab:**
   - Create a new form with client ID
   - Add multiple fields
   - Verify form appears in "All Forms" list
4. **Quotations Tab:**
   - Create quotation for submitted form
   - Verify quotation appears in list
5. **Contracts Tab:**
   - Verify generated contracts appear
   - Test PDF download

### Client Dashboard Testing

1. Navigate to `http://localhost:3000`
2. Login with client credentials: `client@test.com` / `client123`
3. **My Forms Tab:**
   - Verify assigned form appears
   - Click "Fill Form" button
   - Fill out all fields
   - Submit form
   - Verify status changes to "submitted"
4. **Quotations Tab:**
   - Verify received quotations appear
   - Review quotation details and price
   - Click "Approve" or "Reject"
   - Verify status updates
5. **Contracts Tab:**
   - Verify approved quotations generate contracts
   - Test PDF download functionality

## Feature Checklist

- [ ] User registration (admin & client)
- [ ] User login with JWT
- [ ] Admin can create forms
- [ ] Admin can view all forms
- [ ] Client can view their assigned forms only
- [ ] Client can fill and submit forms
- [ ] Admin can create quotations
- [ ] Email notification sent (if SMTP configured)
- [ ] Client can view quotations
- [ ] Client can approve/reject quotations
- [ ] Approved quotations generate PDF contracts
- [ ] Contracts can be downloaded
- [ ] Role-based access control works
- [ ] Logout functionality
- [ ] Error handling displays properly
- [ ] Loading states work correctly

## Expected Database Collections

After testing, MongoDB should have:

1. **users**: Admin and client user records
2. **forms**: Created forms with fields and responses
3. **quotations**: Created quotations with status
4. **contracts**: Generated contracts with PDF paths

## Verify Database

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/test_database

# Check collections
show collections

# View users
db.users.find()

# View forms
db.forms.find()

# View quotations
db.quotations.find()

# View contracts
db.contracts.find()
```

## Common Test Scenarios

### Scenario 1: Complete Workflow
1. Admin creates form for client
2. Client logs in and submits form
3. Admin creates quotation
4. Client approves quotation
5. Contract is generated
6. Both parties download contract

### Scenario 2: Rejection Flow
1. Admin creates quotation
2. Client rejects quotation
3. No contract is generated
4. Admin can create new quotation

### Scenario 3: Multiple Forms
1. Admin creates multiple forms for different clients
2. Each client sees only their forms
3. Forms are independently managed

## Performance Testing

Test with multiple concurrent requests:

```bash
# Create 10 users
for i in {1..10}; do
  curl -X POST http://localhost:8001/api/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"User $i\",\"email\":\"user$i@test.com\",\"password\":\"pass123\",\"role\":\"client\"}" &
done
wait
```

## Security Testing

- [ ] Verify tokens are required for protected endpoints
- [ ] Test invalid tokens are rejected
- [ ] Verify role-based access (client cannot access admin endpoints)
- [ ] Test password hashing (passwords not stored in plain text)
- [ ] Verify CORS settings
- [ ] Test XSS protection in form inputs

## Browser Compatibility

Test on:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

## Mobile Responsiveness

- [ ] Login page
- [ ] Dashboard navigation
- [ ] Form filling
- [ ] Quotation review
- [ ] Contract download
