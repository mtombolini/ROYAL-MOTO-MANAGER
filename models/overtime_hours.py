from __future__ import annotations
from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Boolean, and_
from parameters import (
    STANDARD_CHECK_IN_WEEKDAY, STANDARD_CHECK_OUT_WEEKDAY,
    STANDARD_CHECK_IN_SATURDAY, STANDARD_CHECK_OUT_SATURDAY,
    STANDARD_LUNCH_BREAK_DURATION, STANDARD_LUNCH_BREAK_START,
    SCHEDULE_RECORDS_DATE_FORMAT, STANDARD_TOTAL_HOURS_WORKED_WEEKDAY,
    STANDARD_TOTAL_HOURS_WORKED_SATURDAY,
)
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession
from datetime import datetime, timedelta, time
from functools import reduce
from typing import List, Dict
import calendar
import inspect
           
def calculate_monthly_total_hours_worked(records_data):
    iterable = [record['total_hours_worked'] for record in records_data if record['total_hours_worked']]
    return reduce(lambda x, y: x+y, iterable, timedelta())

def calculate_monthly_overtime_hours(records_data):
    iterable = [record['overtime_hours'] for record in records_data if record['total_hours_worked']]
    return reduce(lambda x, y: x+y, iterable, timedelta()) 

class OvertimeRecordRecordNotFoundError(ValueError):
    """Exception raised when the overtime hours record of an employee 
    in a certain month is not found.""" 
    
class OvertimeRecordRecordColumnNotFoundError(AttributeError):
    """Exception raised when trying to access an inexistent record attribute.""" 
    
class OvertimeRecordKeyError(KeyError):
    """Exception raised when the necessary keys/identifiers for a new record
    are not provided."""  

