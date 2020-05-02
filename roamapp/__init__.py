from .app import app
from .models import graph

def create_unique_constraint(label, property):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    query = query.format(label=label, property=property)

    create_unique_constraint("User", "username")
    create_unique_constraint("Restaurant", "name")

