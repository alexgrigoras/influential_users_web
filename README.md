# Influential Users Web Application 

## Description
Web framework using Flask with Plotly Dash for Influential Users Application (Determining the most influential users from the multimedia social network YouTube by creating a graph with the most important users / channels)

![Influential users image](https://www.researchgate.net/profile/Yujie_Fan5/publication/320885176/figure/fig10/AS:557869974392832@1510017974405/Identification-of-the-influential-users_W640.jpg)

Image taken from: <i>Fan, Yujie & Zhang, Yiming & Ye, Yanfang & Zheng, Wanhong. (2017). Social Media for
Opioid Addiction Epidemiology: Automatic Detection of Opioid Addicts from Twitter and
Case Studies, 1259-1267</i>

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

1. <b>Academic papers</b>

1. <b>Web content</b>
- https://github.com/russellromney/dash-auth-flow
- https://plotly.com/python/network-graphs/
- https://plotly.com/python/v3/3d-network-graph/

