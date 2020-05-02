#!env/bin/python
from roamapp import app
# export NEO4J_USERNAME=neo4j
# export NEO4J_PASSWORD=159753

app.secret_key = "test"
app.run(debug=True)
