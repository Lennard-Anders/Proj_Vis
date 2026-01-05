import React from "react";
import { useRisk } from "../../state/selectors";

const QualityBoard: React.FC = () => {
  // Hidden per request
  useRisk();
  return null;
};

export default QualityBoard;
