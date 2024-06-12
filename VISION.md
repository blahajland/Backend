# UserCreationBackend

UserCreationBackend is a project aimed at streamlining the process of user and website creation through a user-friendly interface that interacts with YunoHost's CLI.

## 🚀 Technology Stack

- Node? 

### 📝 Handling Forms

Forms are essential for user and website creation. Our tool will provide a command-line interface (CLI) to handle these forms efficiently.

#### 👤 User Creation Form

The user creation form will capture the following details:

- **Username**: Must match the regex pattern `^[a-z0-9_\.]+$`
- **Display Name**: Must match the regex pattern `^([\^\\W_]{1,30}[ ,.'-]{0,3})+$`
- **Password**: Must match the regex pattern `^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$`
  - Option to generate a temporary password
- **Recovery Email**: 
  - Stored in a file for emergency use
- **Discord Username**

### 🛠️ CLI Commands

We will create CLI commands similar to YunoHost's actions. For example:

```bash
yunohost user create {user} -F {displayName} -p {password} -d blahaj.land -q 1000
```

## 📊 Database

Data will be stored in a database with the following fields:

- **Index**
- **Username**
- **Recovery Email**
- **Discord Username**
- **Tier**: (free, supporter, premium) (Maybe could interact with OpenCollective API?)
- **Timestamps**: In human-readable format (DATE type)

---
