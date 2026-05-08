import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Calendar, X, Check, Trash2 } from 'lucide-react';
import '../styles/CustomCalendarModal.css';

const CustomCalendarModal = ({ value, onChange, name, minDate }) => {
  const { translate } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Debug log for isOpen state
  useEffect(() => {
    console.log('📅 Calendar modal isOpen:', isOpen);
  }, [isOpen]);
  
  // Parse value to Date object
  useEffect(() => {
    if (value && value instanceof Date) {
      setSelectedDate(value);
      setCurrentMonth(value);
    } else if (value) {
      const parsed = new Date(value);
      if (!isNaN(parsed.getTime())) {
        setSelectedDate(parsed);
        setCurrentMonth(parsed);
      }
    }
  }, [value]);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Get days in month
  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add all days in month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    
    return days;
  };

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const handleDateClick = (date) => {
    console.log('📅 handleDateClick called with:', date);
    if (!date) {
      console.log('📅 handleDateClick: date is null, returning');
      return;
    }
    
    const dateToCheck = new Date(date);
    dateToCheck.setHours(0, 0, 0, 0);
    console.log('📅 handleDateClick: checking date:', dateToCheck, 'vs today:', today);
    
    // Check if date is in the past
    if (dateToCheck < today) {
      console.log('📅 handleDateClick: date is in past, returning');
      return;
    }
    
    console.log('📅 handleDateClick: setting selectedDate to:', date);
    setSelectedDate(date);
  };

  const handlePostavi = () => {
    console.log('📅 handlePostavi clicked! selectedDate:', selectedDate);
    if (selectedDate) {
      console.log('📅 Calendar Postavi - calling onChange with:', selectedDate);
      onChange(selectedDate);
      console.log('📅 Calendar Postavi - calling setIsOpen(false)');
      setIsOpen(false);
      console.log('📅 Calendar modal closed');
    } else {
      console.log('📅 handlePostavi: no selectedDate, not closing modal');
    }
  };

  const handleOtkazi = () => {
    // Reset to original value
    if (value && value instanceof Date) {
      setSelectedDate(value);
      setCurrentMonth(value);
    } else if (value) {
      const parsed = new Date(value);
      if (!isNaN(parsed.getTime())) {
        setSelectedDate(parsed);
        setCurrentMonth(parsed);
      }
    } else {
      setSelectedDate(null);
      setCurrentMonth(new Date());
    }
    setIsOpen(false);
  };

  const handleObrisi = () => {
    setSelectedDate(null);
    onChange(null);  // Send null directly, not as event
    setIsOpen(false);
  };

  const formatDisplayDate = (date) => {
    if (!date) return translate('selectDate') || 'Izaberite datum';
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  };

  const isDateSelected = (date) => {
    if (!date || !selectedDate) return false;
    return (
      date.getDate() === selectedDate.getDate() &&
      date.getMonth() === selectedDate.getMonth() &&
      date.getFullYear() === selectedDate.getFullYear()
    );
  };

  const isDateDisabled = (date) => {
    if (!date) return true;
    const dateToCheck = new Date(date);
    dateToCheck.setHours(0, 0, 0, 0);
    return dateToCheck < today;
  };

  const monthNames = [
    translate('monthJan'), translate('monthFeb'), translate('monthMar'), 
    translate('monthApr'), translate('monthMay'), translate('monthJun'),
    translate('monthJul'), translate('monthAug'), translate('monthSep'), 
    translate('monthOct'), translate('monthNov'), translate('monthDec')
  ];

  const dayNames = [
    translate('daySun'), translate('dayMon'), translate('dayTue'), 
    translate('dayWed'), translate('dayThu'), translate('dayFri'), 
    translate('daySat')
  ];

  const days = getDaysInMonth(currentMonth);

  return (
    <div className="custom-calendar-wrapper">
      <div 
        className="calendar-input-trigger"
        onClick={() => {
          console.log('📅 Calendar trigger clicked!');
          setIsOpen(true);
        }}
      >
        <Calendar className="calendar-icon" size={20} />
        <span className={selectedDate ? 'has-value' : 'placeholder'}>
          {formatDisplayDate(selectedDate)}
        </span>
      </div>

      {isOpen && (
        <>
          <div className="calendar-modal-backdrop" onClick={handleOtkazi} />
          <div className="calendar-modal">
            <div className="calendar-modal-header">
              <h3>{translate('selectDate') || 'Izaberite datum'}</h3>
              <button 
                className="calendar-close-btn"
                onClick={handleOtkazi}
                type="button"
              >
                <X size={20} />
              </button>
            </div>

            <div className="calendar-navigation">
              <button 
                className="calendar-nav-btn"
                onClick={handlePrevMonth}
                type="button"
              >
                ‹
              </button>
              <div className="calendar-month-year">
                {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
              </div>
              <button 
                className="calendar-nav-btn"
                onClick={handleNextMonth}
                type="button"
              >
                ›
              </button>
            </div>

            <div className="calendar-grid">
              {dayNames.map((day, index) => (
                <div key={index} className="calendar-day-name">
                  {day}
                </div>
              ))}
              
              {days.map((date, index) => (
                <div
                  key={index}
                  className={`calendar-day ${
                    !date ? 'empty' : ''
                  } ${
                    isDateDisabled(date) ? 'disabled' : ''
                  } ${
                    isDateSelected(date) ? 'selected' : ''
                  }`}
                  onClick={() => handleDateClick(date)}
                >
                  {date ? date.getDate() : ''}
                </div>
              ))}
            </div>

            <div className="calendar-modal-actions">
              <button
                className="calendar-btn calendar-btn-delete"
                onClick={handleObrisi}
                type="button"
              >
                <Trash2 size={16} />
                {translate('calendarDelete')}
              </button>
              <button
                className="calendar-btn calendar-btn-cancel"
                onClick={handleOtkazi}
                type="button"
              >
                <X size={16} />
                {translate('calendarCancel')}
              </button>
              <button
                className="calendar-btn calendar-btn-confirm"
                onClick={handlePostavi}
                disabled={!selectedDate}
                type="button"
              >
                <Check size={16} />
                {translate('calendarConfirm')}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CustomCalendarModal;
