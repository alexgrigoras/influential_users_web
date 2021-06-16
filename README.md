# Social Influencers Web Application 

## Description

Web application made for the dissertation thesis - Multimedia Social Networks Influential Users Identification.
The application determines the most influential users from the YouTube platform and creates a graph with the most important users.

## Installation

1. Install requirements
   ```sh
   pip install -r requirements.txt
   ```
2. Run server
   ```sh
   python main.py
   ```

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
├── logs
├── pages
|   ├── auth_pages
|   |   ├── __init__.py
|   |   ├── change_password.py
|   |   ├── forgot_password.py
|   |   ├── login.py
|   |   ├── logout.py
|   |   └── register.py
|   ├── __init__.py
|   ├── dashboard.py
|   ├── discover.py
|   ├── home.py
|   └── profile.py
├── utilities
|   ├── __init__.py
|   ├── auth.py
|   ├── config.py
|   ├── keys.py
|   └── utils.py
├── __init__.py
├── config.txt
├── create_tables.py
├── main.py
├── README.md
├── requirements.txt
├── server.py
└── users.db
```

## Resources

1. **Web content**
- [russellromney](https://github.com/russellromney) / [dash-auth-flow](https://github.com/russellromney/dash-auth-flow)
- [startbootstrap](https://github.com/startbootstrap) / [startbootstrap-sb-admin-2](https://github.com/startbootstrap/startbootstrap-sb-admin-2)
- [startbootstrap](https://github.com/startbootstrap) / [startbootstrap-landing-page](https://github.com/startbootstrap/startbootstrap-landing-page)
- [UIdeck](https://uideck.com/) (images)
- [Social media mess image](https://www.pinterest.com/pin/75716837455100871/)
- [network-graphs](https://plotly.com/python/network-graphs)
- [3d-network-graph](https://plotly.com/python/v3/3d-network-graph)