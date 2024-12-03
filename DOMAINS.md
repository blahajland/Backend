
The API will interact with the Porkbun API for DNS management operations

---

## Endpoints and Functionality

### **1. `/domains/login`**
- **Method:** `POST`
- **Authentication:** None
- **Functionality:** 
  - Accepts a username.
  - Verifies the username exists in the `users` collection
  - Sends a login email to `<username>@blahaj.land` containing a temporary token
  - The temporary token is stored in the `tokens` collection with a 6-hour expiration, the token should also be tied to the username in the collectin

- **Input:**
  ```json
  {
    "username": "user1"
  }
  ```
- **Output (Success):**
  ```json
  {
    "message": "Login email sent successfully."
  }
  ```
- **Output (Failure):**
  ```json
  {
    "error": "Username not found."
  }
  ```

---

### **2. `/domains/register`**
- **Method:** `POST`
- **Authentication:** JWT Required
- **Functionality:**
  - Allows users to register a new subdomain and its initial records (A and CAA)
  - Validates the subdomain does not already exist
  - Checks the user's tier to ensure they have not exceeded their subdomain limit
  - Stores the subdomain in the `domains` collection, along with its associated records

- **Input:**
  ```json
  {
    "subdomain": "example",
    "ip": "192.168.1.1"
  }
  ```
- **Output (Success):**
  ```json
  {
    "message": "Subdomain registered successfully."
  }
  ```
- **Output (Failure):**
  ```json
  {
    "error": "Subdomain already exists or limit exceeded."
  }
  ```

---

### **3. `/domains/edit`**
- **Method:** `PUT`
- **Authentication:** JWT Required
- **Functionality:**
  - Modifies the IP address of an existing A record for the user’s subdomain through the porkbun API
  - Validates the subdomain belongs to the authenticated user
  - Updates the `domains` collection with the new IP address

- **Input:**
  ```json
  {
    "subdomain": "example",
    "newIP": "192.168.1.100"
  }
  ```
- **Output (Success):**
  ```json
  {
    "message": "Subdomain updated successfully."
  }
  ```
- **Output (Failure):**
  ```json
  {
    "error": "Subdomain does not belong to the user or does not exist."
  }
  ```

---

### **4. `/domains/list`**
- **Method:** `GET`
- **Authentication:** JWT Required
- **Functionality:**
  - Retrieves all subdomains and records associated with the authenticated user
  - Pulls data from the `domains` collection

- **Output (Success):**
  ```json
  [
    {
      "subdomain": "example",
      "records": [
        {
          "type": "A",
          "value": "192.168.1.1"
        },
        {
          "type": "CAA",
          "value": "0 issue \"letsencrypt.org\""
        }
      ],
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
  ```

---

### **5. `/domains/delete`**
- **Method:** `DELETE`
- **Authentication:** JWT Required
- **Functionality:**
  - Deletes a specific subdomain and its associated records
  - Validates the subdomain belongs to the authenticated user
  - Removes the subdomain from the `domains` collection and deletes the records from Porkbun

- **Input:**
  ```json
  {
    "subdomain": "example"
  }
  ```
- **Output (Success):**
  ```json
  {
    "message": "Subdomain deleted successfully."
  }
  ```
- **Output (Failure):**
  ```json
  {
    "error": "Subdomain does not belong to the user or does not exist."
  }
  ```

---

### **6. `/domains/purge`**
- **Method:** `DELETE`
- **Authentication:** JWT Required
- **Functionality:**
  - Deletes all subdomains and associated records owned by the authenticated user
  - Iterates through the `domains` collection and removes all entries tied to the user

- **Output (Success):**
  ```json
  {
    "message": "All subdomains deleted successfully."
  }
  ```
- **Output (Failure):**
  ```json
  {
    "error": "Failed to purge subdomains."
  }
  ```

---

### **7. `/domains/admin/<action>`**
- **Method:** `POST`, `PUT`, `GET`, `DELETE`
- **Authentication:** Admin JWT Required
- **Functionality:**
  - Mirrors `/domains/register`, `/domains/edit`, `/domains/list`, `/domains/delete`, and `/domains/purge`, but includes an additional `username` parameter to specify which user's records to manage

- **Example Admin Input for Register:**
  ```json
  {
    "username": "user1",
    "subdomain": "example",
    "ip": "192.168.1.1"
  }
  ```
- **Output:**
  ```json
  {
    "message": "Subdomain registered successfully for user1."
  }
  ```

---

## Data Storage

### **MongoDB Collections**

1. **Users Collection (`users`):**
   - **Fields:**
     - `username`: Unique identifier
     - `email`: User email address
     - `tier`: User tier (free/paid)
     - `created_at`: Timestamp
   - **Purpose:** Stores user data for validation and tier enforcement

2. **Tokens Collection (`tokens`):**
   - **Fields:**
     - `username`: Associated username
     - `token`: Temporary login token
     - `expires_at`: Expiration timestamp
   - **Purpose:** Manages temporary login tokens

3. **Domains Collection (`domains`):**
   - **Fields:**
     - `subdomain`: Unique subdomain
     - `owner`: Associated username
     - `records`: List of DNS records (e.g., A, CAA)
     - `created_at`: Timestamp
   - **Purpose:** Tracks subdomains and their records

---

## TO-DO List

1. **Authentication:**
   - Implement `/domains/login` endpoint to generate and validate temporary login tokens
   - Secure endpoints with JWT authentication for both users and admins

2. **DNS Record Management:**
   - Develop endpoints for subdomain registration, editing, deletion, and purging
   - Integrate MongoDB for tracking subdomains and their records
   - Ensure actions validate against user tier limits

3. **Admin Functionality:**
   - Extend endpoints to allow admins to manage user-specific records

4. **Porkbun API Integration:**
   - Add logic to interact with Porkbun API for DNS operations:
     - Create records
     - Edit records
     - Delete records

5. **Error Handling and Logging:**
   - Log errors and successful operations to a designated logging system
   - Implement user-friendly error messages
