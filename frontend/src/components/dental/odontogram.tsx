"use client";

import { useState } from "react";
import { cn, getToothName } from "@/lib/utils";
import { ToothCondition } from "@/types";

interface ToothData {
  tooth_number: number;
  condition: ToothCondition;
  surface?: string;
  notes?: string;
}

interface OdontogramProps {
  teeth: ToothData[];
  onToothClick?: (toothNumber: number) => void;
  readOnly?: boolean;
}

const conditionColors: Record<ToothCondition, string> = {
  healthy: "tooth-healthy",
  cavity: "tooth-cavity",
  filled: "tooth-filled",
  crown: "tooth-crown",
  root_canal: "tooth-root-canal",
  extraction: "tooth-extraction",
  missing: "tooth-missing",
  implant: "tooth-implant",
  bridge: "tooth-bridge",
};

// Simplified tooth path for SVG
const ToothPath = ({ 
  x, 
  y, 
  toothNumber, 
  condition,
  onClick,
  isSelected 
}: { 
  x: number; 
  y: number; 
  toothNumber: number;
  condition: ToothCondition;
  onClick?: () => void;
  isSelected: boolean;
}) => {
  const isMolar = [1, 2, 3, 14, 15, 16, 17, 18, 19, 30, 31, 32].includes(toothNumber);
  const width = isMolar ? 40 : 30;
  const height = 50;

  return (
    <g 
      className={cn("tooth", conditionColors[condition], isSelected && "ring-2 ring-primary")}
      onClick={onClick}
      style={{ cursor: onClick ? "pointer" : "default" }}
    >
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={5}
        ry={5}
        className={conditionColors[condition]}
        strokeWidth={2}
      />
      <text
        x={x + width / 2}
        y={y + height / 2 + 5}
        textAnchor="middle"
        className="text-xs font-medium fill-current"
        style={{ fontSize: "10px" }}
      >
        {toothNumber}
      </text>
    </g>
  );
};

export function DentalOdontogram({ teeth, onToothClick, readOnly = false }: OdontogramProps) {
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);

  const getToothCondition = (toothNumber: number): ToothCondition => {
    const tooth = teeth.find((t) => t.tooth_number === toothNumber);
    return tooth?.condition || "healthy";
  };

  const handleToothClick = (toothNumber: number) => {
    if (readOnly) return;
    setSelectedTooth(toothNumber);
    onToothClick?.(toothNumber);
  };

  // Upper teeth: 1-16 (right to left from patient's perspective)
  const upperRightTeeth = [1, 2, 3, 4, 5, 6, 7, 8];
  const upperLeftTeeth = [9, 10, 11, 12, 13, 14, 15, 16];
  
  // Lower teeth: 32-17 (right to left from patient's perspective)
  const lowerRightTeeth = [32, 31, 30, 29, 28, 27, 26, 25];
  const lowerLeftTeeth = [24, 23, 22, 21, 20, 19, 18, 17];

  const renderToothRow = (teeth: number[], startX: number, y: number) => {
    let currentX = startX;
    return teeth.map((toothNum) => {
      const isMolar = [1, 2, 3, 14, 15, 16, 17, 18, 19, 30, 31, 32].includes(toothNum);
      const width = isMolar ? 40 : 30;
      const tooth = (
        <ToothPath
          key={toothNum}
          x={currentX}
          y={y}
          toothNumber={toothNum}
          condition={getToothCondition(toothNum)}
          onClick={() => handleToothClick(toothNum)}
          isSelected={selectedTooth === toothNum}
        />
      );
      currentX += width + 4;
      return tooth;
    });
  };

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-healthy border" />
          <span>Healthy</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-cavity" />
          <span>Cavity</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-filled" />
          <span>Filled</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-crown" />
          <span>Crown</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-root-canal" />
          <span>Root Canal</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-missing border-dashed" />
          <span>Missing</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-implant" />
          <span>Implant</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded tooth-bridge" />
          <span>Bridge</span>
        </div>
      </div>

      {/* Odontogram Chart */}
      <div className="overflow-x-auto">
        <svg
          viewBox="0 0 800 300"
          className="w-full max-w-4xl mx-auto"
          style={{ minWidth: "600px" }}
        >
          {/* Labels */}
          <text x="200" y="20" className="text-sm font-medium fill-current">
            Upper Right
          </text>
          <text x="500" y="20" className="text-sm font-medium fill-current">
            Upper Left
          </text>
          <text x="200" y="180" className="text-sm font-medium fill-current">
            Lower Right
          </text>
          <text x="500" y="180" className="text-sm font-medium fill-current">
            Lower Left
          </text>

          {/* Midline */}
          <line
            x1="400"
            y1="25"
            x2="400"
            y2="275"
            stroke="#e5e7eb"
            strokeWidth="2"
            strokeDasharray="5,5"
          />

          {/* Upper teeth */}
          <g transform="translate(0, 30)">
            {/* Upper Right (teeth 1-8) - rendered right to left */}
            {renderToothRow(upperRightTeeth.reverse(), 50, 0)}
            {/* Upper Left (teeth 9-16) */}
            {renderToothRow(upperLeftTeeth, 410, 0)}
          </g>

          {/* Lower teeth */}
          <g transform="translate(0, 190)">
            {/* Lower Right (teeth 32-25) */}
            {renderToothRow(lowerRightTeeth, 50, 0)}
            {/* Lower Left (teeth 24-17) */}
            {renderToothRow(lowerLeftTeeth, 410, 0)}
          </g>
        </svg>
      </div>

      {/* Selected Tooth Info */}
      {selectedTooth && (
        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-medium">Tooth #{selectedTooth}</h4>
          <p className="text-sm text-muted-foreground">{getToothName(selectedTooth)}</p>
          <p className="text-sm">
            <span className="font-medium">Condition:</span>{" "}
            <span className="capitalize">{getToothCondition(selectedTooth).replace("_", " ")}</span>
          </p>
        </div>
      )}
    </div>
  );
}
