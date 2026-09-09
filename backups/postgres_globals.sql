--
-- PostgreSQL database cluster dump
--

\restrict GZab8ghsqer21syAg8Q73cQa3baMB69W99S0K5qzf2MTbneQegw5JHHoS6NL0Vp

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE safcouser;
ALTER ROLE safcouser WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:XdVgb/MYHNrzX4By3cPW0w==$5iDUPo84n4JH4eAc/MGc6zzsKgnthgz0VceCaipM75I=:1gDPDRQ8NP7wXsPoRbQ52JA8fZ2BvcJBLCHEpBgsUIE=';






\unrestrict GZab8ghsqer21syAg8Q73cQa3baMB69W99S0K5qzf2MTbneQegw5JHHoS6NL0Vp

--
-- PostgreSQL database cluster dump complete
--

