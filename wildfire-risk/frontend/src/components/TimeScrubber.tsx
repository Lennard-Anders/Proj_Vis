import React from "react";

interface Props {
  date: string;
  onChange: (value: string) => void;
}

const TimeScrubber: React.FC<Props> = ({ date, onChange }: Props) => (
  <div className="time-scrubber">
    <label htmlFor="scrubber">
      Date
      <input
        id="scrubber"
        type="date"
        value={date}
        onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
          onChange(event.target.value)
        }
      />
    </label>
  </div>
);

export default TimeScrubber;
