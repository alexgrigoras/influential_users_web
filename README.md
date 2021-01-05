# Influential Users Web Application 

## Description
Web framework using Flask with Plotly Dash for Influential Users Application (Determining the most influential users from the multimedia social network YouTube by creating a graph with the most important users / channels)

## Architecture
The main components of the application are

1. <b>Information Gathering</b> - YouTube

1. <b>Data Storage</b> - MongoDB

1. <b>Analysis</b>
    1. ranking algorithms
    1. sentiment detection

## Application structure
```
influential_users_web
├── application
|   ├── __init__.py
|   ├── message_loader.py
|   ├── mongodb.py
|   ├── network_analysis.py
|   ├── plotly_display.py
|   └── youtube_api.py
├── pages
|   ├── auth_pages
|   |   ├── __init__.py
|   |   ├── change_password.py
|   |   ├── forgot_password.py
|   |   ├── login.py
|   |   ├── logout.py
|   |   └── register.py
|   ├── __init__.py
|   ├── analysis.py
|   ├── home.py
|   └── profile.py
├── static
|   ├── images
|   |   ├── influential_users.png
|   |   └── logo.png
├── utilities
|   ├── __init__.py
|   ├── auth.py
|   ├── config.py
|   └── keys.py
├── __init__.py
├── app.yaml
├── config.txt
├── create_tables.py
├── LICENSE
├── main.py
├── README.md
├── requirements.txt
├── server.py
└── users.db
```

## Resources

1. **Academic papers**


1. **Web content**
- [russellromney](https://github.com/russellromney) / [dash-auth-flow](https://github.com/russellromney/dash-auth-flow)
- [startbootstrap-sb-admin-2](https://github.com/StartBootstrap/startbootstrap-sb-admin-2)
- [network-graphs](https://plotly.com/python/network-graphs)
- [3d-network-graph](https://plotly.com/python/v3/3d-network-graph)