class OvertimeRecord(Base):
    __tablename__ = 'overtime_records'

    date = Column(Date(), nullable=False, primary_key=True)
    employee = relationship('Employee', back_populates='overtime_hours')
    employee_id = Column(Integer, ForeignKey('empleados.id'), nullable=False, primary_key=True)
    _check_in = Column(Time())
    _check_out = Column(Time())
    _lunch_break_start = Column(Time())
    _lunch_break_end = Column(Time())
    _confirmed = Column(Boolean(), default=False)
    _is_holiday = Column(Boolean(), default=False)
    _is_on_vacation = Column(Boolean(), default=False)
    _absence = Column(Boolean(), default=False)
    
    @property
    def is_holiday(self) -> bool:
        return self._is_holiday
     
    
    @property
    def confirmed(self) -> bool:
        return self._confirmed
    
    
    @property
    def is_on_vacation(self) -> bool:
        return self._is_on_vacation
    
    
    @property
    def absence(self) -> bool:
        return self._absence
    
    
    @property
    def employee_name(self) -> str:
        if self.employee:
            return " ".join((self.employee.first_name, self.employee.last_name))
    
    
    @property
    def check_in(self) -> time:
        if self.is_sunday() or self.is_holiday or self.is_on_vacation or self.absence:
            return None
        elif self.is_saturday():
            return self._check_in or STANDARD_CHECK_IN_SATURDAY
        else:
            return self._check_in or STANDARD_CHECK_IN_WEEKDAY
    
    @check_in.setter
    def check_in(self, value: time) -> None:
        if isinstance(value, time):
            self._check_in = value
    
    
    @property
    def check_out(self) -> time:
        if self.is_sunday() or self.is_holiday or self.is_on_vacation or self.absence:
            return None
        elif self.is_saturday():
            return self._check_out or STANDARD_CHECK_OUT_SATURDAY
        else:
            return self._check_out or STANDARD_CHECK_OUT_WEEKDAY
    
    @check_out.setter
    def check_out(self, value: time) -> None:
        if isinstance(value, time):
            self._check_out = value
            
            
    @property
    def lunch_break_start(self) -> time:
        if self.is_saturday() or self.is_sunday() or self.is_holiday or self.is_on_vacation or self.absence:
            return None
        else:
            if self._lunch_break_start:
                return self._lunch_break_start
            elif self.employee:
                return self.employee.lunch_break
            else:
                return STANDARD_LUNCH_BREAK_START
        
    @lunch_break_start.setter
    def lunch_break_start(self, value: time) -> None:
        if isinstance(value, time):
            self._lunch_break_start = value
    
            
    
    @property
    def lunch_break_end(self) -> time | None:
        if self.is_saturday() or self.is_sunday() or self.is_holiday or self.is_on_vacation or self.absence:
            return None
        else:
            if self._lunch_break_end:
                return self._lunch_break_end
            elif self.lunch_break_start:
                full_datetime = datetime.combine(datetime.today(), self.lunch_break_start)
                end_datetime = full_datetime + STANDARD_LUNCH_BREAK_DURATION
                return end_datetime.time()
    
    @lunch_break_end.setter
    def lunch_break_end(self, value: time) -> None:
        if isinstance(value, time):
            self._lunch_break_end = value
    
    
    @property
    def total_hours_worked(self) -> timedelta | None:
        date_today = datetime.today().date()
        if self.is_sunday() or self.is_holiday or self.is_on_vacation or self.absence:
            return timedelta(hours=0)
        elif self.is_saturday():
            datetime_check_in = datetime.combine(date_today, self.check_in)
            datetime_check_out = datetime.combine(date_today, self.check_out)
            return datetime_check_out - datetime_check_in
        else:
            datetime_check_in = datetime.combine(date_today, self.check_in)
            datetime_check_out = datetime.combine(date_today, self.check_out)            
            gross_time_difference = datetime_check_out - datetime_check_in
            datetime_lunch_break_start = datetime.combine(date_today, self.lunch_break_start)
            datetime_lunch_break_end = datetime.combine(date_today, self.lunch_break_end)
            lunch_duration = datetime_lunch_break_end - datetime_lunch_break_start
            return gross_time_difference - lunch_duration
    
    
    @property
    def overtime_hours(self) -> timedelta | None:
        if self.is_sunday() or self.is_holiday or self.is_on_vacation or self.absence:
            return None
        elif self.is_saturday():
            return self.total_hours_worked - STANDARD_TOTAL_HOURS_WORKED_SATURDAY
        else:
            return self.total_hours_worked - STANDARD_TOTAL_HOURS_WORKED_WEEKDAY
    
    
    def is_saturday(self) -> bool:
        return self.date.weekday() == 5
    
    
    def is_sunday(self) -> bool:
        return self.date.weekday() == 6
    
    
    def get_column_values(self) -> Dict:
        columns = {}
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, property):
                columns[name] = value.fget(self)
            elif not name.startswith('_') and not inspect.ismethod(value) or name in ["_is_holiday", "_confirmed", "_is_on_vacation", "_absence"]:
                columns[name] = value
        return columns
    
    
    @classmethod
    def generate_standard_record_data(cls, employee_id: int, date: datetime, session: AppSession) -> Dict:
        from models.employee import Employee
        employee = session.query(Employee).filter(Employee.id == employee_id).one_or_none()
        standard_record = cls(employee_id=employee_id, date=date, employee=employee)
        standard_record_data = standard_record.get_column_values()
        return standard_record_data
    
           
    @classmethod
    def get_employee_month_schedule_record(cls, employee_id: int, month: str) -> List[Dict]:
        with AppSession() as session:
            month_start: datetime = datetime.strptime(month, SCHEDULE_RECORDS_DATE_FORMAT)
            previous_month_start = (month_start - timedelta(days=1)).replace(day=26)
            current_month_start = month_start  # First day of the current month
            current_month_end = current_month_start.replace(day=25)
            _, days_in_month = calendar.monthrange(month=previous_month_start.month, year=month_start.year)
            try:
                employee_month_record: List[cls] = session.query(cls).filter(
                    and_(
                        current_month_end > cls.date,
                        cls.date >= previous_month_start
                    ),
                    cls.employee_id == employee_id
                ).order_by(cls.date).all()
                employee_month_record_data = [
                    (
                        employee_month_record.pop(0).get_column_values() 
                        if employee_month_record and employee_month_record[0].date == (previous_month_start + timedelta(days=i)).date()
                        else cls.generate_standard_record_data(
                            employee_id=employee_id, date=(previous_month_start + timedelta(days=i)).date(),
                            session=session
                        )
                    )
                    for i in range(1, days_in_month + 1)
                ]
                monthly_total_hours_worked = calculate_monthly_total_hours_worked(
                    employee_month_record_data
                )
                monthly_overtime_hours = calculate_monthly_overtime_hours(
                    employee_month_record_data
                )
                monthly_standard_total_hours_worked = monthly_total_hours_worked - monthly_overtime_hours
                return employee_month_record_data, {
                    'monthly_total_hours_worked': monthly_total_hours_worked,
                    'monthly_overtime_hours': monthly_overtime_hours,
                    'monthly_standard_total_hours_worked': monthly_standard_total_hours_worked,
                }
            except Exception as ex:
                session.rollback()
                raise
               
            
    @classmethod
    def create(cls, session: AppSession, **kwargs) -> None:
        try:
            new_record = cls()
            required_keys = ['employee_id', 'date']
            if not all(key in kwargs for key in required_keys):
                missing_keys = ', '.join(key for key in required_keys if key not in kwargs)
                raise KeyError(f'Missing required key(s): {missing_keys}')
            for key, value in kwargs.items():
                if key in dir(new_record):
                    setattr(new_record, key, value)
                else:
                    raise OvertimeRecordRecordColumnNotFoundError(
                        f'Column {key} not found in overtime hours record'
                    )
            session.add(new_record)
            session.commit()
        except Exception as ex:
            session.rollback()
            raise
            
            
    @classmethod
    def edit(cls, employee_id: int, date: str, **kwargs) -> None:
        with AppSession() as session:
            try:
                record_to_edit = session.query(cls).filter(cls.employee_id == employee_id,
                                                           cls.date == date).one_or_none()
                if not record_to_edit:
                    cls.create(session, employee_id=employee_id, date=date, **kwargs)
                else:
                    columns = record_to_edit.get_column_values().keys()
                    for key, value in kwargs.items():
                        if key in columns:
                            setattr(record_to_edit, key, value)
                        else:
                            raise OvertimeRecordRecordColumnNotFoundError(
                                f'Attribute {key} not found in overtime hours record'
                            )
                session.commit()
            except Exception as ex:
                session.rollback()
                raise
            
            
    @classmethod
    def delete(cls, employee_id: int, month: str) -> None:
        with AppSession() as session:
            try:
                record_to_delete = session.query(cls).filter(cls.id == employee_id,
                                                             cls.month == month).one_or_none()
                if record_to_delete:
                    session.delete(record_to_delete)
                    session.commit()
                else:
                    raise OvertimeRecordRecordNotFoundError(
                        f'Overtime record of employee with ID {employee_id} on {month} not found.'
                    )
            except Exception as ex:
                session.rollback()
                raise 
            
    
    @classmethod       
    def toggle_confirmed_status(cls, employee_id: int, date: str) -> None:
        with AppSession() as session: 
            record = session.query(cls).filter(cls.employee_id == employee_id,
                                               cls.date == date).one_or_none()
        if record:
            cls.edit(employee_id, date, **{'_confirmed': not record.is_holiday})
        else:
            cls.edit(employee_id, date, **{'_confirmed': True})
            
    
    @classmethod       
    def toggle_is_holiday_status(cls, employee_id: int, date: str) -> None:
        with AppSession() as session: 
            record = session.query(cls).filter(cls.employee_id == employee_id,
                                               cls.date == date).one_or_none()
        if record:
            cls.edit(employee_id, date, **{'_is_holiday': not record.is_holiday})
        else:
            cls.edit(employee_id, date, **{'_is_holiday': True})    


    @classmethod       
    def toggle_is_on_vacation_status(cls, employee_id: int, date: str) -> None:
        with AppSession() as session: 
            record = session.query(cls).filter(cls.employee_id == employee_id,
                                               cls.date == date).one_or_none()
        if record:
            cls.edit(employee_id, date, **{'_is_on_vacation': not record.is_on_vacation})
        else:
            cls.edit(employee_id, date, **{'_is_on_vacation': True}) 
            
            
    @classmethod
    def toggle_absence_status(cls, employee_id: int, date: str) -> None:
        with AppSession() as session: 
            record = session.query(cls).filter(cls.employee_id == employee_id,
                                               cls.date == date).one_or_none()
        if record:
            cls.edit(employee_id, date, **{'_absence': not record.absence})
        else:
            cls.edit(employee_id, date, **{'_absence': True})    
