import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Clock, X, Check, Trash2 } from 'lucide-react';
import '../styles/CustomTimePickerModal.css';

const CustomTimePickerModal = ({ value, onChange, name }) => {
  const { translate } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedHour, setSelectedHour] = useState('14');
  const [selectedMinute, setSelectedMinute] = useState('00');
  
  // Parse value to hour and minute
  useEffect(() => {
    if (value) {
      const [hour, minute] = value.split(':');
      if (hour && minute) {
        setSelectedHour(hour);
        setSelectedMinute(minute);
      }
    }
  }, [value]);

  // Generate hours (10:00 - 22:00 for spa working hours)
  const hours = Array.from({ length: 13 }, (_, i) => {
    const hour = i + 10;
    return String(hour).padStart(2, '0');
  });

  // Generate minutes in 5-minute intervals (00, 05, 10, 15, ..., 55)
  const minutes = Array.from({ length: 12 }, (_, i) => {
    const minute = i * 5;
    return String(minute).padStart(2, '0');
  });

  const handlePostavi = () => {
    const timeValue = `${selectedHour}:${selectedMinute}`;
    onChange({ target: { name, value: timeValue } });
    setIsOpen(false);
  };

  const handleOtkazi = () => {
    // Reset to original value
    if (value) {
      const [hour, minute] = value.split(':');
      setSelectedHour(hour || '14');
      setSelectedMinute(minute || '00');
    }
    setIsOpen(false);
  };

  const handleObrisi = () => {
    setSelectedHour('14');
    setSelectedMinute('00');
    onChange({ target: { name, value: '' } });
    setIsOpen(false);
  };

  const handleTimeSelect = (type, value) => {
    if (type === 'hour') {
      setSelectedHour(value);
    } else {
      setSelectedMinute(value);
    }
  };

  const formatDisplayTime = (value) => {
    if (!value) return translate('selectTime') || 'Izaberite vreme';
    return value;
  };

  return (
    <div className="custom-time-wrapper">
      <div 
        className="time-input-trigger"
        onClick={() => {
          console.log('🕐 Time picker trigger clicked!');
          setIsOpen(true);
        }}
      >
        <Clock className="time-icon" size={20} />
        <span className={value ? 'has-value' : 'placeholder'}>
          {formatDisplayTime(value)}
        </span>
      </div>

      {isOpen && (
        <>
          <div className="time-modal-backdrop" onClick={handleOtkazi} />
          <div className="time-modal">
            <div className="time-modal-header">
              <Clock size={24} />
              <h3>{translate('selectTime') || 'Izaberite vreme'}</h3>
              <button onClick={handleOtkazi} className="time-close-btn">
                <X size={20} />
              </button>
            </div>

            <div className="time-picker-stepper-container">
              <div className="time-stepper-section">
                <div className="time-label">{translate('hours') || 'Sati'}</div>
                <button 
                  type="button"
                  className="time-stepper-btn time-stepper-up"
                  onClick={() => {
                    const currentIndex = hours.indexOf(selectedHour);
                    const nextIndex = (currentIndex + 1) % hours.length;
                    handleTimeSelect('hour', hours[nextIndex]);
                  }}
                >
                  ▲
                </button>
                <div className="time-stepper-display">
                  {selectedHour}
                </div>
                <button 
                  type="button"
                  className="time-stepper-btn time-stepper-down"
                  onClick={() => {
                    const currentIndex = hours.indexOf(selectedHour);
                    const prevIndex = (currentIndex - 1 + hours.length) % hours.length;
                    handleTimeSelect('hour', hours[prevIndex]);
                  }}
                >
                  ▼
                </button>
              </div>

              <div className="time-stepper-colon">:</div>

              <div className="time-stepper-section">
                <div className="time-label">{translate('minutes') || 'Minuti'}</div>
                <button 
                  type="button"
                  className="time-stepper-btn time-stepper-up"
                  onClick={() => {
                    const currentIndex = minutes.indexOf(selectedMinute);
                    const nextIndex = (currentIndex + 1) % minutes.length;
                    handleTimeSelect('minute', minutes[nextIndex]);
                  }}
                >
                  ▲
                </button>
                <div className="time-stepper-display">
                  {selectedMinute}
                </div>
                <button 
                  type="button"
                  className="time-stepper-btn time-stepper-down"
                  onClick={() => {
                    const currentIndex = minutes.indexOf(selectedMinute);
                    const prevIndex = (currentIndex - 1 + minutes.length) % minutes.length;
                    handleTimeSelect('minute', minutes[prevIndex]);
                  }}
                >
                  ▼
                </button>
              </div>
            </div>

            <div className="time-preview">
              <Clock size={20} />
              <span>{translate('selectedTime') || 'Izabrano vreme'}: {selectedHour}:{selectedMinute}</span>
            </div>

            <div className="time-modal-actions">
              <button
                className="time-btn time-btn-delete"
                onClick={handleObrisi}
                type="button"
              >
                <Trash2 size={16} />
                {translate('timeDelete') || 'Obriši'}
              </button>
              <button
                className="time-btn time-btn-cancel"
                onClick={handleOtkazi}
                type="button"
              >
                <X size={16} />
                {translate('timeCancel') || 'Otkaži'}
              </button>
              <button
                className="time-btn time-btn-confirm"
                onClick={handlePostavi}
                type="button"
              >
                <Check size={16} />
                {translate('timeConfirm') || 'Postavi'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CustomTimePickerModal;
