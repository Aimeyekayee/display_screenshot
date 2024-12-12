from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import func
from datetime import datetime
from fastapi import HTTPException
import json
from typing import Optional, List, Dict, Any, Union
import datetime as dt
import logging
import math


def convert_result(res):
    return [{c: getattr(r, c) for c in res.keys()} for r in res]


# def get_data(db: Session):
#     stmt = f"""
#         SELECT * FROM data_counter
#     """
#     try:
#         result = db.execute(text(stmt)).mappings().all()
#         return result
#     except Exception as e:
#         raise HTTPException(400,"Error get data :"+str(e))


def get_line(db: Session):
    stmt = f"""
        SELECT b.line_id, b.image_path ,c.line_fullname
        FROM public.image_path_screenshot b
        JOIN line c on b.line_id = c.line_id
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(400, "Error get section :" + str(e))


def get_linename(section_name: str, db: Session):
    stmt = f"""
        SELECT DISTINCT line_id, section_code, line_name from organizes
        WHERE section_name = '{section_name}'
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(400, "Error get section :" + str(e))


def get_planID(
    section_code: int, line_id: int, machine_no: str, working_date: str, db: Session
):
    yearMonth = working_date[:7].replace("-", "_")
    stmt = f"""
        SELECT db.section_code, db.line_id, db.machine_no, db.date, db.data, bd.plan_id, bd.period, db.working_date, db.shift
        FROM public.data_baratsuki_{yearMonth} db
        LEFT JOIN 
            public.break_detail bd 
        ON 
            db.break_id_1 = bd.break_id_1 
            AND db.break_id_2 = bd.break_id_2 
            AND db.break_id_3 = bd.break_id_3 
            AND db.break_id_4 = bd.break_id_4
        WHERE
            db.section_code = {section_code} 
            AND line_id = {line_id}
            AND db.machine_no = '{machine_no}'
            AND  db.working_date = '{working_date}'
        ORDER BY 
            db.date
        LIMIT 1
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        return [dict(row) for row in result]
    except Exception as e:
        raise HTTPException(400, "Error get databaratsuki :" + str(e))


def get_data_point_period(
    section_code: int,
    line_id: int,
    machine_no: str,
    working_date: str,
    periods: List[dict],
    plan_id: int,
    db: Session,
):
    yearMonth = working_date[:7].replace("-", "_")
    period_conditions = []

    for period in periods:
        # Check if 'duration' is in the period dictionary
        if "duration" not in period:
            raise HTTPException(400, f"Error: 'duration' not found in period: {period}")

        start_time, end_time = period["period"].split(" - ")
        start_hour, start_minute = map(int, start_time.split(":"))
        end_hour, end_minute = map(int, end_time.split(":"))

        # Condition for start time
        period_conditions.append(
            f"(EXTRACT(HOUR FROM date) = {start_hour} AND EXTRACT(MINUTE FROM date) = {start_minute})"
        )

        # Condition for end time (only if it's not the same as start time)
        if start_hour != end_hour or start_minute != end_minute:
            period_conditions.append(
                f"(EXTRACT(HOUR FROM date) = {end_hour} AND EXTRACT(MINUTE FROM date) = {end_minute})"
            )

    period_conditions_str = " OR ".join(period_conditions)
    stmt = f"""
        SELECT 
            d.id, 
            d.section_code, 
            d.line_id, 
            d.machine_no, 
            d.date, 
            d.working_date, 
            d.data, 
            d.shift, 
            d.ct_target,
            m.machine_name
        FROM 
            data_baratsuki_{yearMonth} d
        JOIN 
            public.machines m
        ON 
            d.machine_no = m.machine_no
        WHERE 
            d.working_date = '{working_date}'
            AND ({period_conditions_str})
            AND d.section_code = {section_code}
            AND d.line_id = {line_id}
            AND d.machine_no = '{machine_no}'
        ORDER BY 
            d.date;
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        enriched_result = []

        for row in result:
            row_dict = dict(row, plan_id=plan_id)
            row_dict["ct_target"] = float(row_dict["ct_target"])
            row_dict["exclusion_time"] = float(0)
            row_time = row_dict["date"].time()
            row_date = row_dict["date"].date()

            for period in periods:
                start_time, end_time = period["period"].split(" - ")
                start_time_obj = datetime.strptime(start_time, "%H:%M").time()
                end_time_obj = datetime.strptime(end_time, "%H:%M").time()

                if start_time_obj <= end_time_obj:  # Same day period
                    if start_time_obj <= row_time <= end_time_obj:
                        row_dict.update(period)
                        break
                else:  # Period spans midnight
                    if (start_time_obj <= row_time or row_time <= end_time_obj) and (
                        row_date == datetime.strptime(working_date, "%Y-%m-%d").date()
                        or row_time <= end_time_obj
                    ):
                        row_dict.update(period)
                        break

            # Ensure 'duration' is properly handled before further processing
            if "duration" not in row_dict:
                raise HTTPException(
                    400,
                    f"Error: 'duration' key missing in processed row_dict: {row_dict}",
                )

            row_dict["target100"] = math.floor(
                row_dict["duration"] / row_dict["ct_target"]
            )
            row_dict["challenge_target"] = 81
            enriched_result.append(row_dict)

        return enriched_result
    except Exception as e:
        raise HTTPException(400, f"Error get databaratsuki: {str(e)}")


