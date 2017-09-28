--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET search_path = public, pg_catalog;

--
-- Name: email_status; Type: TYPE; Schema: public; Owner: cope
--

CREATE TYPE email_status AS ENUM (
    'pending',
    'dispatched',
    'sent',
    'refused'
);


ALTER TYPE public.email_status OWNER TO cope;

--
-- Name: permition_type; Type: TYPE; Schema: public; Owner: cope
--

CREATE TYPE permition_type AS ENUM (
    'read_own',
    'read',
    'edit',
    'delete',
    'create',
    'register',
    'invite',
    'inivteable'
);


ALTER TYPE public.permition_type OWNER TO cope;

--
-- Name: role_type; Type: TYPE; Schema: public; Owner: cope
--

CREATE TYPE role_type AS ENUM (
    'admin',
    'manager',
    'user'
);


ALTER TYPE public.role_type OWNER TO cope;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: app_user; Type: TABLE; Schema: public; Owner: cope; Tablespace: 
--

CREATE TABLE app_user (
    id integer NOT NULL,
    email character varying NOT NULL,
    pwd_hash character varying(60),
    role_id role_type,
    first_name character varying,
    last_name character varying,
    active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.app_user OWNER TO cope;

--
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: cope
--

CREATE SEQUENCE app_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.app_user_id_seq OWNER TO cope;

--
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cope
--

ALTER SEQUENCE app_user_id_seq OWNED BY app_user.id;


--
-- Name: email_queue; Type: TABLE; Schema: public; Owner: cope; Tablespace: 
--

CREATE TABLE email_queue (
    id integer NOT NULL,
    status email_status,
    sender character varying,
    created_at timestamp without time zone DEFAULT now(),
    recipient character varying,
    subject character varying,
    message text,
    data text
);


ALTER TABLE public.email_queue OWNER TO cope;

--
-- Name: email_queue_id_seq; Type: SEQUENCE; Schema: public; Owner: cope
--

CREATE SEQUENCE email_queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.email_queue_id_seq OWNER TO cope;

--
-- Name: email_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cope
--

ALTER SEQUENCE email_queue_id_seq OWNED BY email_queue.id;


--
-- Name: permition; Type: TABLE; Schema: public; Owner: cope; Tablespace: 
--

CREATE TABLE permition (
    id permition_type NOT NULL,
    mask bit(8)
);


ALTER TABLE public.permition OWNER TO cope;

--
-- Name: role; Type: TABLE; Schema: public; Owner: cope; Tablespace: 
--

CREATE TABLE role (
    id role_type NOT NULL,
    permitions bit(8)
);


ALTER TABLE public.role OWNER TO cope;

--
-- Name: user_details; Type: TABLE; Schema: public; Owner: cope; Tablespace: 
--

CREATE TABLE user_details (
    id integer NOT NULL,
    address character varying,
    postal_code character varying,
    date_of_birth date,
    avatar_fname character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.user_details OWNER TO cope;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: cope
--

ALTER TABLE ONLY app_user ALTER COLUMN id SET DEFAULT nextval('app_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: cope
--

ALTER TABLE ONLY email_queue ALTER COLUMN id SET DEFAULT nextval('email_queue_id_seq'::regclass);


--
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: cope
--

COPY app_user (id, email, pwd_hash, role_id, first_name, last_name, active, created_at, updated_at) FROM stdin;
1	admin@cope.com	$2a$06$0WKJ/myBw7c/zPuPAV2Jlulj.oV7bI6fHQ.I.X365tlbytsLHYqru	admin	super	user	t	2017-09-28 12:06:07.784439	2017-09-28 12:06:07.784439
\.


--
-- Name: app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cope
--

SELECT pg_catalog.setval('app_user_id_seq', 1, true);


--
-- Data for Name: email_queue; Type: TABLE DATA; Schema: public; Owner: cope
--

COPY email_queue (id, status, sender, created_at, recipient, subject, message, data) FROM stdin;
\.


--
-- Name: email_queue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cope
--

SELECT pg_catalog.setval('email_queue_id_seq', 1, false);


--
-- Data for Name: permition; Type: TABLE DATA; Schema: public; Owner: cope
--

COPY permition (id, mask) FROM stdin;
read_own	00000001
read	00000010
edit	00000100
delete	00001000
create	00010000
register	00100000
invite	01000000
inivteable	10000000
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: cope
--

COPY role (id, permitions) FROM stdin;
admin	01011111
manager	10000110
user	00100001
\.


--
-- Data for Name: user_details; Type: TABLE DATA; Schema: public; Owner: cope
--

COPY user_details (id, address, postal_code, date_of_birth, avatar_fname, created_at, updated_at) FROM stdin;
\.


--
-- Name: app_user_email_key; Type: CONSTRAINT; Schema: public; Owner: cope; Tablespace: 
--

ALTER TABLE ONLY app_user
    ADD CONSTRAINT app_user_email_key UNIQUE (email);


--
-- Name: app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: cope; Tablespace: 
--

ALTER TABLE ONLY app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- Name: permition_pkey; Type: CONSTRAINT; Schema: public; Owner: cope; Tablespace: 
--

ALTER TABLE ONLY permition
    ADD CONSTRAINT permition_pkey PRIMARY KEY (id);


--
-- Name: role_pkey; Type: CONSTRAINT; Schema: public; Owner: cope; Tablespace: 
--

ALTER TABLE ONLY role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: user_details_pkey; Type: CONSTRAINT; Schema: public; Owner: cope; Tablespace: 
--

ALTER TABLE ONLY user_details
    ADD CONSTRAINT user_details_pkey PRIMARY KEY (id);


--
-- Name: app_user_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cope
--

ALTER TABLE ONLY app_user
    ADD CONSTRAINT app_user_role_id_fkey FOREIGN KEY (role_id) REFERENCES role(id);


--
-- Name: user_details_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cope
--

ALTER TABLE ONLY user_details
    ADD CONSTRAINT user_details_id_fkey FOREIGN KEY (id) REFERENCES app_user(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

