# Oiboymovie recommendation service

## What is it?

This service allows to get movie recommendations for a specific movie, finding similar ones in description and keywords, and for a specific user, based on his previous ratings.

## Installation

To get started, clone this repository on your machine using the following command:

```sh
git clone https://github.com/underfliper/oiboymovie-recommendation.git
```

Afterward, install virtualenv, to create an isolated virtual development environment:

```sh
pip install virtualenv
```

Next, run the command below inside the repository folder to create a virtual environment:

```sh
virtualenv venv
```

Activate the virtual environment:

```sh
# On Windows using Command Prompt or Powershell:
.\venv\Scripts\activate
```

```sh
# On Windows using Git Bash
source ./venv/Scripts/activate
```

```sh
# On Unix or MacOS:
source venv/bin/activate
```

Finally, install the required packages:

```sh
pip install -r requirements.txt
```

## Usage

Start the application:

```sh
flask run
```
