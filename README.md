# Influential Users Web Application 

## Description
Web framework using Flask with Plotly Dash for Influential Users Application (Determining the most influential users from the multimedia social network YouTube by creating a graph with the most important users / channels)

## Architecture
The main components of the application are

1. **Information Gathering** - Data:
    - YouTube API.

1. **Data Storage** - Database:
    - MongoDB;
    - SQLite.

1. **Analysis** - Ranking algorithms:
   - betweenness centrality;
   - degree centrality;
   - closeness centrality;
   - eigenvector centrality;
   - load centrality;
   - harmonic centrality;
   - pagerank;
   - voterank.

## Application structure
```
influential_users_web
├── application
|   ├── __init__.py
|   ├── database.py
|   ├── message_logger.py
|   ├── network_analysis.py
|   ├── network_display.py
|   └── web_crawler.py
├── assets
|   ├── css
|   ├── image
|   └── vendor
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
|   ├── dashboard.py
|   ├── home.py
|   └── profile.py
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
- [startbootstrap](https://github.com/startbootstrap) / [startbootstrap-sb-admin-2](https://github.com/startbootstrap/startbootstrap-sb-admin-2)
- [startbootstrap](https://github.com/startbootstrap) / [startbootstrap-landing-page](https://github.com/startbootstrap/startbootstrap-landing-page)
- [UIdeck](https://uideck.com/) (images)
- [Social media mess image](https://www.pinterest.com/pin/75716837455100871/)
- [network-graphs](https://plotly.com/python/network-graphs)
- [3d-network-graph](https://plotly.com/python/v3/3d-network-graph)

