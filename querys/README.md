# Funciones y procedimientos

Para simplificar la creación de la base de datos a la cual JasperServer hará las consultas necesarias para la creación del reporte, se desarrollaron una serie de Funciones y Procemientos los cuales se encuentran contenidos en el archivo *script_base.sql*.

El cotenido de dicho archivo es el siguiente:

*script_base.sql*
```sql
/*
* Sentencias para la creación de la base de datos a la cual
* Jasper hará las consultas para la creacion de cada grafica 
* en el reporte
*/

/*Creación de Base de Datos*/
DROP DATABASE IF EXISTS BaseJasper;
CREATE DATABASE BaseJasper;
USE BaseJasper;








DROP PROCEDURE IF EXISTS init_tablas;
DELIMITER $$
CREATE PROCEDURE init_tablas ()
BEGIN
/*Tabla de la grafica (Tickets abiertos vs Tickets cerrados)*/
DROP TABLE IF EXISTS BaseJasper.tickets_abiertos_cerrados;
CREATE TABLE BaseJasper.tickets_abiertos_cerrados (gerencia VARCHAR(200), idGerencia INT, total_abiertos INT default 0, total_cerrados INT default 0);
/*Tabla de la grafica (Estado de los tickets vs Cantidad de tickets en ese estado)*/
DROP TABLE IF EXISTS BaseJasper.solicitudes_estado;
CREATE TABLE BaseJasper.solicitudes_estado (estado_nombre VARCHAR(200), total_solicitudes INT default 0);
/*Tabla de la grafica Gerencias y cantidad de tikckets en cada estado*/
DROP TABLE IF EXISTS BaseJasper.gerencias_estados;
CREATE TABLE BaseJasper.gerencias_estados (gerencia VARCHAR(200),
                                idGerencia int,
                                estado_new int default 0,
                                estado_closed_successful int default 0,
                                estado_closed_unsuccessful int default 0,
                                estado_open int default 0,
                                estado_removed int default 0,
                                estado_pending_reminder int default 0,
                                estado_pending_auto_close_mas int default 0,
                                estado_pending_auto_close_menos int default 0,
                                estado_merged int default 0,
                                estado_closed_with_workaround int default 0,
                                estado_Awaiting_Scheduled_Time int default 0,
                                estado_Awaiting_Precedent_Requirement int default 0,
                                estado_open_L2 int default 0,
                                estado_open_L3 int default 0,
                                estado_L1_follow_up int default 0,
                                estado_L1_follow_up_pending_reminder int default 0,
                                estado_closed_without_validation int default 0,
                                estado_closed_invalid_request int default 0,
                                estado_Awaiting_for_missing_information  int default 0,
                                estado_impact_analysis int default 0,
                                estado_application_for_team_leader_approval int default 0,
                                estado_application_for_business_risk_approval int default 0,
                                estado_Queued_L2 int default 0);

DROP TABLE IF EXISTS BaseJasper.solicitudes_pendientes_semanal;
CREATE TABLE BaseJasper.solicitudes_pendientes_semanal (fecha DATETIME, total_semanal INT, total_pendientes INT);

DROP TABLE IF EXISTS BaseJasper.tabla;
CREATE TABLE BaseJasper.tabla (dato INT);
INSERT INTO BaseJasper.tabla VALUES (1);
END $$
DELIMITER ;








/* INSERTS para cada tabla*/
/*-----Funcion para obtener el ultimo estado del ticket-------*/
DROP FUNCTION IF EXISTS ultimoEstado;
DELIMITER $$
CREATE FUNCTION ultimoEstado(id_ticket INT) RETURNS INT
BEGIN
RETURN (SELECT otrsdb.ticket_history.state_id
                FROM  otrsdb.ticket_history
                WHERE otrsdb.ticket_history.ticket_id = id_ticket AND 
                      (otrsdb.ticket_history.history_type_id IN (27,1))
                ORDER BY otrsdb.ticket_history.id DESC
                LIMIT 1);
END $$
DELIMITER ;

/*Tabla tickets_abiertos_cerrados*/
DROP PROCEDURE IF EXISTS insert_abiertos_cerrados;
DELIMITER $$
CREATE PROCEDURE insert_abiertos_cerrados ()
BEGIN
INSERT INTO BaseJasper.tickets_abiertos_cerrados SELECT otrsdb.queue.name,
                otrsdb.queue.id, 
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (11,16,4,6,23) THEN count(DISTINCT otrsdb.ticket.id) END) AS Abiertos,
                (CASE WHEN ultimoEstado(otrsdb.ticket.id)  IN (2,3,9,10,17,18) THEN count(DISTINCT otrsdb.ticket.id) END) AS Cerrados
            FROM otrsdb.ticket 
            INNER JOIN otrsdb.queue on otrsdb.ticket.queue_id = otrsdb.queue.id
            WHERE otrsdb.ticket.queue_id IN (1,2,3,5,8,9,11,12,13,14,15,16,17,18,20,21,22,23,24,25,27,28,29,32,33) /*AND 
                  otrsdb.ticket.create_time >= DATE_SUB("2018-08-13 18:00:00", INTERVAL 7 DAY) AND 
                  otrsdb.ticket.create_time <= "2018-08-13 18:00:00" /*Validacion para obtener solo los tickets de la semana*/
            GROUP BY otrsdb.queue.name,otrsdb.ticket.id;
END $$
DELIMITER ;

/*Tabla solicitudes_estado*/
DROP PROCEDURE IF EXISTS insert_solicitudes_estado;
DELIMITER $$
CREATE PROCEDURE insert_solicitudes_estado ()
BEGIN
INSERT INTO BaseJasper.solicitudes_estado SELECT
                                        otrsdb.ticket_state.name ,
                                        count(DISTINCT otrsdb.ticket.id)
                                FROM otrsdb.ticket_state,otrsdb.ticket
                                WHERE
                                        otrsdb.ticket_state.id = ultimoEstado(otrsdb.ticket.id) AND
                                        otrsdb.ticket.queue_id IN (1,2,3,5,8,9,11,12,13,14,15,16,17,18,20,21,22,23,24,25,27,28,29,32,33) /*AND
                                        otrsdb.ticket.create_time >= DATE_SUB("2018-08-13 18:00:00", INTERVAL 7 DAY) AND 
                                        otrsdb.ticket.create_time <= "2018-08-13 18:00:00" /*Validacion para obtener solo los tickets de la semana*/
                                GROUP BY otrsdb.ticket_state.name;
END $$
DELIMITER ;

/*Tabla gerencias_estados*/
DROP PROCEDURE IF EXISTS insert_gerencias_estados;
DELIMITER $$
CREATE PROCEDURE insert_gerencias_estados ()
BEGIN
INSERT INTO BaseJasper.gerencias_estados SELECT otrsdb.queue.name,
                otrsdb.queue.id,
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (1) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (2) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (3) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (4) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (5) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (6) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (7) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (8) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (9) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (10) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (11) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (12) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (13) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (14) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (15) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (16) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (17) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (18) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (19) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (20) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (21) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (22) THEN count(otrsdb.ticket.id) END),
                (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (23) THEN count(otrsdb.ticket.id) END)
        FROM    otrsdb.ticket,otrsdb.queue
        WHERE
                otrsdb.ticket.queue_id = otrsdb.queue.id AND
                otrsdb.ticket.queue_id IN (1,2,3,5,8,9,11,12,13,14,15,16,17,18,20,21,22,23,24,25,27,28,29,32,33) /*AND
                otrsdb.ticket.create_time >= DATE_SUB("2018-08-13 18:00:00", INTERVAL 7 DAY) AND 
                otrsdb.ticket.create_time <= "2018-08-13 18:00:00" /*Validacion para obtener solo los tickets de la semana*/
        GROUP BY otrsdb.queue.name,otrsdb.ticket.id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS insert_solicitudes_pendientes_semanal;
DELIMITER $$
CREATE PROCEDURE insert_solicitudes_pendientes_semanal ()
BEGIN
SET @temp := 0;
WHILE(@temp < 12) DO
SET @f_inicial := date_sub("2018-08-13 18:00:00", INTERVAL ((@temp + 1) * 7) DAY);
SET @f_final := date_sub("2018-08-13 18:00:00", INTERVAL (@temp * 7) DAY);
INSERT INTO BaseJasper.solicitudes_pendientes_semanal 
            SELECT DATE_FORMAT(@f_final,'%Y-%m-%d'),
                   (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (11,16,4,6,23) THEN count(DISTINCT otrsdb.ticket.id) END),
                   (CASE WHEN ultimoEstado(otrsdb.ticket.id) IN (16,6) THEN count(DISTINCT otrsdb.ticket.id) END)
                   FROM otrsdb.ticket
                   WHERE otrsdb.ticket.create_time >= @f_inicial AND otrsdb.ticket.create_time <= @f_final  
                   AND otrsdb.ticket.queue_id IN (1,2,3,5,8,9,11,12,13,14,15,16,17,18,20,21,22,23,24,25,27,28,29,32,33)
                   GROUP BY 1,otrsdb.ticket.id;
SET @temp := @temp + 1;
END WHILE;
END $$
DELIMITER ;

/*Procedimiento principal*/
DROP PROCEDURE IF EXISTS ingresar_registros;
DELIMITER $$
CREATE PROCEDURE ingresar_registros ()
BEGIN
CALL init_tablas();
CALL insert_abiertos_cerrados();
CALL insert_solicitudes_estado();
CALL insert_gerencias_estados();
CALL insert_solicitudes_pendientes_semanal();
SET lc_time_names = 'es_MX';
END $$
DELIMITER ;
/*Llamada a procedimiento principal ingresar_registros*/
CALL ingresar_registros();






/*SELECTS para el reporte*/
/*Grafica Total Solicitudes cerradas vs Solicitudes Abiertas*/
SELECT gerencia, sum(total_abiertos) as total_abiertos, sum(total_cerrados) as total_cerrados FROM tickets_abiertos_cerrados GROUP BY 1;

/*Grafica Total Solicitudes VS Estatus*/
SELECT estado_nombre, total_solicitudes FROM solicitudes_estado;

SELECT DATE_FORMAT(fecha,"%Y-%M-%d"), SUM(total_semanal) as total_abiertos, SUM(total_pendientes) as total_pendientes
                FROM solicitudes_pendientes_semanal 
                GROUP BY 1
                ORDER BY 1 ASC;


/*Los unicos estados que se consideran abiertos son:
* *new
* open
* pending reminder
* Awaiting Scheduled Time
* Awaiting Precedent Requirement
* L1_follow up pending reminder
* Queued L2
*/

/*Los unicos estados que se consideran cerrados son todos los close y merge*/

/*Grafica Gerencia de Desarrollo de Claro Pagos*/
SELECT gerencia, 
       sum(estado_new) as new,
       sum(estado_closed_successful) as closed_successful,
       sum(estado_closed_unsuccessful) as closed_unsuccessful, 
       sum(estado_open) as "open",
       sum(estado_removed) as removed,
       sum(estado_pending_reminder) as pending_reminder,
       sum(estado_pending_auto_close_mas) as pending_auto_close_mas,
       sum(estado_pending_auto_close_menos) as pending_auto_close_menos,
       sum(estado_merged) as merged,
       sum(estado_closed_with_workaround) as closed_with_workaround,
       sum(estado_Awaiting_Scheduled_Time) as Awaiting_Scheduled_Time,
       sum(estado_Awaiting_Precedent_Requirement) as Awaiting_Precedent_Requirement,
       sum(estado_open_L2) as open_L2,
       sum(estado_open_L3) as open_L3,
       sum(estado_L1_follow_up) as L1_follow_up,
       sum(estado_L1_follow_up_pending_reminder) as L1_follow_up_pending_reminder,
       sum(estado_closed_without_validation) as closed_without_validation,
       sum(estado_closed_invalid_request) as closed_invalid_request,
       sum(estado_Awaiting_for_missing_information) as Awaiting_for_missing_information,
       sum(estado_impact_analysis) as impact_analysis,
       sum(estado_application_for_team_leader_approval) as application_for_team_leader_approval,
       sum(estado_application_for_business_risk_approval) as application_for_business_risk_approval,
       sum(estado_Queued_L2) as Queued_L2
       FROM gerencias_estados WHERE idGerencia = 27 GROUP BY 1;

/*Grafica Gerencia de Desarrollo de Claro Shop*/
SELECT gerencia, 
       sum(estado_new) as new,
       sum(estado_closed_successful) as closed_successful,
       sum(estado_closed_unsuccessful) as closed_unsuccessful, 
       sum(estado_open) as "open",
       sum(estado_removed) as removed,
       sum(estado_pending_reminder) as pending_reminder,
       sum(estado_pending_auto_close_mas) as pending_auto_close_mas,
       sum(estado_pending_auto_close_menos) as pending_auto_close_menos,
       sum(estado_merged) as merged,
       sum(estado_closed_with_workaround) as closed_with_workaround,
       sum(estado_Awaiting_Scheduled_Time) as Awaiting_Scheduled_Time,
       sum(estado_Awaiting_Precedent_Requirement) as Awaiting_Precedent_Requirement,
       sum(estado_open_L2) as open_L2,
       sum(estado_open_L3) as open_L3,
       sum(estado_L1_follow_up) as L1_follow_up,
       sum(estado_L1_follow_up_pending_reminder) as L1_follow_up_pending_reminder,
       sum(estado_closed_without_validation) as closed_without_validation,
       sum(estado_closed_invalid_request) as closed_invalid_request,
       sum(estado_Awaiting_for_missing_information) as Awaiting_for_missing_information,
       sum(estado_impact_analysis) as impact_analysis,
       sum(estado_application_for_team_leader_approval) as application_for_team_leader_approval,
       sum(estado_application_for_business_risk_approval) as application_for_business_risk_approval,
       sum(estado_Queued_L2) as Queued_L2
       FROM gerencias_estados WHERE idGerencia in (14,16,28) GROUP BY 1;

/*Grafica Gerencia de Plataforma y Tramites Administrativos*/
SELECT gerencia, 
       sum(estado_new) as new,
       sum(estado_closed_successful) as closed_successful,
       sum(estado_closed_unsuccessful) as closed_unsuccessful, 
       sum(estado_open) as "open",
       sum(estado_removed) as removed,
       sum(estado_pending_reminder) as pending_reminder,
       sum(estado_pending_auto_close_mas) as pending_auto_close_mas,
       sum(estado_pending_auto_close_menos) as pending_auto_close_menos,
       sum(estado_merged) as merged,
       sum(estado_closed_with_workaround) as closed_with_workaround,
       sum(estado_Awaiting_Scheduled_Time) as Awaiting_Scheduled_Time,
       sum(estado_Awaiting_Precedent_Requirement) as Awaiting_Precedent_Requirement,
       sum(estado_open_L2) as open_L2,
       sum(estado_open_L3) as open_L3,
       sum(estado_L1_follow_up) as L1_follow_up,
       sum(estado_L1_follow_up_pending_reminder) as L1_follow_up_pending_reminder,
       sum(estado_closed_without_validation) as closed_without_validation,
       sum(estado_closed_invalid_request) as closed_invalid_request,
       sum(estado_Awaiting_for_missing_information) as Awaiting_for_missing_information,
       sum(estado_impact_analysis) as impact_analysis,
       sum(estado_application_for_team_leader_approval) as application_for_team_leader_approval,
       sum(estado_application_for_business_risk_approval) as application_for_business_risk_approval,
       sum(estado_Queued_L2) as Queued_L2
       FROM gerencias_estados WHERE idGerencia in (5,8,15,16,20,21,22,23) GROUP BY 1;

/*Grafica Subdirección Corporativa de Iniciativas Digitales*/
SELECT gerencia, 
       sum(estado_new) as new,
       sum(estado_closed_successful) as closed_successful,
       sum(estado_closed_unsuccessful) as closed_unsuccessful, 
       sum(estado_open) as "open",
       sum(estado_removed) as removed,
       sum(estado_pending_reminder) as pending_reminder,
       sum(estado_pending_auto_close_mas) as pending_auto_close_mas,
       sum(estado_pending_auto_close_menos) as pending_auto_close_menos,
       sum(estado_merged) as merged,
       sum(estado_closed_with_workaround) as closed_with_workaround,
       sum(estado_Awaiting_Scheduled_Time) as Awaiting_Scheduled_Time,
       sum(estado_Awaiting_Precedent_Requirement) as Awaiting_Precedent_Requirement,
       sum(estado_open_L2) as open_L2,
       sum(estado_open_L3) as open_L3,
       sum(estado_L1_follow_up) as L1_follow_up,
       sum(estado_L1_follow_up_pending_reminder) as L1_follow_up_pending_reminder,
       sum(estado_closed_without_validation) as closed_without_validation,
       sum(estado_closed_invalid_request) as closed_invalid_request,
       sum(estado_Awaiting_for_missing_information) as Awaiting_for_missing_information,
       sum(estado_impact_analysis) as impact_analysis,
       sum(estado_application_for_team_leader_approval) as application_for_team_leader_approval,
       sum(estado_application_for_business_risk_approval) as application_for_business_risk_approval,
       sum(estado_Queued_L2) as Queued_L2
       FROM gerencias_estados WHERE idGerencia in (28,29) GROUP BY 1; /*falta el id de Claro Musica*/

/*Grafica Triara */
SELECT gerencia, 
       sum(estado_new) as new,
       sum(estado_closed_successful) as closed_successful,
       sum(estado_closed_unsuccessful) as closed_unsuccessful, 
       sum(estado_open) as "open",
       sum(estado_removed) as removed,
       sum(estado_pending_reminder) as pending_reminder,
       sum(estado_pending_auto_close_mas) as pending_auto_close_mas,
       sum(estado_pending_auto_close_menos) as pending_auto_close_menos,
       sum(estado_merged) as merged,
       sum(estado_closed_with_workaround) as closed_with_workaround,
       sum(estado_Awaiting_Scheduled_Time) as Awaiting_Scheduled_Time,
       sum(estado_Awaiting_Precedent_Requirement) as Awaiting_Precedent_Requirement,
       sum(estado_open_L2) as open_L2,
       sum(estado_open_L3) as open_L3,
       sum(estado_L1_follow_up) as L1_follow_up,
       sum(estado_L1_follow_up_pending_reminder) as L1_follow_up_pending_reminder,
       sum(estado_closed_without_validation) as closed_without_validation,
       sum(estado_closed_invalid_request) as closed_invalid_request,
       sum(estado_Awaiting_for_missing_information) as Awaiting_for_missing_information,
       sum(estado_impact_analysis) as impact_analysis,
       sum(estado_application_for_team_leader_approval) as application_for_team_leader_approval,
       sum(estado_application_for_business_risk_approval) as application_for_business_risk_approval,
       sum(estado_Queued_L2) as Queued_L2
       FROM gerencias_estados WHERE idGerencia = 18 GROUP BY 1;
```

**NOTA**: Es importante que el back de la base de datos de OTRS tenga el nombre de **otrsdb**. De igual forma es necesario señalar que la base de datos remota debe contar con un usuario llamado **jasperserver** cuya contraseña es **Mysqlroottoypassw0rd69play!**.