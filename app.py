import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
import json
import pandas as pd
import numpy as np 
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#################################################
# Database Setup
#################################################

engine = create_engine('sqlite:///cma-artworks.db', echo=False)

# Read artwork table
artwork_df = pd.read_sql(sql="select * from artwork", con=engine)
# Rename column appropriately for merge
artwork_dfr=artwork_df.rename(columns={"id":"artwork_id"})
# Read in artwork_creator table
artwork_creator_df = pd.read_sql(sql="select * from artwork__creator", con=engine)
# Read in artwork_department table
artwork_department_df = pd.read_sql(sql="select * from artwork__department", con=engine)
# Read in creator table
creator_df = pd.read_sql(sql="select * from creator", con=engine)
# Rename column appropriately for merge
creator_dfr = creator_df.rename(columns={"id":"creator_id"})
# Read in department table
department_df = pd.read_sql(sql="select * from department", con=engine)
# Rename column appropriately for merge
department_dfr = department_df.rename(columns={"id":"department_id"})

# Merge tables: artwork and artwork_creator
merged_table1 = pd.merge(artwork_dfr, artwork_creator_df, on="artwork_id")
# Merge artwork department table with new merged table above
merged_table2 = pd.merge(merged_table1, artwork_department_df, on="artwork_id")
# Merge creator table with new merged table above
merged_table3 = pd.merge(merged_table2, creator_dfr, on="creator_id")
# Merge department table with new merged table above
merged_table4 = pd.merge(merged_table3, department_dfr, on="department_id")

# Rename column for clarity
CMA_df = merged_table4.rename(columns={"name":"department_name"})
# Remove duplicate rows
CMA_df.drop_duplicates(keep=False,inplace=True) 
# Create Json 
j = (CMA_df.groupby(['artwork_id','accession_number','title','tombstone','department_id','department_name'], as_index=False)
             .apply(lambda x: x[['creator_id','role','description']].to_dict('r'))
             .reset_index()
             .rename(columns={0:'creator_info'})
             .to_json(orient='records'))

# Save json file to a variable
CMA_new = json.loads(j)

#Write json to file
with open('CMA_jjjj.json', 'w') as outfile:
    json.dump(CMA_new, outfile)




#################################################
# Routes
#################################################

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")



if __name__ == "__main__":
    app.run()