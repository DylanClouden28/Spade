# SPADE (Satellite Physical Attribute Data Enricher)

# COMPASS (COmbined Mass Properties And Satellite Sets)

# TAD (TLE Augmented Database)

# RAID (Reconciled Attribute & Information Database)

# Creating a Python Virtual Environment

A virtual environment isolates your project's dependencies.

### macOS & Linux

1.  **Create the environment:**

    ```bash
    python3 -m venv venv
    ```

2.  **Activate the environment:**
    ```bash
    source venv/bin/activate
    ```
    _(Your terminal prompt will now show `(venv)`)_

### Windows

1.  **Create the environment:**

    ```powershell
    python -m venv venv
    ```

2.  **Activate the environment:**
    ```powershell
    .\venv\Scripts\activate
    ```
    _(Your terminal prompt will now show `(venv)`)_

---

### After Activation

You can now install packages, which will be isolated to this project (All packages are inside the virtual enviroment).

```bash
pip install -r requirements.txt
```

### Deactivating

When you are finished, simply run:

```bash
deactivate
```
