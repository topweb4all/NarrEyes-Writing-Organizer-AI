from eralchemy2 import render_er

# Define your database structure
erd_markup = """
[users]
*id {label: "INTEGER"}
username {label: "VARCHAR"}
email {label: "VARCHAR"}
password_hash {label: "VARCHAR"}
created_at {label: "TIMESTAMP"}

[characters]
*id {label: "INTEGER"}
+user_id {label: "INTEGER"}
name {label: "VARCHAR"}
age {label: "INTEGER"}
role {label: "VARCHAR"}
description {label: "TEXT"}
personality {label: "TEXT"}
background {label: "TEXT"}
created_at {label: "TIMESTAMP"}

[chapters]
*id {label: "INTEGER"}
+user_id {label: "INTEGER"}
title {label: "VARCHAR"}
chapter_number {label: "INTEGER"}
content {label: "TEXT"}
word_count {label: "INTEGER"}
status {label: "VARCHAR"}
created_at {label: "TIMESTAMP"}
updated_at {label: "TIMESTAMP"}

[timeline]
*id {label: "INTEGER"}
+user_id {label: "INTEGER"}
event_title {label: "VARCHAR"}
event_date {label: "VARCHAR"}
description {label: "TEXT"}
+chapter_id {label: "INTEGER"}
created_at {label: "TIMESTAMP"}

[relationships]
*id {label: "INTEGER"}
+user_id {label: "INTEGER"}
+character1_id {label: "INTEGER"}
+character2_id {label: "INTEGER"}
relationship_type {label: "VARCHAR"}
description {label: "TEXT"}
created_at {label: "TIMESTAMP"}

users 1--* characters
users 1--* chapters
users 1--* timeline
users 1--* relationships
chapters 1--* timeline
characters 1--* relationships
"""

# Generate ERD
render_er(erd_markup, 'narreyes_erd.png')
print("ERD created successfully: narreyes_erd.png")