def get_machinename(section_code: int, db: Session):
    stmt = f"""
        SELECT machine_no,machine_name FROM machines
        WHERE registered_section_code = {section_code}
        AND (machine_no LIKE '6%' OR machine_no LIKE 'T6%')
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(400, "Error get section :" + str(e))


def get_data_area(
    section_code: int,
    line_id: int,
    machine_no: str,
    interval: str,
    date: Optional[dt.datetime],
    period: str,
    ct_target: float,
    challenge_rate: float,
    accummulate_target: int,
    accummulate_upper: int,
    accummulate_lower: int,
    duration: int,
    exclusion_time: int,
    target_challege_lower: int,
    target_challege_target: int,
    target_challege_upper: int,
    db: Session,
):
    year_month = date.strftime("%Y_%m")
    table_name = f"data_baratsuki_{year_month}"
    stmt = f"""
        SELECT d.section_code, d.line_id, d.machine_no, d.date, d.data, m.machine_name
        FROM {table_name} d
        JOIN machines m ON d.machine_no = m.machine_no
        WHERE d.section_code = {section_code}
        AND d.line_id = {line_id}
        AND d.machine_no = '{machine_no}'
        AND d.date BETWEEN TIMESTAMP '{date}' - INTERVAL '{interval}' 
        AND TIMESTAMP '{date}'
        ORDER BY d.date
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        result_with_additional_fields = [
            dict(
                row,
                period=period,
                ct_target=ct_target,
                challenge_rate=challenge_rate,
                accummulate_target=accummulate_target,
                accummulate_upper=accummulate_upper,
                accummulate_lower=accummulate_lower,
                duration=duration,
                exclusion_time=exclusion_time,
                target_challege_lower=target_challege_lower,
                target_challege_target=target_challege_target,
                target_challege_upper=target_challege_upper,
            )
            for row in result
        ]
        return result_with_additional_fields
    except Exception as e:
        raise HTTPException(400, "Error get data area :" + str(e))


