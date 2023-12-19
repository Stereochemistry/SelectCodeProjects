/*SCRIPT BELOW ALREADY EXECUTED*/

INSERT INTO AM_Buffalo_Employers
SELECT DISTINCT e.id_number,
       e.pref_mail_name
FROM entity_rpt e,
     employment emp,
     address a
WHERE emp.employer_id_number = e.id_number
  AND e.id_number = a.id_number
  AND e.id_number NOT IN (SELECT id_number
                          FROM AM_Buffalo_Employers) -- This table was created by importing an Excel file from the client
  AND a.addr_pref_ind = 'Y'
  AND a.addr_status_code = 'A'
  AND SUBSTR(a.zipcode, 1, 5) IN (SELECT start_zip
                                  FROM   geo_zip
                                  WHERE  geo_code in ('YYYYY'));   -- Buffalo Eight Counties
COMMIT;

DELETE FROM AM_13378_DRIVING_1;
COMMIT;

DELETE FROM AM_13378_DRIVING_2;
COMMIT;

DELETE FROM AM_13378_DRIVING_3;
COMMIT;

--Relevant Buffalo Employers, Last Five Years
INSERT INTO AM_13378_DRIVING_1
SELECT e.id_number,
       e.pref_mail_name,
       be.pref_mail_name AS Employer_Name_A, --Used if Present in Buffalo Employment Table
       emp.employer_name1 AS Employer_Name_B, --Used if Otherwise
       emp.job_title,
       emp.date_added AS start_date,
       CASE
           WHEN TRUNC(emp.date_modified, 'MM') <> TRUNC(emp.date_added, 'MM') THEN emp.date_modified --Exclude positions that were entered incorrectly
           ELSE NULL
       END AS end_date,
       DENSE_RANK() OVER (PARTITION BY e.id_number ORDER BY emp.date_added, emp.job_title) AS Rank --Order by most recent job title
FROM entity_rpt e,
     AM_Buffalo_Employers be,
     employment emp,
     address_rpt a,
     degrees_rpt d
WHERE e.id_number = emp.id_number
  AND (emp.employer_id_number = be.id_number
       OR emp.employer_name1 = be.pref_mail_name)
  AND e.id_number = a.id_number
  AND e.id_number = d.id_number
  AND ((SUBSTR(TO_CHAR(emp.date_added), 8, 9) > '17' AND SUBSTR(TO_CHAR(emp.date_added), 8, 9) < '25')
        OR SUBSTR(emp.start_dt, 0, 4) > '2017')
  AND e.record_status_code IN ('A', 'E')
  AND e.record_type_code = 'AL'
  AND a.country_code NOT IN ('USA', ' ')
  AND SUBSTR(d.grad_dt, 0, 6) > '201812';
COMMIT;

--Update First Driving Table to Include Alumni w/ Work Addresses in Address Table
INSERT INTO AM_13378_DRIVING_1
SELECT e.id_number,
       e.pref_mail_name,
       NVL(e2.pref_mail_name, 'X') AS Employer_Name_A, --Used if Employer has AWA ID
       emp.employer_name1 AS Employer_Name_B, --Used Otherwise
       emp.job_title,
       emp.date_added AS start_date,
       CASE
           WHEN TRUNC(emp.date_modified, 'MM') <> TRUNC(emp.date_added, 'MM') THEN emp.date_modified
           ELSE NULL
       END AS end_date,
       DENSE_RANK() OVER (PARTITION BY e.id_number ORDER BY emp.date_added, emp.job_title) AS Rank --Order by most recent employer
FROM entity_rpt e,
     entity_rpt e2,
--     AM_Buffalo_Employers be,
     employment emp,
     address_rpt a,
     address_rpt a2,
     degrees_rpt d
