CREATE TABLE nodes 
(
	id INTEGER, 
	lat TEXT, 
	lon TEXT, 
	user TEXT, 
	uid INTEGER, 
	version INTEGER, 
	changeset INTEGER, 
	'timestamp' TEXT   
); 

CREATE TABLE node_tags 
(
	key TEXT, 
	value TEXT, 
	type TEXT, 
	id INTEGER, 
	FOREIGN KEY (id) REFERENCES nodes (id) 
); 

CREATE TABLE ways
(
	id INTEGER,
	user TEXT, 
	uid INTEGER, 
	version INTEGER, 
	changeset INTEGER, 
	'timestamp' TEXT 
); 

CREATE TABLE way_tags
(
	key TEXT, 
	value TEXT, 
	type TEXT, 
	id INTEGER, 
	FOREIGN KEY (id) REFERENCES ways (id) 
); 

CREATE TABLE way_nodes
(	
	node_id INTEGER, 
	position INTEGER, 
	id INTEGER, 
	FOREIGN KEY (id) REFERENCES ways (id) 
); 

.mode csv 
.import nodes.csv nodes *FAILED*
.import nodes_tags.csv node_tags 
.import ways.csv ways *FAILED*
.import ways_tags.csv way_tags 
.import ways_nodes.csv way_nodes 