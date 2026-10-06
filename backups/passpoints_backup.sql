--
-- PostgreSQL database dump
--

\restrict qOJvEuTceVQPLRJbbPq4ZEOQ9iKMX3DIRouvt9wX5fH3TzN7JzWJmKTmwP0v9Vx

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attempts (
    id uuid NOT NULL,
    study_session_id uuid NOT NULL,
    duration_ms integer NOT NULL,
    accepted boolean NOT NULL,
    weak boolean NOT NULL,
    detected_patterns character varying[] NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.attempts OWNER TO postgres;

--
-- Name: graphical_passwords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.graphical_passwords (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    image_id character varying(255) NOT NULL,
    verifier text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean NOT NULL
);


ALTER TABLE public.graphical_passwords OWNER TO postgres;

--
-- Name: study_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_sessions (
    id uuid NOT NULL,
    user_id uuid,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    duration_ms integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.study_sessions OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean NOT NULL,
    email character varying(254)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
0003_graphical_hash_backfill
\.


--
-- Data for Name: attempts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attempts (id, study_session_id, duration_ms, accepted, weak, detected_patterns, created_at) FROM stdin;
\.


--
-- Data for Name: graphical_passwords; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.graphical_passwords (id, user_id, image_id, verifier, created_at, updated_at, is_active) FROM stdin;
cc984fc3-ba35-481b-a8e8-bbb1fedb2165	1635c86e-acb7-4eba-b4f0-c917acdc4c77	coast-sunset	$argon2id$v=19$m=19456,t=2,p=1$vUiwG0D8SBpGci2yZHTW6Q$UkeSXKu3B2roxqiU1M35E/rAFu/DS2kWmZasy9aOr5U	2026-09-28 13:35:29.920651-04	2026-09-28 13:35:29.920651-04	t
f865555a-27d9-4155-a4f1-52ea98d7fec6	5073e055-2c6f-4bb7-b878-71a7285aeff8	terracotta-house	$argon2id$v=19$m=19456,t=2,p=1$vhSTHEQJ/86FsNHi5OJWOw$JerKRVe9Ff7XrVMpajUrycNm6JBCH4zriPaPKWwPnFg	2026-09-28 13:46:17.272353-04	2026-09-28 13:46:17.272353-04	t
9d2a4286-92fb-4143-9161-e0f1680d5006	e7a4dd09-e910-462d-93f0-4425b7d4f4f3	desert-palms	$argon2id$v=19$m=19456,t=2,p=1$MGjeTkJtrVi2jJeR63U13w$f0INGZUO1h8sFmAQr+2jEu7O2AgvBr/XbVOwzxrM5dI	2026-09-28 14:50:35.194965-04	2026-09-28 14:50:35.194965-04	t
66cc7a9a-d0e6-49df-b3e0-a3ab66083087	b35c05e5-53c7-42a2-a687-4b2aa3c4c6c5	terracotta-house	$argon2id$v=19$m=19456,t=2,p=1$JPKBPzTsOrJQTcofM+rCfQ$yOVjbuyW21Tnf4zAVlH9fJXBBAxjOP8mnPcRffJgGjE	2026-09-30 11:12:36.512233-04	2026-09-30 11:12:36.512233-04	t
\.


--
-- Data for Name: study_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.study_sessions (id, user_id, started_at, completed_at, duration_ms, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, created_at, updated_at, is_active, email) FROM stdin;
1635c86e-acb7-4eba-b4f0-c917acdc4c77	liannis	$argon2id$v=19$m=19456,t=2,p=1$vUiwG0D8SBpGci2yZHTW6Q$UkeSXKu3B2roxqiU1M35E/rAFu/DS2kWmZasy9aOr5U	2026-09-28 13:35:29.920651-04	2026-09-28 13:35:29.920651-04	t	liannis@gmail.com
5073e055-2c6f-4bb7-b878-71a7285aeff8	bibi	$argon2id$v=19$m=19456,t=2,p=1$vhSTHEQJ/86FsNHi5OJWOw$JerKRVe9Ff7XrVMpajUrycNm6JBCH4zriPaPKWwPnFg	2026-09-28 13:46:17.272353-04	2026-09-28 13:46:17.272353-04	t	bibi@gmail.com
e7a4dd09-e910-462d-93f0-4425b7d4f4f3	nini	$argon2id$v=19$m=19456,t=2,p=1$MGjeTkJtrVi2jJeR63U13w$f0INGZUO1h8sFmAQr+2jEu7O2AgvBr/XbVOwzxrM5dI	2026-09-28 14:50:35.194965-04	2026-09-28 14:50:35.194965-04	t	nini@gmail.com
b35c05e5-53c7-42a2-a687-4b2aa3c4c6c5	fvdsvd	$argon2id$v=19$m=19456,t=2,p=1$JPKBPzTsOrJQTcofM+rCfQ$yOVjbuyW21Tnf4zAVlH9fJXBBAxjOP8mnPcRffJgGjE	2026-09-30 11:12:36.512233-04	2026-09-30 11:12:36.512233-04	t	dvs@gmail.com
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attempts attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attempts
    ADD CONSTRAINT attempts_pkey PRIMARY KEY (id);


--
-- Name: graphical_passwords graphical_passwords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.graphical_passwords
    ADD CONSTRAINT graphical_passwords_pkey PRIMARY KEY (id);


--
-- Name: study_sessions study_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_attempts_study_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attempts_study_session_id ON public.attempts USING btree (study_session_id);


--
-- Name: ix_graphical_passwords_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_graphical_passwords_user_id ON public.graphical_passwords USING btree (user_id);


--
-- Name: ix_study_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_sessions_user_id ON public.study_sessions USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: attempts attempts_study_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attempts
    ADD CONSTRAINT attempts_study_session_id_fkey FOREIGN KEY (study_session_id) REFERENCES public.study_sessions(id) ON DELETE CASCADE;


--
-- Name: graphical_passwords graphical_passwords_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.graphical_passwords
    ADD CONSTRAINT graphical_passwords_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: study_sessions study_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict qOJvEuTceVQPLRJbbPq4ZEOQ9iKMX3DIRouvt9wX5fH3TzN7JzWJmKTmwP0v9Vx