WHERE e.id_number = emp.id_number
  AND e.id_number = a.id_number
  AND e.id_number = a2.id_number
  AND e.id_number = d.id_number
  AND emp.employer_id_number = e2.id_number(+)
  AND ((SUBSTR(TO_CHAR(emp.date_added), 8, 9) > '17' AND SUBSTR(TO_CHAR(emp.date_added), 8, 9) < '25')
        OR SUBSTR(emp.start_dt, 0, 4) > '2017')
  AND e.record_status_code IN ('A', 'E')
  AND e.record_type_code = 'AL'
  AND a.country_code NOT IN ('USA', ' ')
  AND SUBSTR(d.grad_dt, 0, 6) > '201812'
  AND a2.addr_type_code = 'B'
  AND SUBSTR(a2.zipcode, 1, 5) IN (SELECT start_zip
                                  FROM   geo_zip
                                  WHERE  geo_code in ('YYYYY'));
COMMIT;

--Second Driving Table Consisting of Current Employers
INSERT INTO AM_13378_DRIVING_2
SELECT e.id_number,
       e.pref_mail_name,
       e2.pref_mail_name AS Employer_Name_A, --Same logic as previous table
       emp.employer_name1 AS Employer_Name_B,
--       emp.job_title,
       DENSE_RANK() OVER (PARTITION BY e.id_number ORDER BY emp.date_added) AS Rank --Order by most recent employer
FROM entity_rpt e,
     entity_rpt e2,
     employment emp,
     AM_13378_DRIVING_1 am
WHERE e.id_number = emp.id_number
  AND e.id_number = am.id_number
  AND emp.employer_id_number = e2.id_number(+)
  AND emp.job_status_code = 'A'
  AND emp.employ_relat_code = 'PE';
COMMIT;

--Driving Table for Degree Information (I debated between doing things this way vs. using LISTAGG())
INSERT INTO AM_13378_DRIVING_3
SELECT am1.id_number,
       tms1.full_desc AS Degree,
       CASE
           WHEN d.degree_level_code = 'U' THEN 'Undergraduate'
           WHEN d.degree_level_code = 'G' THEN 'Graduate'
       END AS degree_level,
       tms2.full_desc AS Major1,
       tms3.full_desc AS Major2,
       tms4.full_desc AS Major3,
       d.grad_dt,
       DENSE_RANK() OVER (PARTITION BY am1.id_number ORDER BY d.degree_level_code, d.grad_dt, d.xsequence) AS Rank --Order by Highest, Most Recent Degree
FROM AM_13378_DRIVING_1 am1,
     degrees_rpt d,
--     address_rpt a,
     tms_degrees tms1,
     tms_majors tms2,
     tms_majors tms3,
     tms_majors tms4
WHERE am1.id_number = d.id_number
  AND d.degree_code = tms1.degree_code
  AND d.major_code1 = tms2.major_code
  AND d.major_code2 = tms3.major_code(+)
  AND d.major_code3 = tms4.major_code(+);
COMMIT;

DELETE FROM AM_13378_DRIVING_1 am
WHERE am.rank <> 1;
COMMIT;

DELETE FROM AM_13378_DRIVING_2 am
WHERE am.rank <> 1;
COMMIT;

DELETE FROM AM_13378_DRIVING_3 am
WHERE am.rank <> 1;
COMMIT;

DELETE FROM AM_13378;
COMMIT;

INSERT INTO AM_13378
SELECT DISTINCT am1.id_number,
       am1.pref_mail_name,
       am3.degree,
       am3.degree_level,
       am3.major1,
       am3.major2,
       am3.major3,
       am3.grad_dt,
       CASE
           WHEN am1.employer_name_A <> 'X' THEN REGEXP_REPLACE(am1.employer_name_A, '[0-9]+$', '') --Remove trailing numbers in Employer names
           ELSE REGEXP_REPLACE(am1.employer_name_B, '[0-9]+$', '')
       END as employer,
       am1.job_title,
       am1.start_date,
       am1.end_date,
       CASE
           WHEN am1.employer_name_A <> 'X' THEN REGEXP_REPLACE(am2.employer_name_A, '[0-9]+$', '')
           ELSE REGEXP_REPLACE(am2.employer_name_B, '[0-9]+$', '')
       END AS Current_Employer,
       BIO_TOOLS.handling(am1.id_number, ', ') AS handling
FROM --AM_Buffalo_Employers be,
     AM_13378_DRIVING_1 am1,
     AM_13378_DRIVING_2 am2,
     AM_13378_DRIVING_3 am3
WHERE am1.id_number = am2.id_number
  AND am1.id_number = am3.id_number;
