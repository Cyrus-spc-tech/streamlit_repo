# DBGUI - Database Management Interface

## About This Project

DBGUI is a simple database management application built with Python and Streamlit. It provides a graphical user interface for managing user data in a database without writing SQL queries manually.

This project demonstrates how to create a web-based database GUI that allows users to perform common database operations through an intuitive interface. It supports both SQLite (for local/lightweight usage) and MySQL (for more robust database needs).

## What Does It Do?

The application allows you to:
- Add new users to the database
- View all users in a table format
- Update existing user information
- Delete users by ID
- Search for specific users
- Visualize data with charts
- Inspect database table structure

## Technologies Used

- **Streamlit** - For creating the web interface
- **SQLite3** - Local database storage
- **MySQL** - Optional database backend
- **Pandas** - Data manipulation and display
- **Matplotlib** - Data visualization

## How to Run

1. Install required packages:
   ```bash
   pip install streamlit pandas matplotlib mysql-connector-python
   ```

2. Run the application:
   ```bash
   streamlit run guii.py
   ```

3. Open your browser at `http://localhost:8501`

## Project Purpose

This is a learning project that demonstrates:
- Building web applications with Streamlit
- Database CRUD operations in Python
- Working with both SQLite and MySQL
- Creating interactive data visualizations
- Designing user-friendly interfaces for database management
