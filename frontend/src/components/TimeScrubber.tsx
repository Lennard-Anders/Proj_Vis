/**
 * Time scrubber component
 */
import React, { useState } from 'react';

interface TimeScrubberProps {
  initialDate: string;
  onChange: (date: string) => void;
}

export const TimeScrubber: React.FC<TimeScrubberProps> = ({ initialDate, onChange }) => {
  const [date, setDate] = useState(initialDate);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    setDate(newDate);
    onChange(newDate);
  };
  
  return (
    <div style={{ padding: '0.5rem 0' }}>
      <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
        Date
      </label>
      <input
        type="date"
        value={date}
        onChange={handleChange}
        style={{
          width: '100%',
          padding: '0.5rem',
          borderRadius: '4px',
          border: '1px solid #555',
          backgroundColor: '#333',
          color: '#fff'
        }}
      />
    </div>
  );
};
