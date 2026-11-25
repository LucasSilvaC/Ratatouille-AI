\getenv api_db DJANGO_DB_NAME
\getenv api_user DJANGO_DB_USER
\getenv api_password DJANGO_DB_PASSWORD
\getenv web_db WEB_DB_NAME

-- Serialize provisioners using the same maintenance database.
SELECT pg_advisory_lock(hashtextextended('ratatouille/django/database', 0));

SELECT :'api_db' IN (:'web_db', 'postgres', 'template0', 'template1')
       OR :'api_user' = current_user
       OR octet_length(:'api_db') > 63
       OR octet_length(:'api_user') > 63
       OR :'api_db' = ''
       OR :'api_user' = ''
       OR EXISTS (
           SELECT 1 FROM pg_roles
           WHERE rolname = :'api_user'
             AND (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls OR NOT rolcanlogin)
       )
       OR EXISTS (
           SELECT 1 FROM pg_database
           WHERE datname = :'api_db' AND pg_get_userbyid(datdba) <> :'api_user'
       ) AS invalid_config
\gset
\if :invalid_config
DO $$ BEGIN RAISE EXCEPTION 'Use a dedicated Django database and unprivileged owner role.'; END $$;
\endif

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'api_user', :'api_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'api_user')
\gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'api_db', :'api_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'api_db')
\gexec

SELECT format('REVOKE CONNECT ON DATABASE %I FROM PUBLIC', :'api_db')
\gexec