def get_dataparameter_day(
    section_code: int,
    line_id: int,
    machine_no1: str,
    machine_no2: str,
    date_current: str,
    next_date: str,
    isOdd: bool,
    db: Session,
    shift: str,
):
    minute_values_for_brake1_day = "30, 40" if isOdd else "20, 30"
    minute_values_for_brakemain_day = "15" if isOdd else "30"
    minute_values_for_brake2_day = "30, 40" if isOdd else "20, 30"

    minute_values_for_brakemain_night1 = "15" if isOdd else "30"
    minute_values_for_brakemain_night2 = "05" if isOdd else "20"
    year_month = date_current[:7].replace("-", "_")
    table_name = f"public.data_baratsuki_{year_month}"

    stmt = f"""
        	SELECT db.id, db.section_code, db.line_id, db.machine_no, db.date, db.data,m.machine_name
            FROM {table_name} db
            JOIN public.machines m ON db.machine_no = m.machine_no
            WHERE (
                db.date::date = '{date_current}'
                AND (
                (EXTRACT(HOUR FROM db.date) = 7 AND EXTRACT(MINUTE FROM db.date) = 35)
                OR (EXTRACT(HOUR FROM db.date) = 8 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 9 AND EXTRACT(MINUTE FROM db.date) IN ({minute_values_for_brake1_day}))
                OR (EXTRACT(HOUR FROM db.date) = 10 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 11 AND EXTRACT(MINUTE FROM db.date) = {minute_values_for_brakemain_day})
                OR (EXTRACT(HOUR FROM db.date) = 12 AND EXTRACT(MINUTE FROM db.date) = {minute_values_for_brakemain_day})
                OR (EXTRACT(HOUR FROM db.date) = 13 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 14 AND EXTRACT(MINUTE FROM db.date) IN ({minute_values_for_brake2_day}))
                OR (EXTRACT(HOUR FROM db.date) = 15 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 16 AND EXTRACT(MINUTE FROM db.date) IN (30, 50))
                OR (EXTRACT(HOUR FROM db.date) = 17 AND EXTRACT(MINUTE FROM db.date) = 50)
                OR (EXTRACT(HOUR FROM db.date) = 19 AND EXTRACT(MINUTE FROM db.date) = 20)
            )
                AND db.section_code = {section_code} AND db.line_id = {line_id} AND db.machine_no in ('{machine_no1}','{machine_no2}')
            )
            ORDER BY db.date asc
	
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        parsed_result = []
        for row in result:
            parsed_row = dict(row)  # Convert RowMapping to dictionary
            parsed_row["data"] = parsed_row[
                "data"
            ]  # Convert JSONB to Python dictionary
            parsed_result.append(parsed_row)

        return parsed_result
    except Exception as e:
        raise HTTPException(400, "Error get dataparameter :" + str(e))


def get_dataparameter_night(
    section_code: int,
    line_id: int,
    machine_no1: str,
    machine_no2: str,
    date_current: str,
    next_date: str,
    isOdd: bool,
    db: Session,
    shift: str,
):
    minute_values_for_brake1_day = "30, 40" if isOdd else "20, 30"
    minute_values_for_brakemain_day = "15" if isOdd else "30"
    minute_values_for_brake2_day = "30, 40" if isOdd else "20, 30"

    minute_values_for_brakemain_night1 = "15" if isOdd else "30"
    minute_values_for_brakemain_night2 = "05" if isOdd else "20"

    year_month = date_current[:7].replace("-", "_")
    table_name = f"public.data_baratsuki_{year_month}"
    stmt = f"""
        	SELECT db.id, db.section_code, db.line_id, db.machine_no, db.date, db.data,m.machine_name
            FROM {table_name} db
            JOIN public.machines m ON db.machine_no = m.machine_no
            WHERE (
                db.date::date = '{date_current}'
                AND (
                (EXTRACT(HOUR FROM db.date) = 19 AND EXTRACT(MINUTE FROM db.date) = 35)
                OR (EXTRACT(HOUR FROM db.date) = 20 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 21 AND EXTRACT(MINUTE FROM db.date) IN (30, 40))
                OR (EXTRACT(HOUR FROM db.date) = 22 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 23 AND EXTRACT(MINUTE FROM db.date) = {minute_values_for_brakemain_night1})
            )
            ) OR (
                db.date::date = '{next_date}'
                AND (
                (EXTRACT(HOUR FROM db.date) = 0 AND EXTRACT(MINUTE FROM db.date) = {minute_values_for_brakemain_night2})
                OR (EXTRACT(HOUR FROM db.date) = 1 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 2 AND EXTRACT(MINUTE FROM db.date) IN (30, 50))
                OR (EXTRACT(HOUR FROM db.date) = 3 AND EXTRACT(MINUTE FROM db.date) = 30)
                OR (EXTRACT(HOUR FROM db.date) = 4 AND EXTRACT(MINUTE FROM db.date) IN (30, 50))
                OR (EXTRACT(HOUR FROM db.date) = 5 AND EXTRACT(MINUTE FROM db.date) = 50)
                OR (EXTRACT(HOUR FROM db.date) = 7 AND EXTRACT(MINUTE FROM db.date) = 20)
            )
                AND db.section_code = {section_code} AND db.line_id = {line_id} AND db.machine_no in ('{machine_no1}','{machine_no2}')
            )
            ORDER BY db.date asc
	
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        parsed_result = []
        for row in result:
            parsed_row = dict(row)  # Convert RowMapping to dictionary
            parsed_row["data"] = parsed_row[
                "data"
            ]  # Convert JSONB to Python dictionary
            parsed_result.append(parsed_row)

        return parsed_result
    except Exception as e:
        raise HTTPException(400, "Error get dataparameter :" + str(e))


def get_dataparameter_by_shift_column(
    section_code: int,
    line_id: int,
    machine_no1: str,
    machine_no2: str,
    date_current: str,
    next_date: str,
    db: Session,
):
    year_month = date_current[:7].replace("-", "_")
    table_name = f"public.data_baratsuki_{year_month}"
    stmt = f"""
        	SELECT db.id, db.section_code, db.line_id, db.machine_no, db.date, db.data,m.machine_name
            FROM {table_name} db
            JOIN public.machines m ON db.machine_no = m.machine_no
            WHERE (
                db.date::date = '{date_current}'
                AND (
                (EXTRACT(HOUR FROM db.date) = 16 AND EXTRACT(MINUTE FROM db.date) = 50)
                 OR (EXTRACT(HOUR FROM db.date) = 19 AND EXTRACT(MINUTE FROM db.date) = 20)
            )
            ) OR (
                db.date::date = '{next_date}'
                AND (
                (EXTRACT(HOUR FROM db.date) = 4 AND EXTRACT(MINUTE FROM db.date) = 50)
                 OR (EXTRACT(HOUR FROM db.date) = 7 AND EXTRACT(MINUTE FROM db.date) = 20)
            )
                AND db.section_code = {section_code} AND db.line_id = {line_id} AND db.machine_no in ('{machine_no1}','{machine_no2}')
            )
            ORDER BY db.id ASC;
	
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        parsed_result = []
        for row in result:
            parsed_row = dict(row)  # Convert RowMapping to dictionary
            parsed_row["data"] = parsed_row[
                "data"
            ]  # Convert JSONB to Python dictionary
            parsed_result.append(parsed_row)

        return parsed_result
    except Exception as e:
        raise HTTPException(400, "Error get dataparameter :" + str(e))
