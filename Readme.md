# Blockchain-Based E-Voting System with Facial Recognition

A prototype electronic voting application that combines **facial recognition**, a **Flask web application**, a **MySQL/MariaDB database**, and a **hash-linked vote ledger**. The project was designed to explore how identity verification and an append-only, blockchain-style record can be used together in an e-voting workflow.

## Overview

The application supports an end-to-end voting flow in which administrators can register voters and candidates, create elections, and view voting records. Voters authenticate through the web application, complete a facial-recognition check using a webcam, and then cast a vote for an active election.

Votes are stored in the relational database and a corresponding transaction is added to a hash-linked ledger. The application also checks whether a voter has already voted in a given election before accepting another vote.

## Key Features

- **Voter and candidate management** through a Flask-based administrative interface.
- **Election creation and status tracking** using MySQL/MariaDB.
- **Webcam-based facial verification** before access to the voting workflow.
- **Face encoding and classification** using `face_recognition` and a `RandomForestClassifier`.
- **Duplicate-vote prevention** by checking the voter ID and election ID before recording a vote.
- **Hash-linked vote ledger** using SHA-512 hashes and previous-hash references.
- **Vote aggregation and result display** for completed/current elections.
- **Server-rendered web UI** using Flask templates, HTML/CSS, JavaScript, and Bootstrap assets.

## Technology Stack

- **Backend:** Python, Flask
- **Computer Vision:** OpenCV, `face_recognition`
- **Machine Learning:** scikit-learn Random Forest
- **Database:** MySQL / MariaDB, PyMySQL / MySQLdb
- **Data Persistence:** Pickle model serialization
- **Hashing:** Python `hashlib` with SHA-512
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Development / Training:** Jupyter Notebook

## Project Structure

```text
E-Voter/
└── E-Voter/
    ├── Voter_Face_Collection.ipynb
    ├── RandomForestTrainingModel.ipynb
    ├── evoting.sql
    └── Web/
        ├── app.py
        ├── blockchain.py
        ├── camera.py
        ├── dbconnect.py
        ├── voterModel.sav
        ├── haarcascade_frontalface_default.xml
        ├── templates/
        └── static/
```

### Main Components

**`app.py`**  
Contains the Flask routes and the main application workflow, including authentication, election management, facial-verification flow, vote submission, and result rendering.

**`blockchain.py`**  
Implements the blockchain-style vote ledger. Each transaction records a voter ID, election ID, and nominee ID and links the new record to the previous block's hash.

**`camera.py`**  
Wraps OpenCV webcam access, live JPEG streaming, and image capture used during facial verification.

**`dbconnect.py`**  
Provides database connection and helper functions for inserts, updates, and queries against the `evoting` database.

**`Voter_Face_Collection.ipynb`**  
Collects multiple webcam images for a voter and stores them under the voter's unique ID for model training.

**`RandomForestTrainingModel.ipynb`**  
Extracts facial encodings with `face_recognition`, trains a Random Forest classifier, evaluates the model, and serializes the trained classifier to `Web/voterModel.sav`.

**`evoting.sql`**  
Defines the database schema for elections, nominees, voters, recorded votes, and the blockchain-style ledger.

## How the Voting Flow Works

1. An administrator registers voters and candidates and creates an election.
2. Facial images are collected for each voter using the face-collection notebook.
3. Facial encodings are extracted and used to train a Random Forest classifier.
4. A voter signs in to the Flask application.
5. The application verifies that an election is active and that the voter has not already voted in it.
6. The voter's face is captured using the webcam and classified by the trained model.
7. After successful verification, the voter selects a nominee.
8. The application records the vote in `electionconduct` and adds a corresponding transaction to the hash-linked `blockchain` table.
9. Vote totals can be queried and displayed through the application.

## Local Setup

### 1. Prerequisites

You will need:

- Python 3
- MySQL or MariaDB
- A webcam
- Jupyter Notebook if you want to recollect voter images or retrain the recognition model

### 2. Install Python Dependencies

The repository does not include a pinned dependency file, so install the libraries used by the application:

```bash
pip install flask opencv-python face-recognition scikit-learn pymysql mysqlclient matplotlib rsa keyboard notebook
```

> `face-recognition` depends on `dlib`, which may require additional system-level build tools depending on your operating system.

### 3. Create the Database

Create/import the database using the included SQL dump:

```text
evoting.sql
```

The application expects a database named `evoting`.

Database connection settings are currently defined directly in:

```text
Web/dbconnect.py
```

Update the host, username, password, port, or database name as needed for your local environment.

### 4. Train or Reuse the Facial Recognition Model

A serialized model is included as `voterModel.sav`. To create a new model:

1. Run `Voter_Face_Collection.ipynb` to capture voter images.
2. Run `RandomForestTrainingModel.ipynb` to generate face encodings and train the classifier.
3. Save the resulting model to `Web/voterModel.sav`.

### 5. Run the Application

From the `Web` directory:

```bash
python app.py
```

The Flask development server is configured to run at:

```text
http://127.0.0.1:8080
```

## Design Notes

The facial-recognition pipeline first converts each training image into a face embedding using the `face_recognition` library. These embeddings are used as features for a Random Forest classifier whose target is the voter's unique ID. During authentication, a newly captured image is encoded and classified using the serialized model.

The vote ledger is implemented as a **blockchain-style, hash-linked database structure**, rather than as a distributed blockchain network. A ledger record stores the previous hash, a generated current SHA-512 hash, the vote transaction, and a timestamp. The previous-hash reference creates a sequential chain of records in the database.

## Prototype Scope and Potential Improvements

This project was built as a prototype/academic implementation rather than a production election system. If I were evolving it for production use, I would prioritize:

- Replacing string-formatted SQL with parameterized queries or an ORM.
- Moving database credentials and Flask secrets to environment variables or a secrets manager.
- Hashing user passwords with a modern password-hashing algorithm.
- Adding CSRF protection, stronger session management, authorization checks, and audit logging.
- Building the ledger hash from the transaction contents, previous hash, and timestamp so integrity is cryptographically tied to the stored vote record.
- Adding automated unit, integration, and end-to-end tests.
- Pinning dependencies and adding a reproducible environment configuration.
- Measuring facial-verification false-acceptance and false-rejection rates across a larger evaluation set.
- Adding liveness detection and stronger protections against spoofing attacks.
- Separating application, data-access, authentication, and election-domain logic into clearer service layers.

## Code Sample Notes

This repository demonstrates work across several areas of software engineering, including:

- Designing a multi-component Python application.
- Integrating a web backend with computer-vision and machine-learning workflows.
- Building database-backed application logic and election-state management.
- Implementing webcam streaming and image capture.
- Serializing and using a trained ML model in an application workflow.
- Designing a hash-linked transaction record for vote history.

The implementation is intentionally presented as a prototype and reflects the design decisions and constraints of the project at the time it was developed.

## Author

**Prathyusha Naresh Kumar**
