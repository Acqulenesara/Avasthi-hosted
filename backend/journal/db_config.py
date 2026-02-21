DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",           # or your actual DB username
    "password": "1234",  # replace with your actual password
    "dbname": "mental_health_bot"        # replace with your actual database name
}
# ---------------------------------------------------
# -- Table: public.journal_entries
#
# -- DROP TABLE IF EXISTS public.journal_entries;
#
# CREATE TABLE IF NOT EXISTS public.journal_entries
# (
#     id integer NOT NULL DEFAULT nextval('journal_entries_id_seq'::regclass),
#     user_id integer,
#     entry_date date,
#     mood text COLLATE pg_catalog."default",
#     entry text COLLATE pg_catalog."default",
#     sentiment_score double precision,
#     CONSTRAINT journal_entries_pkey PRIMARY KEY (id)
# )
#
# TABLESPACE pg_default;
#
# ALTER TABLE IF EXISTS public.journal_entries
#     OWNER to postgres;
# ------------------------------------------------------
#
#
#
# -- Table: public.journal_entries
#
# -- DROP TABLE IF EXISTS public.journal_entries;
#
# CREATE TABLE IF NOT EXISTS public.journal_entries
# (
#     id integer NOT NULL DEFAULT nextval('journal_entries_id_seq'::regclass),
#     user_id integer,
#     entry_date date,
#     mood text COLLATE pg_catalog."default",
#     entry text COLLATE pg_catalog."default",
#     sentiment_score double precision,
#     CONSTRAINT journal_entries_pkey PRIMARY KEY (id)
# )
#
# TABLESPACE pg_default;
#
# ALTER TABLE IF EXISTS public.journal_entries
#     OWNER to postgres;