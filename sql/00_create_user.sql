-- 00_create_user.sql
-- Run this ONCE as a DBA user (SYSTEM) connected to the pluggable database (XEPDB1 on Oracle XE 18c/21c).
-- Skip this file if your college already gave you an Oracle account to work in.

CREATE USER jobportal IDENTIFIED BY jobportal123
    DEFAULT TABLESPACE users
    QUOTA UNLIMITED ON users;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW,
      CREATE SEQUENCE, CREATE PROCEDURE, CREATE TRIGGER TO jobportal;
