## Trading Social App  

[![Open in Visual Studio Code](https://img.shields.io/badge/Open%20in-VS%20Code-blue?logo=visualstudiocode)](https://vscode.dev)
[![Contributors](https://img.shields.io/badge/contributors-1-brightgreen)](#)
[![Forks](https://img.shields.io/badge/forks-0-blue)](#)
[![Stars](https://img.shields.io/badge/stars-1-yellow)](#)
[![License](https://img.shields.io/badge/license-GPL--3.0-orange)](https://opensource.org/licenses/GPL-3.0)

---

**Trading Social** is a social networking application tailored for trading enthusiasts. The project is currently **under development**.

---

### Installation and Setup

Follow these steps to set up and run the application on your local machine.

---

### Prerequisites
Before proceeding, ensure the following software is installed on your system:
- **PostgreSQL**
- **Redis**
- **Python 3.10+**

---

### Steps to Run

1. **Set Up a Virtual Environment**  
   For **Windows**:  
```bash
   python -m venv venv
   .\venv\Scripts\activate

   For **MacOS or Liniux**:  
```bash
  python -m venv venv
  source venv/bin/activate


2️⃣. **Install Packs**
```bash
   pip install -r requirements.txt


3️⃣.**Create Databases**
## In PostgreSQL, create the following databases:

  ## user_database
  ## view_database
  ## signals_database
  ## comment_database
  ## Configure the Application
  ## Update all necessary values in the config.py file located in the config/ directory.

4️⃣. **Ensure database connection details are correctly specified for the databases created in the previous step**.
This step is critical—the application won't work without a properly configured config.py.

5️⃣.**Run the Application**
If all configurations are set up correctly, the application should run without issues.

```bash  uvicorn app.app:app --reload

6️⃣.**Testing**
The project includes automated tests to verify its functionality. If you follow the setup process, the application is guaranteed to work as expected.


