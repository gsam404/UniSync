# UniSync

**A Local University Publish-Subscribe Messaging System**

UniSync is a local university messaging application that enables offices and departments to distribute announcements to subscribers based on their selected topics.

The system uses a centralized, broker-based publish-subscribe architecture. Publishers send announcements to designated topics, while subscribers receive messages from the topics they follow. The broker uses SQLite to persist messages and subscriptions, ensuring that message history and pending deliveries are retained even after restarts.

## Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Running Terminal Clients](#running-terminal-clients)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)

## Features

- **Topic-Based Messaging** – Distributes announcements according to subscriber interests.
- **Persistent Message Storage** – Stores messages and subscriptions in an SQLite database.
- **Offline Message Delivery** – Maintains pending messages until delivery is acknowledged.
- **Message History** – Allows publishers and subscribers to review previous messages.
- **Desktop Interface** – Provides a graphical interface built with CustomTkinter.
- **Terminal Clients** – Supports publisher and subscriber interactions through the command line.

## System Requirements

| Requirement | Version / Description |
|---|---|
| Operating System | Windows 10 or later |
| Python | 3.10 or later |
| Git | Required for repository cloning |
| CustomTkinter | Required for the desktop interface |

The broker and terminal clients use Python's standard library and do not require additional third-party dependencies.

## Installation and Setup

### 1. Clone the Repository

Open PowerShell and execute:

```powershell
git clone https://github.com/gsam404/UniSync.git
cd UniSync
```

If the project is already available locally, open PowerShell in its root directory.

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### 3. Install Dependencies

Upgrade pip and install CustomTkinter:

```powershell
python -m pip install --upgrade pip
python -m pip install customtkinter
```

**Note:** The repository's `requirements.txt` is currently empty. CustomTkinter is only required to run the desktop interface.

## Running the Application

UniSync requires the broker to be running before connecting through the desktop interface or terminal clients.

### 1. Start the Broker

From the project root, execute:

```powershell
python run_broker.py
```

The broker listens on:

```text
127.0.0.1:5000
```

On its first execution, the broker automatically creates the SQLite database at:

```text
storage\unisync.db
```

Keep the broker terminal open while using the application.

### 2. Launch the Desktop Interface

Open a second PowerShell terminal in the project root.

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Launch the application:

```powershell
python main.py
```

### 3. Connect to UniSync

The application supports two user roles:

- **Subscriber:** Connect using a student number, select topics to follow, and view received-message history.
- **Publisher:** Select a registered university office and enter its corresponding publisher ID to send announcements to permitted topics.

To stop the application, close the GUI window. To stop the broker, press `Ctrl+C` in its terminal.

## Running Terminal Clients

UniSync also provides command-line interfaces for publishers and subscribers.

Ensure that the broker is running before launching either client.

### Subscriber Client

Open a separate terminal and execute:

```powershell
python -m clients.subscriber_client
```

The subscriber can:

- Enter a student number.
- Subscribe to topics.
- Unsubscribe from topics.
- View message history.

### Publisher Client

Open another terminal and execute:

```powershell
python -m clients.publisher_client
```

The publisher can:

- Select a university office.
- Enter the corresponding publisher ID.
- Publish announcements.
- View published-message history.

## Running Tests

To execute the project's automated tests, run:

```powershell
python -m unittest discover -s tests -v
```

Run this command from the project root with the virtual environment activated.

## Troubleshooting

| Issue | Possible Cause | Recommended Action |
|---|---|---|
| Broker offline / Connection refused | The broker is not running. | Start the broker using `python run_broker.py`. |
| Address already in use | Another process is using port `5000`. | Stop the other process or close the existing UniSync broker. |
| `ModuleNotFoundError: customtkinter` | CustomTkinter is not installed in the active environment. | Activate `.venv` and run `python -m pip install customtkinter`. |
| Publisher access denied | The publisher ID does not match the selected office. | Enter the correct ID for the selected office (e.g., `PUB-004` for the College of ICT). |

## Project Repository

[UniSync – GitHub Repository](https://github.com/gsam404/UniSync)

