import React from 'react';
import DatePicker from 'react-datepicker';
import { registerLocale } from 'react-datepicker';
import { sr, enUS, ru } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import { useLanguage } from '../context/LanguageContext';

// Register locales
registerLocale('sr', sr);
registerLocale('en', enUS);
registerLocale('ru', ru);

const DateTimePicker = ({ type, value, onChange, name, id, className, isMobile = false }) => {
  const { language, translate } = useLanguage();
  
  // Map language to date-fns locale
  const getLocale = () => {
    const localeMap = {
      'sr': 'sr',
      'en': 'en',
      'ru': 'ru',
      'th': 'en' // Fallback to English for Thai
    };
    return localeMap[language] || 'sr';
  };

  // Get translated button texts
  const getTodayText = () => {
    const todayMap = {
      'sr': 'Данас',
      'en': 'Today',
      'ru': 'Сегодня',
      'th': 'วันนี้'
    };
    return todayMap[language] || 'Данас';
  };

  const handleChange = (date) => {
    if (type === 'date') {
      // Format as YYYY-MM-DD
      const formatted = date ? date.toISOString().split('T')[0] : '';
      onChange({ target: { name, value: formatted } });
    } else {
      // Format as HH:MM
      const formatted = date ? 
        `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}` : '';
      onChange({ target: { name, value: formatted } });
    }
  };

  const parseValue = () => {
    if (!value) return null;
    
    if (type === 'date') {
      return new Date(value + 'T00:00:00');
    } else {
      const [hours, minutes] = value.split(':');
      const date = new Date();
      date.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      return date;
    }
  };

  // If mobile, use custom picker with DD.MM.YYYY format
  if (isMobile) {
    return (
      <DatePicker
        id={id}
        selected={parseValue()}
        onChange={handleChange}
        locale={getLocale()}
        dateFormat={type === 'date' ? 'dd.MM.yyyy' : 'HH:mm'}
        showTimeSelect={type === 'time'}
        showTimeSelectOnly={type === 'time'}
        timeIntervals={15}
        timeCaption={translate("preferredTime")}
        placeholderText={type === 'date' ? translate("selectDate") : translate("selectTime")}
        className={className}
        todayButton={getTodayText()}
        withPortal
        showMonthDropdown
        showYearDropdown
        dropdownMode="select"
      />
    );
  }

  // For desktop, use custom picker with DD/MM/YYYY format (inline)
  return (
    <DatePicker
      id={id}
      selected={parseValue()}
      onChange={handleChange}
      locale={getLocale()}
      dateFormat={type === 'date' ? 'dd/MM/yyyy' : 'HH:mm'}
      showTimeSelect={type === 'time'}
      showTimeSelectOnly={type === 'time'}
      timeIntervals={15}
      timeCaption={translate("preferredTime")}
      placeholderText={type === 'date' ? translate("selectDate") : translate("selectTime")}
      className={className}
      todayButton={getTodayText()}
      showMonthDropdown
      showYearDropdown
      dropdownMode="select"
    />
  );
};

export default DateTimePicker;
