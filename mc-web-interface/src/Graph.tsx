import React, { useState, useEffect } from 'react';
import Chart from 'chart.js/auto';

interface RawDataPoint {
  timestamp: string;
  value: number;
}

interface AggregatedDataPoint {
  timestamp: string; // Representing the start of the time range
  value: number; // Aggregated value (e.g., average)
}

interface GraphProps {
  rawData: RawDataPoint[];
}

const Graph: React.FC<GraphProps> = ({ rawData }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<number>(60); // 1 hour by default
  const [aggregatedData, setAggregatedData] = useState<AggregatedDataPoint[]>([]);

  useEffect(() => {
    aggregateData();
  }, [selectedTimeRange, rawData]);

  const aggregateData = () => {
    // Aggregate rawData based on selectedTimeRange
    const response = await fetch(endpoint);
    const responseData = await response.json();
    const aggregatedData: AggregatedDataPoint[] = aggregateData(responseData, selectedTimeRange);
    setAggregatedData(aggregatedData);
  };

  const renderChart = () => {
    const ctx = document.getElementById('graphCanvas') as HTMLCanvasElement;
    if (!ctx) return;

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: aggregatedData.map(data => data.timestamp),
        datasets: [
          {
            label: 'Aggregated Value',
            data: aggregatedData.map(data => data.value),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
          },
        ],
      },
    });
  };

  useEffect(() => {
    if (aggregatedData.length > 0) {
      renderChart();
    }
  }, [aggregatedData]);

  return (
    <div>
      {/* Add UI to toggle between different time ranges */}
      <button onClick={() => setSelectedTimeRange(60)}>1 Hour</button>
      <button onClick={() => setSelectedTimeRange(1440)}>1 Day</button>
      <button onClick={() => setSelectedTimeRange(10080)}>1 Week</button>

      {/* Render the graph */}
      <canvas id="graphCanvas" />
    </div>
  );
};

export default Graph;
