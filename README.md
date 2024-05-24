# API-for-workflow-management
Test task "API for workflow management", uses the concept of graphs. 
The system allows you to create 4 types of nodes. 
It includes an API using <b>FastAPI</b> and <b>Pydantic</b> for processing web requests, 
integration with the <b>networkX</b> library for graph management, 
and implementation of an algorithm for determining the path from the start to the end node.
### Built with
<ul>
    <li>FastAPI</li>
    <li>SQLAlchemy</li>
    <li>Pydantic</li>
    <li>networkX </li>
    <li>Docker</li>
    <li>Alembic</li>
    <li>PostgreSQL</li>
</ul>    


## Installation
1. Clone repository
    ```bash 
    git clone https://github.com/0xf0r3v3r/API-for-workflow-management.git
    ```
2. Change directory
    ```bash
    cd API-for-workflow-management
    ```
3. Build docker images
    ```bash
    docker-compose build
    ```
4. Run
    ```bash
    docker-compose up
    ```
5. Open in browser 
    ```bash
    http://127.0.0.1:8000/docs#
    ```




