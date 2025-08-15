# SQLite Email Populator

This project creates an SQLite database named `emails.db` and populates it with fake email entries. It also includes functionality to check URLs associated with these emails.

## Project Structure

```
sqlite-email-populator
├── src
│   ├── populate_db.py
│   └── check_url.py
├── requirements.txt
└── README.md
```

## Requirements

To run this project, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

## Setting Up the Database

1. Navigate to the `src` directory.
2. Run the `populate_db.py` script to create and populate the `emails.db` database:

   ```
   python populate_db.py
   ```

## Checking URLs

After populating the database, you can check the URLs associated with the emails by running the `check_url.py` script:

```
python check_url.py
```

## Dependencies

This project requires the following Python packages:

- `sqlite3`
- `Faker`

Make sure to install these packages before running the scripts.